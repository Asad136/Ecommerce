import stripe
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Store,Product,Order,OrderItem
from django.conf import settings
from .forms import StoreForm,ProductForm
from django.http import JsonResponse
from django.db.models import Sum, F
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages




User = get_user_model()

def verify_sellers(request):
    if request.method == 'POST':
        seller_id = request.POST.get('seller_id')
        seller = User.objects.get(id=seller_id)
        seller.is_verified = True
        seller.save()
        send_mail(
            'Seller Verification',
            'Congratulations, your account has been verified!',
            'from@example.com',
            [seller.email],
            fail_silently=False,
        )

        messages.success(request, f'Seller {seller.username} has been verified.')

    unverified_sellers = User.objects.filter(role='seller', is_verified=False)
    return render(request, 'admin/verify_sellers.html', {'unverified_sellers': unverified_sellers})
@login_required
def create_store(request):
    if request.user.role == 'seller' and request.user.is_verified or request.user.role == 'admin':
        if request.method == 'POST':
            form = StoreForm(request.POST, request.FILES)
            if form.is_valid():
                store = form.save(commit=False)
                store.user_id = request.user 
                store.save()
                return redirect('store_detail', pk=store.pk)
        else:
            form = StoreForm()
        return render(request, 'store/create_store.html', {'form': form})
    else:
        return redirect('home')

@login_required
def store_list(request):
    stores = Store.objects.all()
    return render(request, 'store/store_list.html', {'stores': stores})

@login_required
def store_detail(request, pk):
    store = get_object_or_404(Store, pk=pk)
    return render(request, 'store/store_detail.html', {'store': store})


@login_required
def update_store(request, pk):
    store = Store.objects.get(pk=pk)
    if request.user == store.user_id:
        if request.method == 'POST':
            form = StoreForm(request.POST, request.FILES, instance=store)
            if form.is_valid():
                form.save()
                return redirect('store_list')
        else:
            form = StoreForm(instance=store)
        return render(request, 'store/update_store.html', {'form': form})
    else:
        return redirect('home')

@login_required
def delete_store(request, pk):
    store = Store.objects.get(pk=pk)
    if request.user == store.user_id:
        store.delete()
        return redirect('store_list')
    else:
        return redirect('home')

@login_required
def create_product(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    if request.user == store.user_id or request.user.role == 'admin':
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save(commit=False)
                product.store = store
                product.save()
                return redirect('product_list', store_id=store_id)
        else:
            form = ProductForm()
        return render(request, 'product/create_product.html', {'form': form, 'store': store})
    else:
        return redirect('home')

@login_required
def product_list(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    if request.user == store.user_id:
        products = store.products.all()
        return render(request, 'product/product_list.html', {'products': products, 'store': store})
    else:
        if request.user.role == 'admin':
            return redirect('admin_landing')
        return redirect('home')
    
@login_required
def product_detail(request, store_id, pk):
    product = get_object_or_404(Product, pk=pk, store_id=store_id)
    if request.user.role == 'buyer':
        return render(request, 'product/product_detail_for_buyer.html', {'product': product})
    return render(request, 'product/product_detail.html', {'product': product})

@login_required
def update_product(request, store_id, pk):
    product = get_object_or_404(Product, pk=pk, store_id=store_id)
    if request.user == product.store.user_id or request.user.role == 'admin':
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect('product_list', store_id=store_id)
        else:
            form = ProductForm(instance=product)
        return render(request, 'product/update_product.html', {'form': form, 'store': product.store})
    else:
        return redirect('home')

@login_required
def delete_product(request, store_id, pk):
    product = get_object_or_404(Product, pk=pk, store_id=store_id)
    if request.user == product.store.user_id or request.user.role == 'admin':
        product.delete()
        return redirect('product_list', store_id=store_id)
    else:
        return redirect('home')

from django.http import JsonResponse

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'product_pic': product.product_pic.url
        }

    request.session['cart'] = cart
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    return render(request, 'cart/cart.html', {'cart': cart})

def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        quantity = int(request.POST.get('quantity'))
        if quantity > 0:
            cart[str(product_id)]['quantity'] = quantity
        else:
            del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('view_cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
    request.session['cart'] = cart
    return redirect('view_cart')

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_checkout_session(request):
    cart = request.session.get('cart', {})
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    for item_id, item in cart.items():
        product = get_object_or_404(Product, id=item_id)
        if product.stock < item['quantity']:
            return JsonResponse({'error': 'Some products are out of stock.'}, status=400)

    if total > 0:
        order = Order.objects.create(
            user=request.user,
            order_id=f"order_{request.user.id}_{Order.objects.count() + 1}",
            total_amount=total,
            status='Pending',
        )
        request.session['order_id'] = order.id

        for item_id, item in cart.items():
            product = get_object_or_404(Product, id=item_id)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=item['price']
            )

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Order Total',
                        },
                        'unit_amount': int(total * 100),
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('order_success')),
            cancel_url=request.build_absolute_uri(reverse('view_cart')),
        )

        return JsonResponse({'id': session.id})
    else:
        return redirect('cart')

@login_required
@csrf_exempt
def order_success(request):
    order_id = request.session.get('order_id') 
    if not order_id:
        return redirect('cart')
    order = get_object_or_404(Order, id=order_id)
    order.status = 'Completed'
    order.save()
    for item in order.items.all():
        product = item.product
        if product.stock >=  item.quantity:
            product.stock =product.stock - item.quantity
            product.save()
    del request.session['cart']
    del request.session['order_id']

    return render(request, 'cart/order_success.html', {'order': order})

@login_required
def seller_orders(request):
    if request.user.role != 'seller':
        return redirect('home')
    
    store = request.user.store
    orders = Order.objects.filter(items__product__store=store).distinct()

    orders_with_filtered_items = []
    for order in orders:
        filtered_items = order.items.filter(product__store=store)
        if filtered_items.exists():
            order.filtered_items = filtered_items 
            orders_with_filtered_items.append(order)

    return render(request, 'store/seller_orders.html', {'orders': orders_with_filtered_items})

@login_required
def order_history(request):
    if request.user.role != 'buyer':
        return redirect('home')

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'order/order_history.html', {'orders': orders})
@login_required
def order_detail(request, order_id):
    if request.user.role != 'buyer':
        return redirect('home')

    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()

    return render(request, 'order/order_detail.html', {'order': order, 'order_items': order_items})

@login_required
def product_analytics(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    if request.user == store.user_id or request.user.role == 'admin':
        products = Product.objects.filter(store=store)
        
        today = timezone.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(7)]
        labels = [day.strftime('%Y-%m-%d') for day in last_7_days]
        
        total_sales_data = [0] * 7
        total_quantity_data = [0] * 7
        
        for product in products:
            for i, day in enumerate(last_7_days):
                start_date = day
                end_date = start_date + timedelta(days=1)
                total_sales = OrderItem.objects.filter(
                    product=product,
                    order__created_at__range=(start_date, end_date)
                ).aggregate(total_sales=Sum(F('quantity') * F('price')))['total_sales']
                total_quantity = OrderItem.objects.filter(
                    product=product,
                    order__created_at__range=(start_date, end_date)
                ).aggregate(total_quantity=Sum('quantity'))['total_quantity']
                
                total_sales_data[i] += float(total_sales) if total_sales is not None else 0
                total_quantity_data[i] += int(total_quantity) if total_quantity is not None else 0
        
        context = {
            'store': store,
            'labels': labels,
            'total_sales_data': total_sales_data,
            'total_quantity_data': total_quantity_data,
        }
        
        return render(request, 'store/product_analytics.html', context)
    else:
        return redirect('home')
@login_required
def seller_product_stock(request):
    if request.user.role == 'seller':
        store = request.user.store
        products = Product.objects.filter(store=store)
        return render(request, 'store/seller_product_stock.html', {'products': products})
    else:
        return redirect('home')
