from django.urls import path, re_path
from .views import KeywordDataView, SendOTPView, LoginView, VerifyOTPView, signup, process_payment
from accounts import views
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('api/keyword/<str:url>/', KeywordDataView.as_view(), name='get_keyword_data'),
    path('api/otp/', SendOTPView.as_view(), name='otp'),
    # path('api/verify-otp/', views.verify_otp, name='verify_otp'),
    path('api/signup/', signup, name='signup'),  # Define the path and view function
    path('request-password-reset/', views.request_password_reset, name='request_password_reset'),
   path('reset-password/', views.reset_password, name='reset_password'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/process-payment/', process_payment, name='process_payment'),
     path('api/check-subscription/', views.check_user_subscription, name='check_subscription'),


]
