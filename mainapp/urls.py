from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import RegisterUserView, ForgotPasswordView, BusinessUnitViewSet, DesignationViewSet, UserInfoView

router = DefaultRouter()
router.register(r'business-units', BusinessUnitViewSet)
router.register(r'designations', DesignationViewSet)

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login to get access & refresh token
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Get new access token using refresh token
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # Verify if a token is valid
    path('register/', RegisterUserView.as_view(), name='register'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('userInfo/', UserInfoView.as_view(), name='userInfo'),
]
