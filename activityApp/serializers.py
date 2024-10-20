from rest_framework import serializers
from .models import Activity
from userApp.models import User
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at'] 

class ActivitySerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    class Meta:
        model = Activity
        fields = ['id', 'created_by', 'name', 'created_at']
