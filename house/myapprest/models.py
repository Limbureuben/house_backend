from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

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
    

class Room(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255, default="Ardhi University")
    available_date = models.DateField()
    image = models.ImageField(upload_to='room_images/')
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    date_booked = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} booked {self.house.house_type}"


class SignedAgreementUpload(models.Model):
    username = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    file = models.FileField(upload_to='signed_agreements/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class UploadedAgreement(models.Model):
    sender_phone = models.CharField(max_length=15, null=True)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_agreements')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_agreements')
    file = models.FileField(upload_to='agreements/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class BookingEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_date = models.DateField(auto_now_add=True)
    event_date = models.DateField()
    reference_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')

    def generate_reference_number(self):
        # Generate a unique reference number (for example, combining user ID and booking ID)
        self.reference_number = f"BOOK-{self.id}-{self.user.id}"

    def __str__(self):
        return f"{self.user.username} - {self.room.name}"
