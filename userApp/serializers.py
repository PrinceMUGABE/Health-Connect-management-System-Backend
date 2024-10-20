from rest_framework import serializers
from .models import User
from base64 import b64encode, b64decode

class UserSerializer(serializers.ModelSerializer):
    # This serializer is for general user-related CRUD operations
    picture_data = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone', 'role', 'picture_data', 'created_at']

    def get_picture_data(self, obj):
        if obj.picture_data:
            return b64encode(obj.picture_data).decode('utf-8')  # Convert binary to base64 string
        return None


class UserSignupSerializer(serializers.ModelSerializer):
    # Used for user registration
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone', 'password', 'role', 'picture_data']

    def create(self, validated_data):
        # Handle picture_data as binary if provided
        picture = validated_data.pop('picture_data', None)
        if picture:
            validated_data['picture_data'] = picture.read()

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