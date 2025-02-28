import random
import string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer

User = get_user_model()

class RegisterUserView(APIView):
    def generate_password(self, length=12):
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
                department=serializer.validated_data['department'],
                designation=serializer.validated_data['designation'],
                password=password  # Set the generated password
            )

            # Send password via email
            subject = "Your Account Credentials"
            message = f"Hello {user.email},\n\nYour account has been created successfully!\nYour password is: {password}\n\nPlease change your password after logging in."
            send_mail(subject, message, 'your-email@gmail.com', [user.email])

            return Response({"message": "User registered successfully! Check your email for the password."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
