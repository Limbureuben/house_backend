from rest_framework import viewsets
from .models import House
from .serializers import HouseSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .utils.pdf_generator import generate_booking_pdf

class HouseViewSet(viewsets.ModelViewSet):
    queryset = House.objects.all()
    serializer_class = HouseSerializer
    permission_classes = [IsAuthenticated]  # Ensure that only authenticated users can interact with this viewset

    def perform_create(self, serializer):
        user_id = self.request.data.get('user')  # Get the user ID from the request data
        if user_id:
            try:
                user = User.objects.get(id=user_id)  # Fetch user based on the provided user ID
                serializer.save(user=user)  # Save the house with the associated user
            except User.DoesNotExist:
                raise ValueError("User with provided ID does not exist.")  # Handle case where user is not found
        else:
            # If no user is provided, associate the house with the currently authenticated user
            serializer.save(user=self.request.user)

    def get_queryset(self):
        user_id = self.request.query_params.get('user', None)  # Get the user ID from the query parameters
        if user_id:
            # If user ID is provided in the query parameters, return houses belonging to that user
            return House.objects.filter(user_id=user_id)
        return House.objects.all()

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        house_id = request.data.get('house_id')
        if not house_id:
            return Response({'error': 'House ID is required'}, status=400)

        try:
            house = House.objects.get(id=house_id)
        except House.DoesNotExist:
            return Response({'error': 'House not found'}, status=404)

        booking = Booking.objects.create(user=request.user, house=house)

        # Generate PDF agreement
        filename = f"booking_{booking.id}.pdf"
        pdf_path = generate_booking_pdf(booking, filename)

        return Response({
            'message': 'Booking created',
            'pdf_url': request.build_absolute_uri(f"/media/pdfs/{filename}")
        }, status=201)