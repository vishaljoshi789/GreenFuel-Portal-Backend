from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BusinessUnit, Designation, User

UserModel = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['email', 'dob', 'employee_code', 'designation']

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
