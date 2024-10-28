from django.urls import path

from .views import RequestLoanAPIView, SendLoanOtp, GetLoansAPIView, ApproveLoanAPIView, RejectLoanAPIView


urlpatterns = [
    path('request', RequestLoanAPIView.as_view(), name="request-loan"),
    path('send_otp', SendLoanOtp.as_view(), name="loan-otp"),

    # Admin Paths

    path('all', GetLoansAPIView.as_view(), name="all-loans"),
    path('approve/<str:id>', ApproveLoanAPIView.as_view(), name="approve-loan"),
    path('reject/<str:id>', RejectLoanAPIView.as_view(), name="reject-loan"),
]