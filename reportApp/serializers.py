from rest_framework import serializers
from .models import Report
from userApp.models import User  # Import your custom User model
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at'] 

class ReportSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'created_by', 'activity', 'number', 'created_date']
