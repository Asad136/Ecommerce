from django.db import models
from django.conf import settings

class Store(models.Model):
    user_id = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='store', on_delete=models.CASCADE)
    store_pic = models.ImageField(upload_to='store_pics')
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
    

class Product(models.Model):
    store = models.ForeignKey(Store, related_name='products', on_delete=models.CASCADE)
    product_pic = models.ImageField(upload_to='product_pics')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name