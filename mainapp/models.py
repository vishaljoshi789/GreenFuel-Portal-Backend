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
    # level = models.PositiveIntegerField()

    def __str__(self):
        return str(self.name)


# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (("ADMIN", "ADMIN"), ("APPROVER", "APPROVER"), ("MD", "MD"), ("EMPLOYEE", "EMPLOYEE"))

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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    status = models.BooleanField(default=True)
    is_budget_requester = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Approver(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # approver_request_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    level = models.PositiveIntegerField()

    def __str__(self):
        return str(self.user)

class ApprovalRequestForm(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_unit = models.ForeignKey("BusinessUnit", on_delete=models.CASCADE, null=True)
    department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, related_name='department')
    designation = models.ForeignKey("Designation", on_delete=models.CASCADE, null=True)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    policy_agreement = models.BooleanField(default=False)
    concerned_department = models.ForeignKey("Department", on_delete=models.CASCADE, null=True, related_name='concerned_department')
    status = models.CharField(max_length=255, default='Pending')
    benefit_to_organisation = models.TextField()
    approval_category = models.CharField(max_length=255)
    notify_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notify_to', null=True, blank=True)
    # form_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    # current_category_level = models.IntegerField(default=1)
    # category_max_level = models.PositiveIntegerField(default=1, null=True)
    current_form_level = models.IntegerField(default=0)
    form_max_level = models.PositiveIntegerField(default=1, null=True)
    rejected = models.BooleanField(default=False)
    rejection_reason = models.TextField(null=True, blank=True)
    payback_period = models.CharField(max_length=255, null=True, blank=True)
    document_enclosed_summary = models.TextField(null=True, blank=True)
    current_status = models.CharField(max_length=255, default='Pending')

    @property
    def budget_id(self):
        return str(self.id + 9999999)


    def advance_form_level(self):
        # if self.current_category_level != 0 and self.current_category_level < self.category_max_level:
        #     self.current_category_level += 1
        # elif self.current_category_level == self.category_max_level:
        #     self.current_form_level = 1
        #     self.current_category_level = 0
        if self.current_form_level == 0:
            self.status = "Rejected"
            self.current_status = "Rejected"
        elif self.current_form_level < self.form_max_level:
            self.current_form_level += 1
        else:
            if self.total >= 5000000 and self.status!="Pending for MD approval.":
                self.status = "Pending for MD approval."
                self.current_status = "Pending for MD approval."
                self.current_form_level = self.current_form_level + 1
            else:
                self.current_form_level = self.current_form_level + 1
                self.status = "Approved"
                self.current_status = "Approved"

                budget = BudgetAllocation.objects.filter(
                    business_unit=self.business_unit,
                    department=self.department,
                    category__name=self.approval_category
                ).first()
                print(budget)
                if budget:
                    budget_allocation_history = BudgetAllocationHistory(
                        transaction_type='DEBIT',
                        budget_allocation=budget,
                        amount=self.total,
                        remarks=f"Budget used for approval request {self.budget_id}"
                    )
                    budget_allocation_history.save()
        self.save()

    def reject(self, reason):
        self.rejected = True
        self.status = "Rejected"
        self.current_status = "Rejected"
        self.current_form_level = 0
        # self.current_category_level = 0
        self.rejection_reason = reason
        self.save()

class FormAttachment(models.Model):
    TYPE_CHOICES = (('Asset', 'Asset'), ('Form', 'Form'))
    form = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.form)


class ApprovalLog(models.Model):
    approval_request = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE, related_name='approval_logs')
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='pending')
    approved_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        previous_status = None

        if not is_new:
            previous_status = ApprovalLog.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if is_new or (previous_status != self.status):
            if self.status == 'approved':
                self.approval_request.advance_form_level()
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

class Chat(models.Model):
    form = models.ForeignKey(ApprovalRequestForm, on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.sender)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

class BudgetAllocation(models.Model):
    business_unit = models.ForeignKey(BusinessUnit, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class BudgetAllocationHistory(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('DEBIT', 'DEBIT'),
        ('CREDIT', 'CREDIT'),
    ]
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    budget_allocation = models.ForeignKey(BudgetAllocation, on_delete=models.CASCADE, related_name='history')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == 'DEBIT':
            if self.amount > self.budget_allocation.remaining_budget:
                raise ValueError("Insufficient budget")
            self.budget_allocation.remaining_budget -= self.amount
        elif self.transaction_type == 'CREDIT':
            self.budget_allocation.budget = self.amount
            self.budget_allocation.remaining_budget = self.amount
        self.budget_allocation.save()
        super().save(*args, **kwargs)
