import os
import uuid
from rest_framework import viewsets

from .tasks import send_reset_email_task
from .models import House
from .serializers import HouseSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .utils.pdf_generator import generate_booking_pdf
from django.http import FileResponse, HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import IsAdminUser
from rest_framework import status, permissions
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from reportlab.lib import colors
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader


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

    
class PasswordResetRequestView(APIView):
    def post(self, request):
        print("PasswordResetRequestView POST called")  # Console debug

        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

        # Use Celery to send the email asynchronously
        send_reset_email_task.delay(email, reset_link)

        return Response({'message': 'Password reset link sent to email.'}, status=200)


class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        print("PasswordResetConfirmView POST called")
        print("Received uidb64:", uidb64)
        print("Received token:", token)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            print("Decoded UID:", uid)
            user = User.objects.get(pk=uid)
            print("User found:", user.username)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError) as e:
            print("Error decoding UID or fetching user:", str(e))
            return Response({'error': 'Invalid user ID'}, status=400)

        if not default_token_generator.check_token(user, token):
            print("Invalid or expired token for user:", user.username)
            return Response({'error': 'Invalid or expired token'}, status=400)

        new_password = request.data.get('password')
        if not new_password:
            print("No password provided")
            return Response({'error': 'Password is required'}, status=400)

        user.set_password(new_password)
        user.save()
        print("Password reset successful for user:", user.username)
        return Response({'message': 'Password reset successfully'}, status=200)


class UploadAgreementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # Copy the request data to safely modify it
        data = request.data.copy()

        # Set the from_user automatically
        from_user = request.user
        data['from_user'] = from_user.username  # If you're using source='from_user.username' as read-only

        # Validate sender phone
        sender_phone = data.get('sender_phone')
        if not sender_phone:
            return Response({'sender_phone': ['Sender phone number is required.']}, status=400)

        # Validate to_user exists
        to_username = data.get('to_user')
        if not to_username:
            return Response({'to_user': ['Receiver username is required.']}, status=400)

        try:
            User.objects.get(username=to_username)
        except User.DoesNotExist:
            return Response({'to_user': [f"Object with username={to_username} does not exist."]}, status=400)

        # Serialize and save
        serializer = UploadedAgreementSerializer(data=data)
        if serializer.is_valid():
            serializer.save(from_user=from_user)  # Set from_user via save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


class ReceivedAgreementsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        agreements = UploadedAgreement.objects.filter(to_user=request.user)
        serializer = UploadedAgreementSerializer(agreements, many=True)
        return Response(serializer.data)


class DownloadAgreementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, filename):
        file_path = os.path.join(settings.MEDIA_ROOT, 'agreements', filename)
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        return Response(status=404)


class UserCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        count = User.objects.count()
        return Response({'total_users': count})
    
class HouseCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        count = House.objects.count()
        return Response({'total_houses': count})


class RegisterRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        if not data.get('location'):
            data['location'] = "Ardhi University"

        serializer = RoomSerializer(data=data)
        if serializer.is_valid():
            serializer.save(is_available=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AvailableRoomsAPIView(APIView):
    def get(self, request):
        rooms = Room.objects.filter(is_available=True)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateBookingEventView(APIView):
    from django.contrib.auth.models import User

class CreateBookingEventView(APIView):
    def post(self, request):
        # Collect user and booking details from request
        user_details = request.data['user_details']
        room_id = request.data['room']
        event_date = request.data['event_date']
        
        room = Room.objects.get(id=room_id)

        try:
            user = User.objects.get(username=user_details['username'])
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        booking = BookingEvent.objects.create(
            user=user,
            room=room,
            event_date=event_date,
        )

        # Generate a reference number for the booking
        booking.generate_reference_number()
        booking.save()

        # Mark the room as unavailable
        room.is_available = False
        room.save()

        # Generate the PDF for the booking
        pdf = self.generate_booking_pdf(booking, user_details, room)

        # Send the email with the PDF attached
        self.send_booking_email(user_details['email'], pdf)

        return Response(BookingEventSerializer(booking).data, status=201)


    def generate_booking_pdf(self, booking, user_details, room):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="booking_{booking.id}.pdf"'
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # Generate QR code (e.g., for booking ID or a URL)
        qr_data = f"Booking ID: {booking.id}\nUser: {user_details['username']}\nEvent Date: {booking.event_date}"
        qr_img = qrcode.make(qr_data)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)

        # Load your logo
        logo_path = "../media/room_images/ardhi.png"  # Replace with actual path
        logo_reader = ImageReader(logo_path)

        # Draw Title
        p.setFont("Helvetica-Bold", 20)
        p.setFillColor(colors.darkblue)
        p.drawCentredString(width / 2.0, height - 60, "Booking Confirmation")
        p.setStrokeColor(colors.grey)
        p.line(50, height - 70, width - 50, height - 70)

        # Draw Logo (top-right corner)
        p.drawImage(logo_reader, width - 150, height - 120, width=80, height=80, mask='auto')

        # Booking Details
        y = height - 140
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(colors.black)
        p.drawString(50, y, "Booking Details")

        p.setFont("Helvetica", 12)
        y -= 20
        p.drawString(70, y, f"Booking ID: {booking.id}")
        y -= 20
        p.drawString(70, y, f"Room: {room.name}")
        y -= 20
        p.drawString(70, y, f"Location: {room.location}")
        y -= 20
        p.drawString(70, y, f"Price: Tsh {room.price}")
        y -= 20
        p.drawString(70, y, f"Event Date: {booking.event_date}")

        y -= 30
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "User Information")

        p.setFont("Helvetica", 12)
        y -= 20
        p.drawString(70, y, f"Name: {user_details['username']}")
        y -= 20
        p.drawString(70, y, f"Email: {user_details['email']}")
        y -= 20
        p.drawString(70, y, f"Phone: {user_details['phone']}")

        y -= 30
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Payment Information")

        p.setFont("Helvetica", 12)
        y -= 20
        p.drawString(70, y, f"Reference Number: {booking.reference_number}")
        y -= 20
        p.drawString(70, y, f"Payment Status: {booking.payment_status}")
        y -= 20
        p.drawString(70, y, f"Amount Paid: Tsh {room.price}")

        # Draw QR Code on the right side
        p.drawImage(qr_reader, width - 150, y - 20, width=100, height=100)

        # Footer
        p.setFont("Helvetica-Oblique", 10)
        p.setFillColor(colors.grey)
        p.drawCentredString(width / 2.0, 30, "Thank you for booking with us!")

        p.showPage()
        p.save()

        return response

    def send_booking_email(self, user_email, pdf):
        subject = "Booking Confirmation"
        message = "Thank you for booking with us. Please find your booking details attached."
        email = EmailMessage(subject, message, to=[user_email])
        email.attach('booking_details.pdf', pdf.content, 'application/pdf')
        email.send()

class BookedRoomsView(APIView):
    def get(self, request):
        bookings = BookingEvent.objects.select_related('room', 'user')
        serializer = BookingEventSerializer(bookings, many=True)
        return Response(serializer.data)
    
    
class InactiveRoomsAPIView(APIView):
    def get(self, request):
        rooms = Room.objects.filter(is_available=False)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ActivateRoomAPIView(APIView):
    def patch(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            room.is_available = True
            room.save()
            return Response({"message": "Room activated"}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

class DashboardStatsAPIView(APIView):
    def get(self, request):
        data = {
            "total_rooms": Room.objects.count(),
            "total_users": User.objects.filter(is_staff=False, is_superuser=False).count(),
            "total_bookings": BookingEvent.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)
