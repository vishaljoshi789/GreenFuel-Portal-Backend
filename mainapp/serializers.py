from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Max
from .models import BusinessUnit, Department, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalLog, Approver, Notification, ApprovalRequestCategory

UserModel = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'name', 'dob', 'employee_code','business_unit', 'department', 'designation', 'contact', 'address', 'city', 'state', 'country', 'is_budget_requester']

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    business_unit_name = serializers.CharField(source='business_unit.name', read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    business_unit_name = serializers.CharField(source='business_unit.name', read_only=True)

    class Meta:
        model = Designation
        fields = '__all__'

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions', 'is_active', 'is_superuser', 'first_name', 'last_name']

class ApprovalRequestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequestCategory
        fields = '__all__'

class ApproverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Approver
        fields = '__all__'

class ApprovalRequestFormSerializer(serializers.ModelSerializer):
    budget_id = serializers.SerializerMethodField()

    def get_budget_id(self, obj):
        return obj.budget_id

    class Meta:
        model = ApprovalRequestForm
        fields = '__all__'


class ApprovalRequestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequestItem
        fields = '__all__'

class ApprovalLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalLog
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'