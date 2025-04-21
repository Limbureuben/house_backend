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