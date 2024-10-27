# serializers.py
from rest_framework import serializers
from .models import Candidate
from trainingApp.models import Training, TrainingMaterial
from userApp.models import User
from communityHealthWorkApp.models import CommunityHealthWorker
from base64 import b64encode, b64decode
from serviceApp.models import Service
import logging
from trainingApp.models import Module

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']  # Adjust fields to match your User model


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
      

class CommunityHealthWorkerSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = CommunityHealthWorker
        fields = ['id', 'created_by', 'first_name', 'middle_name', 'last_name', 'email', 'address', 'status', 'created_at']


        

    
    

class CandidateSerializer(serializers.ModelSerializer):
    worker = CommunityHealthWorkerSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'worker', 'training', 'status', 'picture_data', 'created_at']


    def get_picture_data(self, obj):
        if obj.picture_data:
            return b64encode(obj.picture_data).decode('utf-8')  # Convert binary to base64 string
        return None


