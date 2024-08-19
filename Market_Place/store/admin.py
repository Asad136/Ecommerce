from django.contrib import admin
from .models import Product,Store,OrderItem,Order

admin.site.register(Product)
admin.site.register(Store)
admin.site.register(OrderItem)
admin.site.register(Order)
