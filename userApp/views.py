from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from health_connect_backend.settings import BASE_DIR
from .models import User  # Use your custom User model
from .serializers import UserSerializer, LoginSerializer, ResetPasswordSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout, login
import base64
import base64
import numpy as np
import cv2
import face_recognition
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
User = get_user_model()
# face_recognition_app/views.py
import logging
import cv2
import numpy as np
import face_recognition
from django.shortcuts import render

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Pre-trained face detector from OpenCV
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def is_high_quality(image):
    """Check if the image is of high enough resolution."""
    height, width = image.shape[:2]
    min_resolution = (200, 200)
    return width >= min_resolution[0] and height >= min_resolution[1]

def get_image_from_file(image):
    """Load an image from a bytes-like object and perform basic checks."""
    try:
        # Convert the uploaded image bytes to a numpy array
        file_array = np.frombuffer(image, np.uint8)
        loaded_image = cv2.imdecode(file_array, cv2.IMREAD_COLOR)

        if loaded_image is None:
            logging.error("Image could not be loaded.")
            return None, None

        if not is_high_quality(loaded_image):
            logging.error("Image is too low quality.")
            return None, None

        faces = face_detector.detectMultiScale(loaded_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Check the number of faces detected
        if len(faces) == 0:
            logging.error("No faces detected in the image.")
            return None, None
        elif len(faces) > 1:
            logging.error("Multiple faces detected in the image.")
            return None, None

        logging.info("Successfully loaded and validated image.")
        return loaded_image, faces

    except Exception as e:
        logging.error(f"Failed to process image: {e}")
        return None, None


import base64

@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
    phone = request.data.get('phone')
    password = request.data.get('password')
    role = request.data.get('role')
    

    errors = {}

    # Validate phone number
    if not phone:
        errors['phone'] = "Phone number is required."
    elif not (phone.startswith('072') or phone.startswith('078') or phone.startswith('073') or phone.startswith('079')) or len(phone) != 10:
        errors['phone'] = "Phone number must be 10 digits and start with 072, 078, 073, or 079."
    
    # Duplicate phone number check
    if User.objects.filter(phone=phone).exists():
        errors['phone'] = "This phone number already exists."

    # Validate password
    if not password:
        errors['password'] = "Password is required."
    elif len(password) < 8:
        errors['password'] = "Password must be at least 8 characters long."
    elif not (any(char.isdigit() for char in password) and 
              any(char.isupper() for char in password) and 
              any(char.islower() for char in password)):
        errors['password'] = "Password must contain at least one uppercase letter, one lowercase letter, and one digit."


    try: 
        # Save user
        hashed_password = make_password(password)
        user = User(
            phone=phone,
            role=role,
            password=hashed_password,
        )
        user.save()

        return Response({"message": "Account created successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






def is_high_quality(image):
    height, width = image.shape[:2]
    min_resolution = (200, 200)  # Minimum resolution for a high-quality image
    return width >= min_resolution[0] and height >= min_resolution[1]

def get_image_from_base64(picture_data):
    try:
        # Remove the "data:image/jpeg;base64," part if it exists
        if ',' in picture_data:
            picture_data = picture_data.split(',', 1)[1]
        picture_bytes = base64.b64decode(picture_data)
        submitted_image = cv2.imdecode(np.frombuffer(picture_bytes, np.uint8), cv2.IMREAD_COLOR)

        if submitted_image is None:
            message = 'Image data is not valid.'
            logging.error(message)
            return None, JsonResponse({'error': message}, status=400)

        if not is_high_quality(submitted_image):
            message = 'Image quality is too low. Please submit a higher quality image.'
            logging.error(message)
            return None, JsonResponse({'error': message}, status=400)

        # Face detection using Haar Cascade Classifier
        faces = face_detector.detectMultiScale(submitted_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            message = 'No faces detected in the image. Please submit a picture with a face.'
            logging.error(message)
            return None, JsonResponse({'error': message}, status=400)
        elif len(faces) > 1:
            message = 'Multiple faces detected. Please submit a picture with only one person.'
            logging.error(message)
            return None, JsonResponse({'error': message}, status=400)

        return submitted_image, None

    except Exception as e:
        logging.error(f"Failed to decode base64 image: {e}")
        return None, JsonResponse({'error': 'Failed to decode base64 image'}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    print("Received login request:", request.data)  # Debugging print
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']

        if not phone:
            return Response({'error': 'Phone is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            login(request, user)

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_info = {
                'id': user.id,
                'phone': user.phone,
                'role': user.role,
                'access_token': access_token,
                'refresh_token': refresh_token,
            }
            print(f'\n\nUser logged in successfully as {user.role}\n\n')  # Debugging print
            return Response(user_info, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Get user by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, user_id):
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Get all users
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Update or delete user by ID
@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update_delete_user(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


# Get user profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


import logging
import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from userApp.models import User
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist  # Import this for exception handling

# Configure logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    logger.info("Received request to reset password.")

    # Manually get data from the request
    phone = request.data.get('phone')
    new_password = request.data.get('new_password')

    logger.debug(f"Phone: {phone}, New Password: {new_password}")

    # Validate the phone number
    if not phone or not re.match(r'^(078|079|072|073)\d{7}$', phone):
        logger.error("Invalid phone number format.")
        return JsonResponse({
            'error': 'Phone number must be exactly 10 digits and start with 078, 079, 072, or 073.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate the new password
    if not new_password:
        logger.error("New password is missing.")
        return JsonResponse({'error': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)

    if (len(new_password) < 5 or 
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password) or
        not re.search(r'[A-Z]', new_password) or
        not re.search(r'[a-z]', new_password) or
        not re.search(r'\d', new_password)):
        logger.error("Password validation failed.")
        return JsonResponse({
            'error': 'Password must be at least 5 characters long, contain a special character, an uppercase letter, a lowercase letter, and a number.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Find the user by phone
        user = User.objects.get(phone=phone)
    except ObjectDoesNotExist:
        logger.error("User with the provided phone number does not exist.")
        return JsonResponse({'error': 'Phone number not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Proceed to set the new password
    user.set_password(new_password)
    user.save()
    logger.info("Password reset successfully for user: %s", phone)

    return JsonResponse({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)





import logging
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ContactUsSerializer
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status

# Configure logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
def contact_us(request):
    logger.info("Received contact request with data: %s", request.data)
    
    serializer = ContactUsSerializer(data=request.data)
    
    if serializer.is_valid():
        names = serializer.validated_data['names']
        email = serializer.validated_data['email']
        subject = serializer.validated_data['subject']
        description = serializer.validated_data['description']
        
        # Check for empty fields
        if not names.strip():
            logger.error("Name field is empty.")
            return Response({"error": "Name field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not subject.strip():
            logger.error("Subject field is empty.")
            return Response({"error": "Subject field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)
        if not description.strip():
            logger.error("Description field is empty.")
            return Response({"error": "Description field cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            logger.error("Invalid email format: %s", email)
            return Response({"error": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST)

        # Sending email
        try:
            send_mail(
                subject=f"Contact Us: {subject}",
                message=f"Name: {names}\nEmail: {email}\n\nDescription:\n{description}",
                from_email=email,
                recipient_list=['harerimanaclementkella@gmail.com'],
                fail_silently=False,
            )
            logger.info("Email sent successfully to %s", email)
            return Response({"message": "Email sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("An error occurred while sending email: %s", e)
            return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.error("Invalid serializer data: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from .models import User

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    phone = request.data.get('phone')
    role = request.data.get('role')

    errors = {}

    # Validate phone number
    if not phone:
        errors['phone'] = "Phone number is required."
    elif not (phone.startswith('072') or phone.startswith('078') or phone.startswith('073') or phone.startswith('079')) or len(phone) != 10:
        errors['phone'] = "Phone number must be 10 digits and start with 072, 078, 073, or 079."
    
    # Duplicate phone number check
    if User.objects.filter(phone=phone).exists():
        errors['phone'] = "This phone number already exists."

    if errors:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    try:

        # Save user
        user = User(
            phone=phone,
            role=role
        )
        user.save()

        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
