from rest_framework import viewsets
from .models import House
from .serializers import HouseSerializer
from django.contrib.auth.models import User

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')
        if user_id:
            user = User.objects.get(id=user_id)  # Fetch user based on provided ID
            serializer.save(user=user)
        else:
            serializer.save()

    def get_queryset(self):
        user_id = self.request.query_params.get('user', None)
        if user_id:
            return House.objects.filter(user_id=user_id)
        return House.objects.all()