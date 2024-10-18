# serializers.py
from rest_framework import serializers
from .models import Appointment
from communityHealthWorkApp.models import CommunityHealthWorker
from userApp.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']

class CommunityHealthWorkerSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = CommunityHealthWorker
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'status', 'created_by', 'created_at']

class AppointmentSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    appointed_to = CommunityHealthWorkerSerializer()

    class Meta:
        model = Appointment
        fields = ['id', 'created_by', 'appointed_to', 'first_name', 'last_name', 'address', 'details', 'created_date']

class CreateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['created_by', 'appointed_to', 'first_name', 'last_name', 'address', 'details']
    
    def validate(self, data):
        # Add custom validation logic if needed
        if 'address' not in data:
            raise serializers.ValidationError("Address field is required.")
        return data
