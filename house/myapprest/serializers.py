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
    from_user = serializers.ReadOnlyField(source='from_user.username')  # Read-only field for the logged-in user
    to_user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())  # For selecting the recipient user
    file = serializers.FileField()  # Ensure the 'file' field is included

    class Meta:
        model = UploadedAgreement
        fields = ['id', 'sender_phone', 'from_user', 'to_user', 'file', 'uploaded_at']
