from django.contrib import admin
from .models import CreditRequest, Transaction

admin.site.register(CreditRequest)
admin.site.register(Transaction)
