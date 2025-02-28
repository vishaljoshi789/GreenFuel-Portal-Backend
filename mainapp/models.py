from django.db import models
from django.contrib.auth.models import AbstractUser

from mainapp.CustomUserManager import UserManager

# Create your models here.
class User(AbstractUser):
    department_choice = (("emp", "Employee"), ("hod", "HOD"), ("finance", "Finance Head"), ("sbo", "SBO Head"), ("md", "Managing Director"))
    email = models.EmailField(unique=True)
    dob = models.DateField()
    employee_code = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=20, choices=department_choice)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dob', 'employee_code', 'department', 'designation']

    objects = UserManager()

    def __str__(self):
        return self.email
