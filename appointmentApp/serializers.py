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
        fields = ['appointed_to', 'first_name', 'last_name', 'address', 'details']

    def create(self, validated_data):
        # Automatically assign 'created_by' to the logged-in user
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user

        return super().create(validated_data)

    def validate(self, data):
        # Ensure appointed_to (worker) is present and valid
        if 'appointed_to' not in data:
            raise serializers.ValidationError("You must select a worker.")
        if 'address' not in data:
            raise serializers.ValidationError("Address field is required.")
        return data
