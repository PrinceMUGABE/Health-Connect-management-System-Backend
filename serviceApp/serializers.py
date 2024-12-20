from rest_framework import serializers
from .models import Service
from userApp.models import User  # Import your custom User model
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']
        
        
class ServiceSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'created_by', 'name', 'created_at']
