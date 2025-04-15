from rest_framework import serializers
from .models import House
from django.contrib.auth.models import User

class HouseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    class Meta:
        model = House
        fields = '__all__'