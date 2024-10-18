# serializers.py
from rest_framework import serializers
from .models import Candidate
from trainingApp.models import Training
from userApp.models import User



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']  # Adjust fields to match your User model


class TrainingSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    class Meta:
        model = Training
        fields = ['id', 'name', 'created_by', 'materials', 'created_at']




class CandidateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    training = TrainingSerializer(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'user', 'training', 'first_name', 'last_name', 'status', 'created_at']

