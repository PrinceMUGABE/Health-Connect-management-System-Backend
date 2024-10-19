from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ExamResult
from .serializers import ExamResultSerializer
from django.core.files.base import ContentFile
import face_recognition
import base64
import io
from django.core.files.images import ImageFile
from django.core.exceptions import ValidationError
from trainingCandidateApp.models import Candidate
from examApp.models import Exam


import base64
import cv2
import logging
import numpy as np
import face_recognition
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse

# face_recognition_app/views.py
import logging
import cv2
import numpy as np
import face_recognition
from django.shortcuts import render


# face_recognition_app/views.py
import logging
import cv2
import numpy as np
import face_recognition
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


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
        image.seek(0)  # Move to the beginning of the BytesIO object
        file_array = np.frombuffer(image.read(), np.uint8)  # Read bytes
        loaded_image = cv2.imdecode(file_array, cv2.IMREAD_COLOR)

        if loaded_image is None:
            logging.error("Image could not be loaded.")
            return None, None

        if not is_high_quality(loaded_image):
            logging.error("Image is too low quality.")
            return None, None

        faces = face_detector.detectMultiScale(loaded_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Check if multiple faces are detected first
        if len(faces) > 1:
            logging.error("Multiple faces detected in the image.")
            return None, "Multiple faces detected in the image."
        
        # Check if no faces are detected
        if len(faces) == 0:
            logging.error("No faces detected in the image.")
            return None, "No faces detected in the image."

        logging.info("Successfully loaded and validated image.")
        return loaded_image, None

    except Exception as e:
        logging.error(f"Failed to process image: {e}")
        return None, "Failed to decode submitted picture."

def compare_images_content(submitted_picture, existing_picture):
    """Compare the content of two images."""
    try:
        submitted_picture_rgb = cv2.cvtColor(submitted_picture, cv2.COLOR_BGR2RGB)
        existing_picture_rgb = cv2.cvtColor(existing_picture, cv2.COLOR_BGR2RGB)

        submitted_encodings = face_recognition.face_encodings(submitted_picture_rgb)
        existing_encodings = face_recognition.face_encodings(existing_picture_rgb)

        if not submitted_encodings or not existing_encodings:
            logging.error("Failed to encode faces in one or both pictures.")
            return 0.0

        distances = face_recognition.face_distance(existing_encodings, submitted_encodings[0])
        if len(distances) == 0:
            return 0.0

        best_match_score = 1 - min(distances)
        logging.info(f"Best match score: {best_match_score}")
        return best_match_score

    except Exception as e:
        logging.error(f"Error comparing images: {e}")
        return 0.0


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
import base64
import io


from datetime import timedelta
from django.utils import timezone  # To work with dates

from datetime import timedelta
from django.utils import timezone  # To work with dates

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_exam_result(request):
    logging.info("Received request to create exam result.")
    existing_result = None  # Initialize variable here to avoid reference before assignment
    candidate = None  # Initialize candidate variable
    try:
        # Extract and validate input data
        exam_id = request.data.get('exam')
        marks = request.data.get('marks')
        status_str = request.data.get('status')
        picture_data = request.data.get('image')

        if not exam_id or marks is None or not status_str or picture_data is None:
            logging.warning("Validation failed: All fields are required.")
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Decode the base64 string to bytes
        try:
            picture_data = base64.b64decode(picture_data)
        except Exception as e:
            logging.error(f"Failed to decode submitted picture: {e}")
            return Response({'error': 'Failed to decode submitted picture'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if exam exists
        try:
            exam = Exam.objects.get(id=exam_id)
            logging.info(f"Exam found: {exam_id}.")
        except Exam.DoesNotExist:
            logging.error(f"Exam with ID {exam_id} does not exist.")
            return Response({'error': 'Exam with the provided ID does not exist'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        logging.info(f"User: {user.phone}")

        # Get the candidate instance
        candidates = Candidate.objects.filter(user=user)
        if candidates.exists():
            candidate = candidates.first()  # Get the first candidate
            logging.info(f"Candidate found: {candidate.id}.")
        else:
            logging.error(f"Candidate for user {user.phone} does not exist.")
            return Response({'error': 'Candidate associated with the user does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the candidate already has a result for this exam
        try:
            existing_result = ExamResult.objects.filter(created_by=candidate, exam=exam).latest('created_at')
            logging.info(f"Found existing exam result for candidate {candidate.id} and exam {exam_id}.")
            
            # If the result status is 'succeeded', prevent saving new result
            if existing_result.status == 'succeeded':
                logging.warning("Candidate has already completed the training.")
                return Response({'error': 'You have already completed the training.'}, status=status.HTTP_400_BAD_REQUEST)

            # If the result status is 'failed', check the time difference between results
            if existing_result.status == 'failed':
                one_week_ago = timezone.now() - timedelta(weeks=2)
                
                if existing_result.created_at >= one_week_ago:
                    logging.warning("Candidate cannot retake the exam within a week of the last attempt.")
                    return Response({'error': 'You can only retake the exam after two weeks from the last failed attempt.'}, status=status.HTTP_400_BAD_REQUEST)
                
                logging.info("Candidate is eligible to retake the exam (more than one week has passed).")

        except ExamResult.DoesNotExist:
            logging.info("No existing result found for this candidate and exam. Proceeding with new result creation.")

        # Validate user picture data
        if user.picture_data is None or len(user.picture_data) == 0:
            logging.warning("Validation failed: User has no profile picture.")
            return Response({'error': 'User has no profile picture'}, status=status.HTTP_400_BAD_REQUEST)

        # Process the stored picture
        stored_image, stored_error = get_image_from_file(io.BytesIO(user.picture_data))
        if stored_image is None:
            logging.error(f"Error with stored picture: {stored_error}")
            return Response({'error': stored_error}, status=status.HTTP_400_BAD_REQUEST)

        logging.info("Stored picture processed successfully.")

        # Process the submitted image
        submitted_image, submitted_error = get_image_from_file(io.BytesIO(picture_data))
        if submitted_image is None:
            logging.error(f"Error with submitted picture: {submitted_error}")
            return Response({'error': submitted_error}, status=status.HTTP_400_BAD_REQUEST)

        logging.info("Submitted picture processed successfully.")

        # Compare pictures
        picture_match = compare_images_content(submitted_image, stored_image)

        logging.info(f'Images match score: {picture_match}')
        
        if picture_match >= 0.7:
            logging.info(f'Images match: True (Score: {picture_match})')

            # If existing result has 'failed' status, update it instead of creating a new one
            if existing_result and existing_result.status == 'failed':
                existing_result.total_marks = marks
                existing_result.status = status_str
                existing_result.save()
                logging.info(f"Exam result updated successfully for user: {user.phone}")
                return Response({'result': 'Exam result updated successfully', 'match_score': picture_match}, status=status.HTTP_200_OK)
            elif existing_result is None:  # No existing result found, create a new one
                # Save a new result
                result = ExamResult(
                    created_by=candidate,
                    exam=exam,
                    total_marks=marks,
                    status=status_str
                )
                result.save()
                logging.info(f"Exam result saved successfully for user: {user.phone}")
                return Response({'result': 'Success', 'match_score': picture_match}, status=status.HTTP_200_OK)
        else:
            logging.warning(f'Images match: False (Score: {picture_match})')
            return Response({'error': 'You are not the right person doing exam.', 'match_score': picture_match}, status=status.HTTP_403_FORBIDDEN)

    except Exception as e:
        logging.error(f"Error during image processing: {e}")
        return Response({'error': f'Error during image processing: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def exam_result_list(request):
    exam_results = ExamResult.objects.all()
    serializer = ExamResultSerializer(exam_results, many=True)
    return Response(serializer.data)






@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_exam_result(request, pk):
    try:
        exam_result = ExamResult.objects.get(pk=pk)
    except ExamResult.DoesNotExist:
        return Response({"error": "Exam result not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExamResultSerializer(exam_result)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_exam_result(request, pk):
    try:
        exam_result = ExamResult.objects.get(pk=pk)
    except ExamResult.DoesNotExist:
        return Response({"error": "Exam result not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExamResultSerializer(exam_result, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_exam_result(request, pk):
    try:
        exam_result = ExamResult.objects.get(pk=pk)
    except ExamResult.DoesNotExist:
        return Response({"error": "Exam result not found."}, status=status.HTTP_404_NOT_FOUND)

    exam_result.delete()
    return Response({"message": "Exam result deleted successfully."}, status=status.HTTP_204_NO_CONTENT)















from .serializers import ExamResultDetailSerializer
# Set up logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_exam_results(request):
    user = request.user  # Get the currently logged-in user
    logger.info(f"User {user.phone} is requesting their exam results.")  # Log user request

    try:
        # Fetch the candidates associated with the user
        candidates = Candidate.objects.filter(user=user)
        
        if not candidates.exists():
            logger.error(f"No candidates found for user {user.phone}.")
            return Response({'error': 'No candidates found for the logged-in user.'}, status=status.HTTP_404_NOT_FOUND)

        # Log the number of candidates found
        logger.info(f"Found {candidates.count()} candidates for user {user.phone}.")

        # If you want to consider the first candidate, you could do this:
        candidate = candidates.first()

        # Now fetch exam results for the candidate
        exam_results = ExamResult.objects.filter(created_by=candidate).select_related(
            'exam', 
            'exam__training', 
            'created_by'
        ).order_by('-created_at')  # Order by most recent results

        # Log the number of results found
        logger.info(f"Found {exam_results.count()} exam results for candidate {candidate.first_name} {candidate.last_name}.")

        # Serialize the exam results
        serializer = ExamResultDetailSerializer(exam_results, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("An error occurred while fetching exam results.")  # Log the exception
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    user = request.user  # Get the currently logged-in user
    logger.info(f"User {user.phone} is requesting their exam results.")  # Log user request

    try:
        # Fetch the candidate associated with the user
        try:
            candidate = Candidate.objects.get(user=user)
            logger.info(f"Found candidate: {candidate.first_name} {candidate.last_name} for user {user.phone}.")
        except Candidate.DoesNotExist:
            logger.error(f"Candidate not found for user {user.phone}.")
            return Response({'error': 'Candidate not found for the logged-in user.'}, status=status.HTTP_404_NOT_FOUND)

        # Now fetch exam results for the candidate
        exam_results = ExamResult.objects.filter(created_by=candidate).select_related(
            'exam', 
            'exam__training', 
            'created_by'
        ).order_by('-created_at')  # Order by most recent results

        # Log the number of results found
        logger.info(f"Found {exam_results.count()} exam results for candidate {candidate.first_name} {candidate.last_name}.")

        # Serialize the exam results
        serializer = ExamResultDetailSerializer(exam_results, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception("An error occurred while fetching exam results.")  # Log the exception
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  