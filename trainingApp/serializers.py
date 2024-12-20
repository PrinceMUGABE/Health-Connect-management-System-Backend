# serializers.py in trainingApp
from rest_framework import serializers
from .models import Training, Module, TrainingMaterial
from userApp.models import User
from serviceApp.models import Service
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'created_at']

class TrainingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingMaterial
        fields = ['id', 'file', 'uploaded_at']

class ModuleSerializer(serializers.ModelSerializer):
    materials = TrainingMaterialSerializer(many=True, read_only=True)  # Nested materials
    

    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'training', 'materials', 'created_at']

class TrainingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), write_only=True)
    modules = ModuleSerializer(many=True, read_only=True)  # Nested modules

    class Meta:
        model = Training
        fields = ['id', 'created_by', 'service', 'service_id', 'name', 'modules', 'created_at']

    def to_representation(self, instance):
        logger.debug(f"Serializing training: {instance}")
        return super().to_representation(instance)
    
    
    
    
    
    
    
    
    
    
    
    
