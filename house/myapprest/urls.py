from django.urls import path
from .views import *

house_list = HouseViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

house_detail = HouseViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('houses/', house_list, name='house-list'),
    path('houses/<int:pk>/', house_detail, name='house-detail'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('book/', CreateBookingView.as_view(), name='create-booking'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('received-agreements/', ReceivedAgreementsView.as_view(), name='my-received-agreements'),
    path('agreement/', UploadAgreementView.as_view(), name='upload-agreement'),
    path('agreement/download/<str:filename>/', DownloadAgreementView.as_view(), name='download-agreement'),
    path('user-count/', UserCountView.as_view(), name='user-count'),
    path('house-count/', HouseCountView.as_view(), name='house-count'),
    path('register-room/', RegisterRoomView.as_view(), name='register-room'),
    path('book-room/', CreateBookingView.as_view(), name='book-room'),
    path('available-rooms/', AvailableRoomsAPIView.as_view(), name='available-rooms'),
    path('generate-pdf/<int:booking_id>/', generate_booking_pdf, name='generate-booking-pdf'),
    path('booking-events/', CreateBookingEventView.as_view(), name='create-booking-event'),
]
