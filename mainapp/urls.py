from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import RegisterUserView, ForgotPasswordView, BusinessUnitAPIView, DepartmentAPIView, DesignationAPIView, UserInfoView, ApprovalRequestFormAPIView, ApprovalRequestItemAPIView, PendingApprovalsAPIView, ApprovalApproveRejectView, ApprovalLogListView, ApproverAPIView, NotificationAPIView, ApprovalRequestCategoryAPIView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'), 
    path('business-units/', BusinessUnitAPIView.as_view(), name='business-unit-list'),
    path('business-units/<int:pk>/', BusinessUnitAPIView.as_view(), name='business-unit-update'),
    path('designations/', DesignationAPIView.as_view(), name='designation-list'),
    path('designations/<int:pk>/', DesignationAPIView.as_view(), name='designation-update'),
    path('departments/', DepartmentAPIView.as_view(), name='department-list'),
    path('departments/<int:pk>/', DepartmentAPIView.as_view(), name='department-update'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('userInfo/', UserInfoView.as_view(), name='userInfo'),
    path('userInfo/<int:pk>/', UserInfoView.as_view(), name='userInfo-update'),
    path('approver/', ApproverAPIView.as_view(), name='approver'),
    path('approval-request-category/', ApprovalRequestCategoryAPIView.as_view(), name='approver-request-category'),
    path('approval-requests/', ApprovalRequestFormAPIView.as_view(), name='approval-requests'),
    path('approval-requests/<int:pk>/', ApprovalRequestFormAPIView.as_view(), name='approval-requests'),
    path('approval-items/', ApprovalRequestItemAPIView.as_view(), name='approval-items'),
    path('approval-requests/<int:pk>/<str:action>/', ApprovalApproveRejectView.as_view(), name='approval-requests-approve-reject'),
    path('approval-logs/', ApprovalLogListView.as_view(), name='approval-logs-list'),
    path('pending-approvals/', PendingApprovalsAPIView.as_view(), name='pending-approvals'),
    path('notifications/', NotificationAPIView.as_view(), name='notifications'),
]
