from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BusinessUnit, Designation, User, ApprovalRequestForm, ApprovalRequestItem, ApprovalProcess

UserModel = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'name', 'dob', 'employee_code', 'designation', 'business_unit', 'department', 'contact', 'address', 'city', 'state', 'country']

class BusinessUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUnit
        fields = '__all__'

class DesignationSerializer(serializers.ModelSerializer):
    business_unit_name = serializers.CharField(source='business_unit.name', read_only=True)

    class Meta:
        model = Designation
        fields = '__all__'

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ApprovalRequestFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequestForm
        fields = '__all__'

class ApprovalRequestItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalRequestItem
        fields = '__all__'

class ApprovalProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalProcess
        fields = '__all__'
