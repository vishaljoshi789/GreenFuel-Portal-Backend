import random
import string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from django.utils.crypto import get_random_string
from .models import BusinessUnit, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalProcess
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .serializers import BusinessUnitSerializer, DesignationSerializer, UserInfoSerializer, ApprovalRequestFormSerializer, ApprovalRequestItemSerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

UserModel = get_user_model()

class RegisterUserView(APIView):
    permission_classes = [IsAdminUser]

    def generate_password(self, length=8):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            password = self.generate_password()
            user = UserModel.objects.create_user(
                email=serializer.validated_data['email'],
                name=serializer.validated_data['name'],
                dob=serializer.validated_data['dob'],
                employee_code=serializer.validated_data['employee_code'],
                designation=serializer.validated_data['designation'],
                password=password,
                business_unit=serializer.validated_data['business_unit'],
                department=serializer.validated_data['department'],
                contact=serializer.validated_data['contact'],
                address=serializer.validated_data['address'],
                city=serializer.validated_data['city'],
                state=serializer.validated_data['state'],
                country=serializer.validated_data['country'],
            )
            subject = "Your Account Credentials"
            message = f"Hello {user.email},\n\nYour account has been created successfully!\nYour password is: {password}"
            send_mail(subject, message, 'your-email@gmail.com', [user.email])
            return Response({"message": "User registered successfully! Check your email for the password."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        self_only = request.query_params.get('self', 'false').lower() == 'true'
        if user.is_staff and not self_only:
            users = User.objects.all()
            serializer = UserInfoSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if request.user != user and not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserInfoSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [IsAdminUser]

    def generate_password(self, length=8):
        return get_random_string(length, allowed_chars=string.ascii_letters + string.digits + string.punctuation)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserModel.objects.get(email=email)
            new_password = self.generate_password()
            user.set_password(new_password)
            user.save()
            subject = "Password Reset Request"
            message = f"Hello {user.email},\n\nYour new password is: {new_password}"
            send_mail(subject, message, 'your-email@gmail.com', [user.email])
            return Response({"message": "A new password has been sent to your email."}, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

class BusinessUnitAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, id=None):
        if id:
            business_unit = get_object_or_404(BusinessUnit, id=id)
            serializer = BusinessUnitSerializer(business_unit)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            business_units = BusinessUnit.objects.all()
            serializer = BusinessUnitSerializer(business_units, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BusinessUnitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        business_unit = get_object_or_404(BusinessUnit, pk=pk)
        serializer = BusinessUnitSerializer(business_unit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DesignationAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, id=None):
        business_unit_id = request.query_params.get('business_unit', None)
        if id:
            designation = get_object_or_404(Designation, id=id)
            serializer = DesignationSerializer(designation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if business_unit_id:
            designations = Designation.objects.filter(business_unit_id=business_unit_id)
        else:
            designations = Designation.objects.all()
        serializer = DesignationSerializer(designations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DesignationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        designation = get_object_or_404(Designation, pk=pk)
        serializer = DesignationSerializer(designation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApprovalRequestFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        approval_requests = ApprovalRequestForm.objects.filter(user=request.user)
        serializer = ApprovalRequestFormSerializer(approval_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ApprovalRequestFormSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApprovalRequestItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        form_id = request.query_params.get('form_id')
        if form_id:
            items = ApprovalRequestItem.objects.filter(form_id=form_id)
        else:
            items = ApprovalRequestItem.objects.all()
        serializer = ApprovalRequestItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ApprovalRequestItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApproveRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, form_id):
        try:
            approval_form = ApprovalRequestForm.objects.get(id=form_id)
            user_designation = Designation.objects.filter(user=request.user).first()

            if not user_designation or user_designation.level != approval_form.current_level:
                return Response({"error": "You are not authorized to approve at this level."},
                                status=status.HTTP_403_FORBIDDEN)
            approval_process = ApprovalProcess.objects.get(request_form=approval_form, designation=user_designation)
            if approval_process.approved:
                return Response({"error": "This level is already approved."}, status=status.HTTP_400_BAD_REQUEST)
            approval_process.approve()
            return Response({"message": "Approval successful", "current_level": approval_form.current_level}, status=status.HTTP_200_OK)
        except ApprovalRequestForm.DoesNotExist:
            return Response({"error": "Request form not found"}, status=status.HTTP_404_NOT_FOUND)
        except ApprovalProcess.DoesNotExist:
            return Response({"error": "Approval process not found"}, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, form_id):
        try:
            approval_form = ApprovalRequestForm.objects.get(id=form_id)
            user_designation = Designation.objects.filter(user=request.user).first()
            if not user_designation or user_designation.level != approval_form.current_level:
                return Response({"error": "You are not authorized to reject at this level."},
                                status=status.HTTP_403_FORBIDDEN)
            approval_process = ApprovalProcess.objects.get(request_form=approval_form, designation=user_designation)
            if approval_process.rejected:
                return Response({"error": "This request has already been rejected."}, status=status.HTTP_400_BAD_REQUEST)
            rejection_reason = request.data.get("reason", "No reason provided")
            approval_process.reject(rejection_reason)
            return Response({"message": "Request rejected", "rejection_reason": rejection_reason}, status=status.HTTP_200_OK)
        except ApprovalRequestForm.DoesNotExist:
            return Response({"error": "Request form not found"}, status=status.HTTP_404_NOT_FOUND)
        except ApprovalProcess.DoesNotExist:
            return Response({"error": "Approval process not found"}, status=status.HTTP_400_BAD_REQUEST)
        
class PendingApprovalsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_designation = Designation.objects.filter(user=request.user).first()
            if not user_designation:
                return Response({"error": "User has no designation"}, status=status.HTTP_400_BAD_REQUEST)
            pending_forms = ApprovalRequestForm.objects.filter(
                current_level=user_designation.level,
                rejected=False,
                current_status="In Progress"
            )
            serializer = ApprovalRequestFormSerializer(pending_forms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)