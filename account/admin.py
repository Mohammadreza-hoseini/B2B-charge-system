from django.contrib import admin
from .models import User, Customer, Vendor

# Register your models here.

admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Vendor)
