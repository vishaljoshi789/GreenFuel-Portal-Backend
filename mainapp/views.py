import random
import string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from django.utils.crypto import get_random_string
from .models import BusinessUnit, Department, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalLog, Approver
from django.db import transaction
from django.shortcuts import get_object_or_404
from .serializers import BusinessUnitSerializer, DepartmentSerializer, DesignationSerializer, UserInfoSerializer, ApprovalRequestFormSerializer, ApprovalRequestItemSerializer, ApprovalLogSerializer, ApproverSerializer
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
                business_unit=serializer.validated_data['business_unit'],
                department=serializer.validated_data['department'],
                designation=serializer.validated_data['designation'],
                password=password,
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

    def get(self, request, pk=None):
        user = request.user
        if pk:
            user = get_object_or_404(User, pk=pk)
            serializer = UserInfoSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        self_only = request.query_params.get('self', 'false').lower() == 'true'
        designation_id = request.query_params.get('designation', None)
        if designation_id:
            users = User.objects.filter(designation_id=designation_id)
            serializer = UserInfoSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if not self_only:
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

    def get(self, request, pk=None):
        if pk:
            business_unit = get_object_or_404(BusinessUnit, id=pk)
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
    
    def delete(self, request, pk):
        business_unit = get_object_or_404(BusinessUnit, pk=pk)
        business_unit.delete()
        return Response({"message": "Business unit deleted"}, status=status.HTTP_200_OK)


class DepartmentAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, pk=None):
        business_unit_id = request.query_params.get('business_unit', None)
        if pk:
            department = get_object_or_404(Department, id=pk)
            serializer = DepartmentSerializer(department)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if business_unit_id:
            departments = Department.objects.filter(business_unit_id=business_unit_id)
        else:
            departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        department = get_object_or_404(Department, pk=pk)
        department.delete()
        return Response({"message": "Department deleted"}, status=status.HTTP_200_OK)
    

class DesignationAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request, pk=None):
        department_id = request.query_params.get('department', None)
        if pk:
            designation = get_object_or_404(Designation, id=pk)
            serializer = DesignationSerializer(designation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if department_id:
            designations = Designation.objects.filter(department_id=department_id)
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
    
    def delete(self, request, pk):
        designation = get_object_or_404(Designation, pk=pk)
        designation.delete()
        return Response({"message": "Designation deleted"}, status=status.HTTP_200_OK)
    
class ApproverAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            approver = get_object_or_404(Approver, id=pk)
            serializer = ApproverSerializer(approver)
            return Response(serializer.data, status=status.HTTP_200_OK)
        approvers = Approver.objects.all()
        serializer = ApproverSerializer(approvers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ApproverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        approver = get_object_or_404(Approver, pk=pk)
        approver.delete()
        return Response({"message": "Approver deleted"}, status=status.HTTP_200_OK)
    


class ApprovalRequestFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            approval_request = get_object_or_404(ApprovalRequestForm, id=pk)
            serializer = ApprovalRequestFormSerializer(approval_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        approval_requests = ApprovalRequestForm.objects.filter(user=request.user)
        serializer = ApprovalRequestFormSerializer(approval_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        with transaction.atomic():
            serializer = ApprovalRequestFormSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                form = serializer.save(user=request.user)

                items_data = request.data.get("items", [])

                if not items_data:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": "At least one item is required."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for item_data in items_data:
                    ApprovalRequestItem.objects.create(form=form, **item_data, user=request.user)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApprovalRequestItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        form_id = request.query_params.get("form_id")
        if form_id:
            items = ApprovalRequestItem.objects.filter(form_id=form_id)
        else:
            items = ApprovalRequestItem.objects.all()
        serializer = ApprovalRequestItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def post(self, request):
    #     with transaction.atomic():
    #         serializer = ApprovalRequestItemSerializer(data=request.data, many=True)
    #         if serializer.is_valid():
    #             serializer.save(user=request.user)  
    #             return Response(serializer.data, status=status.HTTP_201_CREATED)

    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ApprovalApproveRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        approval_request = get_object_or_404(ApprovalRequestForm, pk=pk)

        if action == "approve":
            approval_log = ApprovalLog.objects.create(
                approval_request=approval_request,
                approver=request.user,
                status="approved",
                comments=request.data.get("comments", ""),
            )
            approval_log.save()
            approval_request.advance_level()
            return Response({"message": "Approval granted"}, status=status.HTTP_200_OK)

        elif action == "reject":
            rejection_reason = request.data.get("comments", "No reason provided")
            approval_log = ApprovalLog.objects.create(
                approval_request=approval_request,
                approver=request.user,
                status="rejected",
                comments=rejection_reason,
            )
            approval_log.save()
            approval_request.reject(rejection_reason)
            return Response({"message": "Approval request rejected"}, status=status.HTTP_200_OK)

        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)


class ApprovalLogListView(APIView):
    def get(self, request):
        logs = ApprovalLog.objects.filter(approver=request.user)
        serializer = ApprovalLogSerializer(logs, many=True)
        return Response(serializer.data)

class PendingApprovalsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_designation = Designation.objects.filter(user=request.user).first()
            if not user_designation:
                return Response({"error": "User has no designation"}, status=status.HTTP_400_BAD_REQUEST)
            pending_forms = ApprovalRequestForm.objects.filter(
                department = user_designation.department,
                current_level=user_designation.level,
                rejected=False
            )
            serializer = ApprovalRequestFormSerializer(pending_forms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)