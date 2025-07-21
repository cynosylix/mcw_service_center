from django.db import models

# Create your models here.
class ShopDB(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,blank=True, null=True)
    def __str__(self):
        return f"{self.id} - {self.name}"
    
class UsesDB(models.Model):
    CATEGORY_CHOICES = [
        ('Purchase Staff', 'Purchase Staff'),
        ('Helper', 'Helper'),
        ('Supervisor', 'Supervisor'),
        ('Mechanic', 'Mechanic'),
        ('Owner', 'Owner'), 	
        ('Senior Mechanic', 'Senior Mechanic'), 
    ]
    Status_CHOICES = [
        ('Active', 'Active'),
        ('InActive', 'InActive'),
        ('On Leave', 'On Leave'),
      
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100,blank=True, null=True)
    shop = models.ForeignKey(ShopDB, on_delete=models.CASCADE,blank=True, null=True)
    password = models.CharField(max_length=100,blank=True, null=True)
    position = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True,default="Helper")
    email = models.EmailField()
    mobile = models.CharField(max_length=15, blank=True, null=True)
    JoinDate=models.CharField(max_length=15, blank=True, null=True)
    ResignDate=models.CharField(max_length=15, blank=True, null=True)
    Status = models.CharField(max_length=20, choices=Status_CHOICES,default="InActive")
    BasicSalary=models.IntegerField( blank=True, null=True)
    BankAccount=models.CharField(max_length=100, blank=True, null=True)
    address_line1 = models.CharField(max_length=100, blank=True, null=True)
    address_line2 = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(upload_to='user_prf/', blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.name} - {self.position}"