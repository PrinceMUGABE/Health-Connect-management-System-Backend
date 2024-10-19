from rest_framework import serializers
from .models import Activity
from userApp.models import User  # Import your custom User model
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        created_by = ['id', 'phone', 'role', 'created_at'] 

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'created_by', 'name', 'created_at']
