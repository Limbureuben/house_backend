from django.shortcuts import render
from graphene_django import DjangoObjectType
import graphene
from django.contrib.auth.models import User
from graphql import GraphQLError
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "is_staff", "is_superuser")

class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        confirm_password = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, username, password, confirm_password):
        if password != confirm_password:
            return RegisterUser(success=False, message="Passwords do not match")

        if User.objects.filter(username=username).exists():
            return RegisterUser(success=False, message="Username already exists")

        user = User(
            username=username,
            is_staff=False,
            is_superuser=False
        )
        user.set_password(password)
        user.save()

        return RegisterUser(user=user, success=True, message="User registered successfully")


class LoginUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()
    role = graphene.String()
    token = graphene.String()

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            return LoginUser(success=False, message="Invalid credentials")

        # Create JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Check if the user is a staff (admin) or regular user
        if user.is_staff:
            return LoginUser(
                user=user,
                success=True,
                message="Admin login successful",
                token=access_token,
                role="staff",  # This indicates an admin user

            )
        else:
            return LoginUser(
                user=user,
                success=True,
                message="User login successful",
                token=access_token,
                role="user",  # This indicates a regular user
            )


class CreateBooking(graphene.Mutation):
    class Arguments:
        house_id = graphene.ID(required=True)

    booking = graphene.Field(BookingType)
    pdf_url = graphene.String()

    def mutate(self, info, house_id):
        user = info.context.user
        house = House.objects.get(id=house_id)
        booking = Booking.objects.create(user=user, house=house, status='pending')

        filename = f"agreement_{booking.id}.pdf"
        pdf_path = generate_booking_pdf(booking, filename)

        pdf_url = f"/media/pdfs/{filename}"  # Make sure media is served
        return CreateBooking(booking=booking, pdf_url=pdf_url)
