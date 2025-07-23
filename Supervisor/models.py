from datetime import date, datetime
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
    


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
        ('on_leave', 'On Leave'),
        ('overtime', 'Overtime'),
    ]
    
    employee = models.ForeignKey(UsesDB, on_delete=models.CASCADE, related_name='attendances', null=True)
    date = models.DateField(null=True, blank=True, default=date.today)
    
    # Morning session
    morning_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    morning_check_in = models.TimeField(null=True, blank=True)
    morning_check_out = models.TimeField(null=True, blank=True)
    morning_remarks = models.TextField(null=True, blank=True)
    
    # Afternoon session
    afternoon_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    afternoon_check_in = models.TimeField(null=True, blank=True)
    afternoon_check_out = models.TimeField(null=True, blank=True)
    afternoon_remarks = models.TextField(null=True, blank=True)
    
    # Overtime session
    overtime_check_in = models.TimeField(null=True, blank=True)
    overtime_check_out = models.TimeField(null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_approved = models.BooleanField(default=False)
    overtime_remarks = models.TextField(null=True, blank=True)
    
    # Daily summary
    total_working_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    late_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    day_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    daily_remarks = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')
        ordering = ['-date', 'employee__name']

    def __str__(self):
        return f"{self.employee.name if self.employee else 'No employee'} - {self.date}"
    
    def save(self, *args, **kwargs):
        self.calculate_working_hours()
        super().save(*args, **kwargs)
    
    def calculate_working_hours(self):
        total_hours = 0
        late_hours = 0
        overtime_hours = 0
        
        # Calculate morning session
        if self.morning_check_in and self.morning_check_out:
            morning_start = datetime.combine(date.today(), self.morning_check_in)
            morning_end = datetime.combine(date.today(), self.morning_check_out)
            morning_hours = (morning_end - morning_start).total_seconds() / 3600
            total_hours += morning_hours
            
            # Check for late arrival (after 8:30 AM)
            if self.morning_check_in > datetime.strptime('08:30', '%H:%M').time():
                late_start = datetime.combine(date.today(), datetime.strptime('08:30', '%H:%M').time())
                late_hours += (morning_start - late_start).total_seconds() / 3600
        
        # Calculate afternoon session
        if self.afternoon_check_in and self.afternoon_check_out:
            afternoon_start = datetime.combine(date.today(), self.afternoon_check_in)
            afternoon_end = datetime.combine(date.today(), self.afternoon_check_out)
            afternoon_hours = (afternoon_end - afternoon_start).total_seconds() / 3600
            total_hours += afternoon_hours
            
            # Check for late arrival (after 1:00 PM)
            if self.afternoon_check_in > datetime.strptime('13:00', '%H:%M').time():
                late_start = datetime.combine(date.today(), datetime.strptime('13:00', '%H:%M').time())
                late_hours += (afternoon_start - late_start).total_seconds() / 3600
        
        # Calculate overtime
        if self.overtime_check_in and self.overtime_check_out:
            overtime_start = datetime.combine(date.today(), self.overtime_check_in)
            overtime_end = datetime.combine(date.today(), self.overtime_check_out)
            overtime_hours = (overtime_end - overtime_start).total_seconds() / 3600
        
        self.total_working_hours = total_hours
        self.late_hours = late_hours
        self.overtime_hours = overtime_hours
        
        # Determine day status
        if self.morning_status == 'absent' and self.afternoon_status == 'absent':
            self.day_status = 'absent'
        elif self.morning_status == 'present' and self.afternoon_status == 'present':
            self.day_status = 'present'
        elif self.morning_status == 'late' or self.afternoon_status == 'late':
            self.day_status = 'late'
        elif self.morning_status == 'half_day' or self.afternoon_status == 'half_day':
            self.day_status = 'half_day'
        elif self.morning_status == 'on_leave' or self.afternoon_status == 'on_leave':
            self.day_status = 'on_leave'
        else:
            self.day_status = 'absent'
