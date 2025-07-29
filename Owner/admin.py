from django.contrib import admin

from Owner.models import UsesDB,remindersDB

# Register your models here.  

admin.site.register(UsesDB)
admin.site.register(remindersDB)
