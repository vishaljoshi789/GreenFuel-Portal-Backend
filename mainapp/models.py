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
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    employee_code = models.CharField(max_length=255, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
