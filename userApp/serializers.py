from rest_framework import serializers
from .models import User
from base64 import b64encode, b64decode

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'created_at']


class UserSignupSerializer(serializers.ModelSerializer):
    # Used for user registration
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'password', 'role']

    def create(self, validated_data):
       
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    # Serializer for user login
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ResetPasswordSerializer(serializers.Serializer):
    # Serializer for password reset
    phone = serializers.CharField()
    new_password = serializers.CharField(write_only=True)




from rest_framework import serializers

class ContactUsSerializer(serializers.Serializer):
    names = serializers.CharField(max_length=100, required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=True)