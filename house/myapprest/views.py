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
from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


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
    
    def destroy(self, request, *args, **kwargs):
        house = self.get_object()
        if house.user != request.user:
            return Response({"detail": "You are not allowed to delete this house."},
                            status=status.HTTP_403_FORBIDDEN)
        house.delete()
        return Response({"detail": "House deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

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

        pdf_bytes = generate_booking_pdf(booking)
        if not pdf_bytes:
            return Response({'error': 'Failed to generate PDF'}, status=500)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="rental_agreement.pdf"'
        return response



class UploadSignedAgreementView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        phone_number = request.data.get('phone_number')
        file = request.FILES.get('file')

        if not username or not phone_number or not file:
            return Response({'error': 'All fields are required'}, status=400)

        upload = SignedAgreementUpload.objects.create(
            username=username,
            phone_number=phone_number,
            file=file
        )

        matched_house = House.objects.filter(contact=phone_number).first()

        if matched_house:
            data = {
                'message': 'Upload successful. Matching house found.',
                'house': {
                    'id': matched_house.id,
                    'location': matched_house.location,
                    'house_type': matched_house.house_type,
                    'price': matched_house.price_per_month
                }
            }
        else:
            data = {'message': 'Upload successful. No matching house found.'}

        return Response(data, status=201)
    

class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"  # adjust path as needed

        send_mail(
            subject='Password Reset',
            message=f'Click the link to reset your password: {reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email]
        )

        return Response({'message': 'Password reset link sent to email.'}, status=200)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'error': 'Invalid user ID'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=400)

        new_password = request.data.get('password')
        if not new_password:
            return Response({'error': 'Password is required'}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successfully'}, status=200)

