from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import RegisterUserView, ForgotPasswordView, BusinessUnitAPIView, DesignationAPIView, UserInfoView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'), 
    path('business-units/', BusinessUnitAPIView.as_view(), name='business-unit-list'),
    path('business-units/<int:pk>/', BusinessUnitAPIView.as_view(), name='business-unit-update'),
    path('designations/', DesignationAPIView.as_view(), name='designation-list'),
    path('designations/<int:pk>/', DesignationAPIView.as_view(), name='designation-update'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('userInfo/', UserInfoView.as_view(), name='userInfo'),
    path('userInfo/<int:pk>/', UserInfoView.as_view(), name='userInfo-update'),
    
]
