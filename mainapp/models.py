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
    dob = models.DateField()
    employee_code = models.CharField(max_length=255)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dob', 'employee_code', 'designation']

    objects = UserManager()

    def __str__(self):
        return self.email
