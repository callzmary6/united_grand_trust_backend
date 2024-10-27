from rest_framework import generics, status

from authentication.permissions import IsAuthenticated
from .serializers import Loan
from authentication.utils import Util as auth_util

from django.conf import settings
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from datetime import datetime, timedelta

from united_sky_trust.base_response import BaseResponse

import re
import pymongo


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
            'to': user['email'],
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
            serializer.validated_data['account_manager_id'] = user['account_manager_id']
            serializer.validated_data['loan_currency'] = user['account_currency']

            serializer.save()

            return BaseResponse.response(status=True, message="Loan request successful", HTTP_STATUS=status.HTTP_200_OK)
        
        return BaseResponse.error_response(message='Auth pin is not correct!', status_code=status.HTTP_400_BAD_REQUEST)
    


# Admin Section for Loan

class GetLoansAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user['_id']
        entry = int(request.GET.get('entry', 10))
        page = int(request.GET.get('page', 1))
        search = request.GET.get('search', '')

        query = {'account_manager_id': user_id}

        if search:
            search_regex = re.compile(re.escape(search), re.IGNORECASE)
            query['$or'] = [
                {'first_name': search_regex},
                {'middle_name': search_regex},
                {'last_name': search_regex},
                {'amount': search_regex},
                {'loan_type': search_regex},
                {'status': search_regex},
            ]
        
        sorted_loans = db.loans.find(query, {'account_manager_id': 0}).sort('createdAt', pymongo.DESCENDING)

        paginator = Paginator(list(sorted_loans), entry)
        page_obj = paginator.get_page(page)

        new_loans = []

        for user in page_obj:
            user['_id'] = str(user['_id'])
            new_loans.append(user)

        total_loans = len(new_loans)
        
        data = {
            'loans': new_loans,
            'total_loans': total_loans,
            'current_page': page
        }

        return BaseResponse.response(
            status=True,
            HTTP_STATUS=status.HTTP_200_OK,
            data=data
        )
        
