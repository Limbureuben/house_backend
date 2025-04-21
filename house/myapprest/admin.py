from django.contrib import admin
from .models import *

# Register your models here.

class HouseAdmin(admin.ModelAdmin):
    list_display = ('house_type', 'location', 'availability_date', 'contact')
admin.site.register(House, HouseAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'house', 'date_booked')
admin.site.register(Booking, BookingAdmin)

class SignedAgreementUploadAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'uploaded_at')
admin.site.register(SignedAgreementUpload, SignedAgreementUploadAdmin)