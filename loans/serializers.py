from rest_framework import serializers

from account_manager.utils import Util as manager_utils

from django.conf import settings

from datetime import datetime

db = settings.DB


class Loan(serializers.Serializer):
    ref_number = serializers.CharField(read_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    middle_name = serializers.CharField()
    amount = serializers.IntegerField()
    loan_type =  serializers.CharField() 
    account_manager_id = serializers.CharField(read_only=True)
    loan_currency = serializers.CharField(read_only=True)
    status =serializers.CharField(read_only=True)
    isApproved = serializers.CharField(read_only=True, default=False)
    loan_user_id = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    country = serializers.CharField()
    state_province = serializers.CharField()
    city = serializers.CharField()
    zip_code_postal_code = serializers.CharField()
    address = serializers.CharField()
    phone_number = serializers.CharField()
    marital_status = serializers.CharField()
    date_of_birth = serializers.CharField()
    city = serializers.CharField()
    isEmployed = serializers.BooleanField()
    employment_type = serializers.CharField()
    employer_name = serializers.CharField()
    employment_duration = serializers.CharField()
    job_title = serializers.CharField()
    annual_income_range = serializers.CharField()
    isBusinessOwner = serializers.BooleanField()
    application_date = serializers.CharField()
    amount_in_words = serializers.CharField()
    createdAt = serializers.CharField(read_only=True)


    def create(self, validated_data):
        validated_data["ref_number"] = manager_utils.generate_code()
        validated_data["createdAt"] = datetime.now()
        validated_data["isApproved"] = False
        validated_data["status"] = "Pending"
        return db.loans.insert_one(validated_data)
        
        

        


    
