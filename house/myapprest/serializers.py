from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User

class HouseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = House
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class SignedAgreementUploadSerializer(serializers.Serializer):
    class Meta:
        model = SignedAgreementUpload
        fields = ['username', 'phone_number', 'file']

class UploadedAgreementSerializer(serializers.ModelSerializer):
    from_user = serializers.ReadOnlyField(source='from_user.username')
    to_user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    sender_phone = serializers.CharField(max_length=15)

    class Meta:
        model = UploadedAgreement
        fields = ['id', 'sender_phone', 'from_user', 'to_user', 'file', 'uploaded_at']



class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BookingEventSerializer(serializers.ModelSerializer):
    room = RoomSerializer()

    class Meta:
        model = BookingEvent
        fields = ['id', 'room', 'event_date', 'booking_date', 'reference_number', 'payment_status']

