from django.contrib import admin
from .models import User, BusinessUnit, Department, Designation, ApprovalRequestForm, ApprovalRequestItem, Approver, Notification, ApprovalLog
# Register your models here.

admin.site.register(User)
admin.site.register(BusinessUnit)
admin.site.register(Department)
admin.site.register(Designation)
admin.site.register(ApprovalRequestForm)
admin.site.register(ApprovalRequestItem)
admin.site.register(Approver)
admin.site.register(Notification)
admin.site.register(ApprovalLog)

