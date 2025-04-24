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
    to_username = serializers.CharField(write_only=True)

    class Meta:
        model = UploadedAgreement
        fields = ['to_username', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def create(self, validated_data):
        to_username = validated_data.pop('to_username')
        try:
            to_user = User.objects.get(username=to_username)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient user not found")

        agreement = UploadedAgreement.objects.create(
            from_user=self.context['request'].user,
            to_user=to_user,
            **validated_data
        )
        return agreement
