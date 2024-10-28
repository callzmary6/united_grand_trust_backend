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
    createdAt = serializers.CharField(read_only=True)


    def create(self, validated_data):
        validated_data["ref_number"] = manager_utils.generate_code()
        validated_data["createdAt"] = datetime.now()
        validated_data["isApproved"] = False
        validated_data["status"] = "Pending"
        return db.loans.insert_one(validated_data)
        
        

        


    
