from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max

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
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    status = models.BooleanField(default=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    
    
class ApprovalRequestForm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    policy_agreement = models.BooleanField(default=False)
    initiate_dept = models.CharField(max_length=255)
    current_status = models.CharField(max_length=255, default='Pending')
    benefit_to_organisation = models.TextField()
    approval_category = models.CharField(max_length=255)
    approval_type = models.CharField(max_length=255)
    notify_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notify_to', null=True, blank=True)
    current_level = models.PositiveIntegerField(default=1) 
    max_level = models.PositiveIntegerField(default=1) 
    rejected = models.BooleanField(default=False) 
    rejection_reason = models.TextField(null=True, blank=True)

    def get_max_level(self):
        max_level = Designation.objects.filter(
            user=self.user
        ).aggregate(Max('level'))['level__max']
        
        return max_level if max_level else 0

    def advance_level(self):
        if self.current_level < self.max_level:
            self.current_level += 1
            self.current_status = "In Progress"
        else:
            self.current_status = "Approved"
        self.save()

    def reject(self, reason):
        self.rejected = True
        self.current_status = "Rejected"
        self.rejection_reason = reason
        self.save()
    
class ApprovalRequestItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    per_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sap_code = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    form = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)
    
class ApprovalProcess(models.Model):
    request_form = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)  # New field
    date_approved = models.DateTimeField(null=True, blank=True)
    date_rejected = models.DateTimeField(null=True, blank=True)

    def approve(self):
        self.approved = True
        self.date_approved = models.DateTimeField(auto_now=True)
        self.save()
        self.request_form.advance_level()

    def reject(self, reason):
        self.rejected = True
        self.date_rejected = models.DateTimeField(auto_now=True)
        self.save()
        self.request_form.reject(reason)



    
