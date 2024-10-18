# serializers.py
from rest_framework import serializers
from userApp.models import User
from .models import CommunityHealthWorker

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']

class CommunityHealthWorkerSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)  # Nested serializer for full user info

    class Meta:
        model = CommunityHealthWorker
        fields = ['id', 'created_by', 'first_name', 'middle_name', 'last_name', 'email', 'address', 'status', 'created_at']
