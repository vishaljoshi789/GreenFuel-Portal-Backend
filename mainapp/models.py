from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Max

from mainapp.CustomUserManager import UserManager

class BusinessUnit(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return str(self.name)
    
class Department(models.Model):
    name = models.CharField(max_length=300)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.name)

class Designation(models.Model):
    name = models.CharField(max_length=300)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    level = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    employee_code = models.CharField(max_length=255, null=True, blank=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.CASCADE, null=True, blank=True)
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
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_unit = models.ForeignKey("BusinessUnit", on_delete=models.CASCADE, null=True)
    department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, related_name='department')
    designation = models.ForeignKey("Designation", on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Fixed amount reference
    reason = models.TextField()
    policy_agreement = models.BooleanField(default=False)
    initiate_dept = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, related_name='initiate_dept')
    current_status = models.CharField(max_length=255, default='Pending')
    benefit_to_organisation = models.TextField()
    approval_category = models.CharField(max_length=255)
    approval_type = models.CharField(max_length=255)
    notify_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notify_to', null=True, blank=True)
    current_level = models.PositiveIntegerField(default=1)
    max_level = models.PositiveIntegerField(default=1)
    rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)

    @property
    def budget_id(self):
        return str(self.id + 9999999)

    def advance_level(self):
        if self.current_level < self.max_level:
            self.current_level += 1 
            if self.current_level == self.max_level and self.total > 5000000: 
                self.current_status = "Waiting for MD Approval"
            else:
                self.current_status = "In Progress"
        else:
           self.current_status = "Approved"
        self.save()

    def reject(self, reason):
        self.rejected = True
        self.current_status = "Rejected"
        self.current_level = self.user.designation.level
        self.rejection_reason = reason
        self.save()


class ApprovalLog(models.Model):
    approval_request = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE, related_name='approval_logs')
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding 
        previous_status = None

        if not is_new:
            previous_status = ApprovalLog.objects.get(pk=self.pk).status 

        super().save(*args, **kwargs)

        if is_new or (previous_status != self.status):
            if self.status == 'approved':
                self.approval_request.advance_level()
            elif self.status == 'rejected':
                self.approval_request.reject(self.comments or "No reason provided")
    
class ApprovalRequestItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    per_unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sap_code = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    form = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return str(self.user)
