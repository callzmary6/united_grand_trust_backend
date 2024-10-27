from rest_framework import generics, status

from authentication.permissions import IsAuthenticated
from .serializers import Loan
from authentication.utils import Util as auth_util

from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime, timedelta

from united_sky_trust.base_response import BaseResponse


db = settings.DB


class SendLoanOtp(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        otp = auth_util.generate_number(6) 

        context = {
            'customer_name': user['first_name'],
            'otp': otp
        }

        data = {
            'to': user["email"],
            'body': 'Use this otp to verify your transaction',
            'subject': 'Verify Transaction',
            'html_template': render_to_string('loan-otp.html', context)
        }  

        expire_at = datetime.now() + timedelta(seconds=600)
        db.otp_codes.insert_one({'user_id': user['_id'], 'code': otp, 'expireAt': expire_at})

        auth_util.email_send(data)

        return BaseResponse.response(status=True, message='Opt sent successfully', HTTP_STATUS=status.HTTP_200_OK)


class RequestLoanAPIView(generics.GenericAPIView):
    serializer_class = Loan
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        user = request.user
        data = request.data
        otp = data["otp_code"]
        auth_pin = data["auth_pin"]

        otp_code = db.otp_codes.find_one({'user_id': user['_id'], 'code': otp})
        
        serializer = self.serializer_class(data=data, partial=True)
        serializer.is_valid(raise_exception=True)

        if user['isVerified'] == False:
            return BaseResponse.error_response(message='Loan request failed, Email is not verified!', status_code=status.HTTP_400_BAD_REQUEST)

        if user['isSuspended'] == True:
            return BaseResponse.error_response(message='Loan request failed, Account is suspended!', status_code=status.HTTP_400_BAD_REQUEST)
        
        if user['isTransferBlocked'] == True:
            return BaseResponse.error_response(message='Loan request failed, Transfer is blocked for this user!', status_code=status.HTTP_400_BAD_REQUEST)
        
        if otp_code is None:
            return BaseResponse.error_response(message='Code is invalid!', status_code=status.HTTP_400_BAD_REQUEST)
        

        if otp != otp_code['code']:
            return BaseResponse.error_response(message='Otp is not correct!', status_code=status.HTTP_400_BAD_REQUEST)  
        
        db.otp_codes.delete_many({})

        if user["auth_pin"] == auth_pin:
        
            serializer.validated_data["first_name"] = user["first_name"]
            serializer.validated_data["last_name"] = user["last_name"]
            serializer.validated_data["middle_name"] = user["middle_name"]
            serializer.validated_data["email"] = user["email"]

            serializer.save()

            return BaseResponse.response(status=True, message="Loan request successful", HTTP_STATUS=status.HTTP_200_OK)
        
        return BaseResponse.error_response(message='Auth pin is not correct!', status_code=status.HTTP_400_BAD_REQUEST)
        
