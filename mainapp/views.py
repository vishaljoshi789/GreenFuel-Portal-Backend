import random
import string
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from django.utils.crypto import get_random_string
from .models import BusinessUnit, Department, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalLog, Approver, Notification, ApprovalRequestCategory
from django.db import transaction
from django.db.models import Q
from django.db.models import Max
from django.shortcuts import get_object_or_404
from .serializers import BusinessUnitSerializer, DepartmentSerializer, DesignationSerializer, UserInfoSerializer, ApprovalRequestFormSerializer, ApprovalRequestItemSerializer, ApprovalLogSerializer, ApproverSerializer, NotificationSerializer, ApprovalRequestCategorySerializer
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
                is_budget_requester=serializer.validated_data.get('is_budget_requester', False)
            )
            subject = "Your Account Credentials"
            message = f"Hello {user.email},\n\nYour account has been created successfully!\nYour password is: {password}"
            send_mail(subject, message, "admin@greenfuelenergy.in", [user.email])
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
            send_mail(subject, message, "admin@greenfuelenergy.in", [user.email])
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
        department = request.query_params.get('department', None)
        if pk:
            approver = get_object_or_404(Approver, id=pk)
            serializer = ApproverSerializer(approver)
            return Response(serializer.data, status=status.HTTP_200_OK)
        type = request.query_params.get('type', None)
        if department:
            approvers = Approver.objects.filter(department_id=department)
        elif type == 'approver':
            approvers = Approver.objects.filter(approver_request_category__isnull=True)
        elif type == 'category':
            approvers = Approver.objects.filter(approver_request_category__isnull=False)
        else:
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
    
class ApprovalRequestCategoryAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get(self, request, pk=None):
        if pk:
            category = get_object_or_404(ApprovalRequestCategory, id=pk)
            serializer = ApprovalRequestCategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        category = ApprovalRequestCategory.objects.all()
        serializer = ApprovalRequestCategorySerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ApprovalRequestCategorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        category = get_object_or_404(ApprovalRequestCategory, id=pk)
        serializer = ApprovalRequestCategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        category = get_object_or_404(ApprovalRequestCategory, id=pk)
        category.delete()
        return Response({"message": "Category deleted"}, status=status.HTTP_200_OK)

class ApprovalRequestFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            approval_request = get_object_or_404(ApprovalRequestForm, id=pk)
            serializer = ApprovalRequestFormSerializer(approval_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        approval_requests = ApprovalRequestForm.objects.filter(Q(user=request.user) | Q(notify_to=request.user))
        serializer = ApprovalRequestFormSerializer(approval_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        with transaction.atomic():
            if not request.user.is_budget_requester:
                return Response({"error": "User is not a budget requester"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ApprovalRequestFormSerializer(data=request.data)
            if serializer.is_valid():
                category_max_level = Approver.objects.filter(approver_request_category=serializer.validated_data['form_category'],department=request.user.department).aggregate(Max('level'))['level__max']
                form_max_level = Approver.objects.filter(department=serializer.validated_data['concerned_department'],approver_request_category__isnull=True).aggregate(Max('level'))['level__max']
                form = serializer.save(user=request.user,form_max_level=form_max_level,category_max_level=category_max_level)

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

        if not Approver.objects.filter(user=request.user).exists():
            return Response({"error": "User is not an approver"}, status=status.HTTP_400_BAD_REQUEST)
        
        if approval_request.rejected:
            return Response({"error": "Approval request has been rejected"}, status=status.HTTP_400_BAD_REQUEST)
        
        if approval_request.department != Approver.objects.filter(user=request.user).first().department:
            return Response({"error": "User is not the approver of this request"}, status=status.HTTP_400_BAD_REQUEST)

        if approval_request.current_form_level == 0 and approval_request.current_category_level != Approver.objects.filter(user=request.user).first().level:
            return Response({"error": "User is not the approver of this request"}, status=status.HTTP_400_BAD_REQUEST)
        elif approval_request.current_form_level != Approver.objects.filter(user=request.user).first().level:
            return Response({"error": "User is not the approver of this request"}, status=status.HTTP_400_BAD_REQUEST)
        if action == "approve":
            approval_log = ApprovalLog.objects.create(
                approval_request=approval_request,
                approver=request.user,
                status="approved",
                comments=request.data.get("comments", ""),
            )
            approval_log.save()
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
        form = request.query_params.get('form', None)
        if form:
            logs = ApprovalLog.objects.filter(approval_request_id=form)
        else:
            logs = ApprovalLog.objects.filter(approver=request.user)
        serializer = ApprovalLogSerializer(logs, many=True)
        return Response(serializer.data)

class PendingApprovalsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_approver = Approver.objects.filter(user=request.user).first()
            if not user_approver:
                return Response({"error": "User is not any approver"}, status=status.HTTP_400_BAD_REQUEST)
            pending_forms = ApprovalRequestForm.objects.filter(
                department = user_approver.department,
                rejected=False
            ).filter(Q(current_form_level=user_approver.level) | Q(current_category_level = user_approver.level))
            serializer = ApprovalRequestFormSerializer(pending_forms, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class NotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, email=None):
        if email:
            user = get_object_or_404(User, email=email)
        else:
            user = request.user
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_notification(self, user, message):
        Notification.objects.create(user=user, message=message)
        subject = "Green Fuel"
        send_mail(subject, message, "admin@greenfuelenergy.in", [user.email])
        return Response({"message": "Notification has been sent"}, status=status.HTTP_200_OK)
    

    def delete(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.delete()
        return Response({"message": "Notification deleted"}, status=status.HTTP_200_OK)