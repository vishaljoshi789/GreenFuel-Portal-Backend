from django.db import models
from django.contrib.auth.models import AbstractUser

from mainapp.CustomUserManager import UserManager

class BusinessUnit(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return str(self.name)

class Designation(models.Model):
    name = models.CharField(max_length=300)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    level = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)


# Create your models here.
class User(AbstractUser):
    designation_choice = (("emp", "Employee"), ("hod", "HOD"), ("finance", "Finance Head"), ("sbo", "SBO Head"), ("md", "Managing Director"))
    email = models.EmailField(unique=True)
    dob = models.DateField()
    employee_code = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=20, choices=designation_choice)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dob', 'employee_code', 'department', 'designation']

    objects = UserManager()

    def __str__(self):
        return self.email
