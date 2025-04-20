from django.contrib import admin
from .models import *

# Register your models here.

class HouseAdmin(admin.ModelAdmin):
    list_display = ('house_type', 'location', 'availability_date', 'contact')
admin.site.register(House, HouseAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'house', 'booked_at')
admin.site.register(Booking, BookingAdmin)