from django.contrib import admin
from .models import *

# Register your models here.

class HouseAdmin(admin.ModelAdmin):
    list_display = ('house_type', 'location', 'availability_date', 'contact')
    list_per_page = 10
admin.site.register(House, HouseAdmin)


class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'house', 'date_booked')
    list_per_page = 8
admin.site.register(Booking, BookingAdmin)

class SignedAgreementUploadAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'uploaded_at')
admin.site.register(SignedAgreementUpload, SignedAgreementUploadAdmin)

class UploadedAgreementAdmin(admin.ModelAdmin):
    list_display = ('sender_phone','from_user', 'to_user', 'uploaded_at')
admin.site.register(UploadedAgreement, UploadedAgreementAdmin)