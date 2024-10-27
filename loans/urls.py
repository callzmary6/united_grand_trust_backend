from django.urls import path

from .views import RequestLoanAPIView, SendLoanOtp, GetLoansAPIView


urlpatterns = [
    path('request', RequestLoanAPIView.as_view(), name="request-loan"),
    path('send_otp', SendLoanOtp.as_view(), name="loan-otp"),

    # Admin Paths

    path('all', GetLoansAPIView.as_view(), name="all-loans"),
]