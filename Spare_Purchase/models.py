from django.db import models

from Owner.models import ShopDB

# Create your models here.
class StockDB(models.Model):
    Status_CHOICES = [
        ('In Stock', 'In Stock'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
      
    ]
    id = models.AutoField(primary_key=True)
    ItemCode=models.CharField(max_length=100,blank=True, null=True)
    ItemName = models.CharField(max_length=100,blank=True, null=True)
    Category = models.CharField(max_length=100,blank=True, null=True)
    Supplier= models.CharField(max_length=100,blank=True, null=True)
    Quantity=models.IntegerField( blank=True, null=True)
    Unit= models.CharField(max_length=100,blank=True, null=True)
    Price=models.IntegerField( blank=True, null=True)
    Value =models.IntegerField( blank=True, null=True)
    Status = models.CharField(max_length=20, choices=Status_CHOICES,default="Out of Stock")
    PurchaseStatus = models.TextField(blank=True, null=True,default=" ")
    salesStatus = models.TextField(blank=True, null=True,default=" ")
    image = models.ImageField(upload_to='stok_prf/', blank=True, null=True)
    shop = models.ForeignKey(ShopDB, on_delete=models.CASCADE,blank=True, null=True)
    
    def __str__(self):
        return f"{self.id} - {self.ItemName} - {self.ItemCode}"