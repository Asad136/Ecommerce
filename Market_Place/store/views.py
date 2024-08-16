from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Store,Product
from .forms import StoreForm,ProductForm

@login_required
def create_store(request):
    if request.user.role == 'seller' and request.user.is_verified:
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
    if request.user == store.user_id:
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
    if request.user == product.store.user_id:
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
    if request.user == product.store.user_id:
        product.delete()
        return redirect('product_list', store_id=store_id)
    else:
        return redirect('home')
