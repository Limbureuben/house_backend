from rest_framework import viewsets
from .models import House
from .serializers import HouseSerializer
from rest_framework import permissions


class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [permissions.AllowAny] 

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)