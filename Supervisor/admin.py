from django.contrib import admin

from Supervisor.models import CustomerDB,VehicleDB,JobCardPartsDB,JobCardDB

# Register your models here.
admin.site.register(CustomerDB)
admin.site.register(VehicleDB)
admin.site.register(JobCardPartsDB)
admin.site.register(JobCardDB)
