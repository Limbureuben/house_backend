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
]
