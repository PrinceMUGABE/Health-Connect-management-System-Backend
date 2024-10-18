from rest_framework import serializers
from .models import Training
from userApp.models import User  # Import your custom User model
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at'] 

class TrainingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    materials = serializers.FileField(required=False)  # Allow for optional file uploads

    class Meta:
        model = Training
        fields = ['id', 'created_by', 'name', 'materials', 'created_at']

    def to_representation(self, instance):
        logger.debug(f"Serializing training: {instance}")
        return super().to_representation(instance)
