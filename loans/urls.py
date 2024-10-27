from django.urls import path

from .views import RequestLoanAPIView, SendLoanOtp


urlpatterns = [
    path('request', RequestLoanAPIView.as_view(), name="request-loan"),
    path('send_otp', SendLoanOtp.as_view(), name="loan-otp"),
]