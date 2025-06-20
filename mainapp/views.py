import random
import string
# from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer
from django.utils.crypto import get_random_string
from .models import BusinessUnit, Department, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalLog, Approver, Notification, Category, FormAttachment, Chat, BudgetAllocation, BudgetAllocationHistory
from django.db import transaction
from django.db.models import Q, F
import json
from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import BusinessUnitSerializer, DepartmentSerializer, DesignationSerializer, UserInfoSerializer, ApprovalRequestFormSerializer, ApprovalRequestItemSerializer, ApprovalLogSerializer, ApproverSerializer, NotificationSerializer, CategorySerializer, FormAttachmentSerializer, ChatSerializer, CustomTokenObtainPairSerializer, BudgetAllocationSerializer, BudgetAllocationHistorySerializer
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from .utils import send_email
from datetime import datetime, date
from calendar import monthrange

UserModel = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        role = response.data.get('role')

        # Set role in cookie
        response.set_cookie(
            key='user_role',
            value=role,
            httponly=False,
            secure=False,
            samesite='Lax',
            max_age=3600,
        )
        return response

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
            if send_email(subject, user.email, message):
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
            users = User.objects.all().filter(is_deleted=False)
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
            if send_email(subject, user.email, message):
                return Response({"message": "A new password has been sent to your email."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Email not sent."}, status=status.HTTP_400_BAD_REQUEST)
        except UserModel.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

class ChangePasswordAPIView(APIView):
    def post(self, request):
        old_pass = request.data["old_pass"]
        new_pass = request.data["new_pass"]
        user = UserModel.objects.get(id = request.user.id)
        if user.check_password(old_pass):
            user.set_password(new_pass)
            user.save()
            return Response({"message": "Password Changed Successfully."})
        else:
            return Response({"message": "Invalid Credentials."})

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
        # elif type == 'approver':
        #     approvers = Approver.objects.filter(approver_request_category__isnull=True)
        # elif type == 'category':
        #     approvers = Approver.objects.filter(approver_request_category__isnull=False)
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

    def put(self, request, pk):
        approver = get_object_or_404(Approver, id=pk)
        serializer = ApproverSerializer(approver, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        approver = get_object_or_404(Approver, id=pk)
        approver.delete()
        return Response({"message": "Approver deleted"}, status=status.HTTP_200_OK)

class CategoryAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get(self, request, pk=None):
        if pk:
            category = get_object_or_404(Category, id=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        category = Category.objects.all()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = get_object_or_404(Category, id=pk)
        category.delete()
        return Response({"message": "Category deleted"}, status=status.HTTP_200_OK)

class ApprovalRequestFormAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            approval_request = get_object_or_404(ApprovalRequestForm, id=pk)
            serializer = ApprovalRequestFormSerializer(approval_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.user.is_staff:
            approval_requests = ApprovalRequestForm.objects.all()
        else:
            approval_requests = ApprovalRequestForm.objects.filter(Q(user=request.user) | Q(notify_to=request.user))
        serializer = ApprovalRequestFormSerializer(approval_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        with transaction.atomic():
            if not request.user.is_budget_requester:
                return Response({"error": "User is not a budget requester"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ApprovalRequestFormSerializer(data=request.data)
            if serializer.is_valid():
                # category_max_level = Approver.objects.filter(approver_request_category=serializer.validated_data['form_category'],department=request.user.department).aggregate(Max('level'))['level__max']
                form_max_level = Approver.objects.filter(department=serializer.validated_data['concerned_department']).aggregate(Max('level'))['level__max']
                form = serializer.save(user=request.user,form_max_level=form_max_level)

                items_data = request.data.getlist("items", [])

                if not items_data:
                    transaction.set_rollback(True)
                    return Response(
                        {"error": "At least one item is required."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                for item_data in items_data:
                    try:
                        item_dict = json.loads(item_data)
                        ApprovalRequestItem.objects.create(form=form, **item_dict, user=request.user)
                    except json.JSONDecodeError:
                        transaction.set_rollback(True)
                        return Response(
                            {"error": "Invalid item format."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                form_attachments = request.FILES.getlist("form_attachments")
                for attachment in form_attachments:
                    FormAttachment.objects.create(form=form, file=attachment, type="Form")

                asset_attachments = request.FILES.getlist("asset_attachments")
                for attachment in asset_attachments:
                    FormAttachment.objects.create(form=form, file=attachment, type="Asset")

                # Notify the user
                approver = Approver.objects.get(department=serializer.validated_data['concerned_department'], level=1)
                subject = "Action Required: CAPEX Request Awaiting Approval"
                to_email = approver.user.email
                plain_message = f"""
                    Dear {approver.user.name},

                    A procurement request has been submitted via the Sugamgreenfuel portal and is pending for your approval.

                    Request ID: {form.budget_id}
                    Submitted By: {form.user.name} ({form.user.email}) / {form.department.name}
                    Amount: {form.total}

                    Please review and take necessary action by logging into the system: https://sugamgreenfuel.in
                    """

                html_message = f"""
                        <p>Dear {approver.user.name},</p>
                        <p>A procurement request has been submitted via the <strong>Sugamgreenfuel</strong> portal and is pending for your approval.</p>
                        <p>
                        <strong>Request ID:</strong> {form.budget_id}<br>
                        <strong>Submitted By:</strong> {form.user.name} ({form.user.email}) / {form.department.name}<br>
                        <strong>Amount:</strong> {form.total}
                        </p>
                        <p>
                        Please review and take necessary action by logging into the system:
                        <a href="https://sugamgreenfuel.in" target="_blank">SUGHAMGREENFUEL.IN</a>
                        </p>
                    """
                if send_email(subject, to_email, plain_message, html_message):
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"message": "Email not sent."}, status=status.HTTP_400_BAD_REQUEST)

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

class FormAttachmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        form_id = request.query_params.get("form_id")
        if form_id:
            attachments = FormAttachment.objects.filter(form_id=form_id)
        else:
            attachments = FormAttachment.objects.all()
        serializer = FormAttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ApprovalApproveRejectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        approval_request = get_object_or_404(ApprovalRequestForm, id=pk)

        user_approvers = Approver.objects.filter(user=request.user)

        if not Approver.objects.filter(user=request.user).exists() and request.user.role != 'MD':
            return Response({"error": "User is not an approver"}, status=status.HTTP_400_BAD_REQUEST)

        if approval_request.rejected and request.user.role != 'MD':
            return Response({"error": "Approval request has been rejected"}, status=status.HTTP_400_BAD_REQUEST)

        if not any(approval_request.department == approver.department for approver in user_approvers) and request.user.role != 'MD':
            return Response({"error": "User is not the approver of this request"}, status=status.HTTP_400_BAD_REQUEST)

        # if approval_request.current_form_level == 0 and not any(approval_request.current_category_level == approver.level and approval_request.form_category == approver.approver_request_category for approver in user_approvers):
        #     return Response({"error": "User is not the approver of this request"}, status=status.HTTP_400_BAD_REQUEST)
        # if not any(approval_request.current_form_level == approver.level for approver in user_approvers):
        #     return Response({"error": "User is not the approver of this request"}, status=status.HTTP_400_BAD_REQUEST)
        if action == "approve":
            approval_log = ApprovalLog.objects.create(
                approval_request=approval_request,
                approver=request.user,
                status="approved",
                comments=request.data.get("comments", ""),
            )
            approval_log.save()

            #notify approver
            approver = Approver.objects.filter(department=approval_request.concerned_department, level=approval_request.current_form_level).first()
            if approver:
                subject = "Action Required: CAPEX Request Awaiting Approval"
                to_email = approver.user.email
                plain_message = f"""
                        Dear {approver.user.name},

                        A procurement request has been submitted via the Sugamgreenfuel portal and is pending for your approval.

                        Request ID: {approval_request.budget_id}
                        Submitted By: {approval_request.user.name} ({approval_request.user.email}) / {approval_request.department.name}
                        Amount: {approval_request.total}

                        Please review and take necessary action by logging into the system: https://sugamgreenfuel.in
                        """

                html_message = f"""
                            <p>Dear {approver.user.name},</p>
                            <p>A procurement request has been submitted via the <strong>Sugamgreenfuel</strong> portal and is pending for your approval.</p>
                            <p>
                            <strong>Request ID:</strong> {approval_request.budget_id}<br>
                            <strong>Submitted By:</strong> {approval_request.user.name} ({approval_request.user.email}) / {approval_request.department.name}<br>
                            <strong>Amount:</strong> {approval_request.total}
                            </p>
                            <p>
                            Please review and take necessary action by logging into the system:
                            <a href="https://sugamgreenfuel.in" target="_blank">SUGHAMGREENFUEL.IN</a>
                            </p>
                        """
                if send_email(subject, to_email, plain_message, html_message):
                    return Response({"message": "Approval granted"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Email not sent."}, status=status.HTTP_400_BAD_REQUEST)
            else:
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
            user_approvers = Approver.objects.filter(user=request.user)
            query = Q()

            for approver in user_approvers:
                query |= Q(
                    concerned_department=approver.department,
                    current_form_level=approver.level
                )
                # | Q(
                #     current_category_level=approver.level,
                #     form_category=approver.approver_request_category,
                #     department=approver.department
                # )

            pending_forms = ApprovalRequestForm.objects.filter(query, rejected=False).distinct()
            if request.user.role == "MD":
                pending_forms = ApprovalRequestForm.objects.filter(current_form_level__gt=F('form_max_level'), total__gte=5000000, status="Pending for MD approval.")
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
        send_email(subject, message, "admin@greenfuelenergy.in", [user.email])
        return Response({"message": "Notification has been sent"}, status=status.HTTP_200_OK)


    def delete(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        notification.delete()
        return Response({"message": "Notification deleted"}, status=status.HTTP_200_OK)

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        form_id = request.query_params.get("form_id")
        if form_id:
            chats = Chat.objects.filter(form_id=form_id)
            serializer = ChatSerializer(chats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Form ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApprovalDashboardView(APIView):
    def get(self, request):
        user = request.user
        pending_count = ApprovalRequestForm.objects.filter(user=user, status='Pending', rejected=False).count()
        approved_count = ApprovalRequestForm.objects.filter(user=user, status='Approved', rejected=False).count()
        rejected_count = ApprovalRequestForm.objects.filter(user=user, rejected=True).count()
        form_count = ApprovalRequestForm.objects.filter(user=user).count()
        context = {
                    'pending_count': pending_count,
                    'approved_count': approved_count,
                    'rejected_count': rejected_count,
                    'form_count': form_count
        }
        return Response(context, status=status.HTTP_200_OK)

class UserYearlyStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year_str = request.query_params.get('year')

        if not year_str:
            return Response({"error": "Missing 'year' parameter. Use format YYYY."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year_str)
        except ValueError:
            return Response({"error": "Invalid year format. Use YYYY."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        yearly_stats = []

        for month in range(1, 13):
            month_start = date(year, month, 1)
            last_day = monthrange(year, month)[1]
            month_end = date(year, month, last_day + 1)

            base_qs = ApprovalRequestForm.objects.filter(
                user=user,
                date__gte=month_start,
                date__lt=month_end
            )

            monthly_data = {
                "month": month_start.strftime("%B"),
                "created": base_qs.count(),
                "approved": base_qs.filter(current_status='Approved').count(),
                "rejected": base_qs.filter(rejected=True).count(),
            }

            yearly_stats.append(monthly_data)

        return Response({
            "year": year,
            "data": yearly_stats
        }, status=status.HTTP_200_OK)

class UserBudgetAllocationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        department = request.query_params.get('department', None)
        category = request.query_params.get('category', None)
        budget_allocations = BudgetAllocation.objects.filter(department=department, category=category)
        serializer = BudgetAllocationSerializer(budget_allocations)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        department = request.data.get('department')
        category = request.data.get('category')
        amount = request.data.get('amount')
        transaction_type = request.data.get('transaction_type')
        remarks = request.data.get('remarks')

        if not all([department, category, amount, transaction_type]):
            return Response(
                {"error": "Missing required fields"},
                status=status.HTTP_400_BAD_REQUEST
            )

        budget_allocation = BudgetAllocation.objects.filter(
            department=department,
            category=category
        ).first()

        if not budget_allocation:
            budget_allocation = BudgetAllocation.objects.create(
                department=department,
                category=category
            )

        BudgetAllocationHistory.objects.create(
            budget_allocation=budget_allocation,
            amount=amount,
            transaction_type=transaction_type,
            remarks=remarks
        )

        serializer = BudgetAllocationSerializer(budget_allocation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserBudgetAllocationHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        department = request.query_params.get('department', None)
        category = request.query_params.get('category', None)
        budget_allocations = BudgetAllocationHistory.objects.filter(budget_allocation__department=department, budget_allocation__category=category)
        serializer = BudgetAllocationHistorySerializer(budget_allocations)
        return Response(serializer.data, status=status.HTTP_200_OK)
