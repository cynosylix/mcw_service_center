from django.db import models

from Owner.models import UsesDB
from Spare_Purchase.models import StockDB

# Create your models here.
class CustomerDB(models.Model):
    createdby = models.ForeignKey(UsesDB, on_delete=models.CASCADE, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    editeed_details = models.TextField(blank=True, null=True)
    customernotes = models.TextField(blank=True,  null=True)
    
    def __str__(self):
        return f"{self.id} - {self.name}"
    
class VehicleDB(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(CustomerDB, on_delete=models.CASCADE)
    registration_no = models.CharField(max_length=20,blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    make = models.CharField(max_length=50, blank=True, null=True)
    chassis_no = models.CharField(max_length=50, blank=True, null=True)
    engine_no = models.CharField(max_length=50, blank=True, null=True)
    petrol_level = models.CharField(max_length=250, blank=True, null=True )
    notes = models.TextField(blank=True,  null=True)
    
    def __str__(self):
        return f"{self.id} - {self.registration_no}"
    

    
class JobCardDB(models.Model):
    JOB_TYPE_CHOICES = [
        ('Service', 'Service'),
        ('Repair', 'Repair'),
        ('Inspection', 'Inspection'),
        ('Custom', 'Custom Work'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]
    PAYMENT_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(CustomerDB, on_delete=models.CASCADE, blank=True, null=True)
    vehicle = models.ForeignKey(VehicleDB, on_delete=models.CASCADE, blank=True, null=True)

    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, null=True)
    received_date = models.DateField( blank=True, null=True)
    delivery_date = models.DateField( blank=True, null=True)
    assigned_staff = models.ForeignKey(UsesDB, on_delete=models.CASCADE)
    work_description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', blank=True, null=True)
    labor_hours = models.DecimalField(max_digits=5, decimal_places=2, default=1, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, blank=True, null=True)
    TotalPayent = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paymentStatus= models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='Pending', blank=True, null=True)
    
    
    def __str__(self):
        return f"JC-{self.id} - {self.customer.name} - {self.vehicle.registration_no}"

class JobCardPartsDB(models.Model):
    JobCart = models.ForeignKey(JobCardDB, on_delete=models.CASCADE, blank=True, null=True)
    id = models.AutoField(primary_key=True)
    part_obj = models.ForeignKey(StockDB, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    
    
    def __str__(self):
        return f"{self.id} - {self.part_obj.ItemName} x{self.quantity}"