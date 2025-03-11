from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Max
from .models import BusinessUnit, Department, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalProcess

UserModel = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'name', 'dob', 'employee_code','business_unit', 'department', 'designation', 'contact', 'address', 'city', 'state', 'country']

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
        exclude = ['password', 'groups', 'user_permissions', 'is_staff', 'is_active', 'is_superuser', 'first_name', 'last_name']

class ApprovalRequestFormSerializer(serializers.ModelSerializer):
    budget_id = serializers.SerializerMethodField()

    def get_budget_id(self, obj):
        return obj.budget_id

    class Meta:
        model = ApprovalRequestForm
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        max_level = Designation.objects.filter(user=user).aggregate(Max('level'))['level__max']
        max_level = max_level if max_level else 0
        validated_data['current_level'] = user.designation.level + 1
        validated_data['max_level'] = max_level

        return super().create(validated_data)

class ApprovalRequestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequestItem
        fields = '__all__'

class ApprovalProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalProcess
        fields = '__all__'
