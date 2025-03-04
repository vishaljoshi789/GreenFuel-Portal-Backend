import random
import string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from django.utils.crypto import get_random_string
from .models import BusinessUnit, Designation
from rest_framework import viewsets
from .serializers import BusinessUnitSerializer, DesignationSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

User = get_user_model()

class RegisterUserView(APIView):
    permission_classes = [IsAdminUser]

    def generate_password(self, length=8):
        """Generate a random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Generate a random password
            password = self.generate_password()

            # Create the user
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                dob=serializer.validated_data['dob'],
                employee_code=serializer.validated_data['employee_code'],
                designation=serializer.validated_data['designation'],
                password=password  # Set the generated password
            )

            # Send password via email
            subject = "Your Account Credentials"
            message = f"Hello {user.email},\n\nYour account has been created successfully!\nYour password is: {password}"
            send_mail(subject, message, 'your-email@gmail.com', [user.email])

            return Response({"message": "User registered successfully! Check your email for the password."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def generate_password(self, length=8):
        """Generate a random password."""
        return get_random_string(length, allowed_chars=string.ascii_letters + string.digits + string.punctuation)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            # Generate a new password
            new_password = self.generate_password()

            # Set new password
            user.set_password(new_password)
            user.save()

            # Send the new password via email
            subject = "Password Reset Request"
            message = f"Hello {user.email},\n\nYour new password is: {new_password}"
            send_mail(subject, message, 'your-email@gmail.com', [user.email])

            return Response({"message": "A new password has been sent to your email."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

class BusinessUnitViewSet(viewsets.ModelViewSet):
    queryset = BusinessUnit.objects.all()
    serializer_class = BusinessUnitSerializer

    def get_permissions(self):
            if self.request.method in ['GET']:  # Allow anyone to read
                return [AllowAny]
            return [IsAdminUser]

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer

    def get_permissions(self):
            if self.request.method in ['GET']:  # Allow anyone to read
                return [AllowAny]
            return [IsAdminUser]
