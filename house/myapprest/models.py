from django.db import models
from django.contrib.auth.models import User

class House(models.Model):
    HOUSE_TYPES = [
        ('apartment', 'Apartment'),
        ('bedsitter', 'Bedsitter'),
        ('single_room', 'Single Room'),
        ('bungalow', 'Bungalow'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='houses')
    house_type = models.CharField(max_length=20, choices=HOUSE_TYPES)
    number_of_rooms = models.PositiveIntegerField()
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='house_images/')
    availability_date = models.DateField()
    contact = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.house_type} - {self.location}"
