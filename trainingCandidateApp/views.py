import logging
import base64
import numpy as np
import cv2
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Candidate
from trainingApp.models import Training
from .serializers import CandidateSerializer
from rest_framework.permissions import IsAuthenticated
from communityHealthWorkApp.models import CommunityHealthWorker
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def is_high_quality(image):
    """Check if the image is of high enough resolution."""
    height, width = image.shape[:2]
    min_resolution = (200, 200)
    return width >= min_resolution[0] and height >= min_resolution[1]

def get_image_from_file(image_data):
    """Process image data from base64-decoded bytes."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    try:
        logger.debug(f"Processing image data of length: {len(image_data)}")
        
        # Convert bytes to numpy array
        try:
            file_array = np.frombuffer(image_data, np.uint8)
            logger.debug(f"Numpy array created: shape={file_array.shape}, dtype={file_array.dtype}")
        except Exception as e:
            logger.error(f"Failed to create numpy array: {str(e)}")
            return None, "Failed to process image data"

        # Decode image
        try:
            loaded_image = cv2.imdecode(file_array, cv2.IMREAD_COLOR)
            if loaded_image is None:
                logger.error("OpenCV failed to decode image")
                return None, "Invalid image format"
            logger.debug(f"Image decoded: shape={loaded_image.shape}")
        except Exception as e:
            logger.error(f"Failed to decode image: {str(e)}")
            return None, "Failed to decode image"

        # Check image quality
        try:
            if not is_high_quality(loaded_image):
                logger.error("Image failed quality check")
                return None, "Image resolution too low"
        except Exception as e:
            logger.error(f"Quality check error: {str(e)}")
            return None, "Failed to check image quality"

        # Detect faces
        try:
            faces = face_detector.detectMultiScale(loaded_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            logger.debug(f"Face detection complete: found {len(faces)} faces")
            
            if len(faces) > 1:
                return None, "Multiple faces detected"
            if len(faces) == 0:
                return None, "No face detected"
        except Exception as e:
            logger.error(f"Face detection error: {str(e)}")
            return None, "Failed to detect faces"

        logger.debug("Image processing completed successfully")
        return loaded_image, None

    except Exception as e:
        logger.error(f"Unexpected error in get_image_from_file: {str(e)}")
        logger.error(traceback.format_exc())
        return None, f"Image processing failed: {str(e)}"





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_candidate(request):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Log incoming request data
    logger.debug("=== Create Candidate Request Data ===")
    logger.debug(f"User ID: {request.user.id}")
    logger.debug(f"Content Type: {request.content_type}")
    logger.debug("Request Data Keys: " + ", ".join(request.data.keys()))
    
    training_id = request.data.get('training_id')
    image_data = request.data.get('image')
    
    # Debug image data
    if image_data:
        logger.debug(f"Image data type: {type(image_data)}")
        logger.debug(f"Image data length: {len(image_data) if image_data else 'None'}")
        logger.debug(f"Image data preview: {image_data[:100] if image_data else 'None'}")
    else:
        logger.error("No image data received")
        return Response({"detail": "Image data is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Get worker
    try:
        worker = CommunityHealthWorker.objects.get(created_by=request.user)
        logger.debug(f"Found worker: {worker.id}")
    except CommunityHealthWorker.DoesNotExist:
        logger.error(f"No worker found for user {request.user.id}")
        return Response({"detail": "Worker not found"}, status=status.HTTP_400_BAD_REQUEST)

    # Get training
    try:
        training = Training.objects.get(id=training_id)
        logger.debug(f"Found training: {training.id}")
    except Training.DoesNotExist:
        logger.error(f"Training not found: {training_id}")
        return Response({"detail": "Training not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check existing registration
    if Candidate.objects.filter(worker=worker, training=training).exists():
        logger.error("Duplicate registration attempt")
        return Response({"detail": "Already registered"}, status=status.HTTP_400_BAD_REQUEST)

    # Process image with detailed error handling
    try:
        logger.debug("Starting image processing")
        
        # Handle base64 prefix
        if isinstance(image_data, str):
            if image_data.startswith('data:image'):
                logger.debug("Removing base64 prefix")
                image_data = image_data.split('base64,')[1]
            
            try:
                logger.debug("Attempting base64 decode")
                decoded_image = base64.b64decode(image_data)
                logger.debug(f"Successfully decoded image, size: {len(decoded_image)} bytes")
            except Exception as e:
                logger.error(f"Base64 decode error: {str(e)}")
                return Response({"detail": "Invalid image encoding"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"Unexpected image data type: {type(image_data)}")
            return Response({"detail": "Invalid image format"}, status=status.HTTP_400_BAD_REQUEST)

        # Process image
        logger.debug("Calling get_image_from_file")
        submitted_image, error_message = get_image_from_file(decoded_image)
        
        if error_message:
            logger.error(f"Image processing error: {error_message}")
            return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)
        
        if submitted_image is None:
            logger.error("Image processing returned None without error message")
            return Response({"detail": "Image processing failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.debug("Image processed successfully")

        # Create candidate
        try:
            logger.debug("Creating candidate record")
            candidate = Candidate(
                worker=worker,
                training=training,
                picture_data=decoded_image,
                status='pending'
            )
            candidate.save()
            logger.debug(f"Candidate created successfully: {candidate.id}")

            serializer = CandidateSerializer(candidate)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return Response({"detail": "Failed to save candidate"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_candidate_by_id(request, candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        serializer = CandidateSerializer(candidate)
        return Response(serializer.data)
    except Candidate.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_candidates_training(request):
    try:
        candidates = Candidate.objects.filter(training__in=request.user.training_set.all())
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)




@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_candidate(request, candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        serializer = CandidateSerializer(candidate, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Candidate.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)







@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_candidate(request, candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
        candidate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Candidate.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def display_all_candidates(request):
    candidates = Candidate.objects.all()
    serializer = CandidateSerializer(candidates, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_registered_trainings(request):
    
    print(f'User found: {request.user}')
    
    worker = CommunityHealthWorker.objects.filter(created_by=request.user)
    print(f'Worker ID: {worker}')
    
    
    # Fetch all the Candidate records where the user matches the logged-in user
    candidates = Candidate.objects.filter(worker=worker.first())
    
    print(f'Candidate ID: {candidates}')

    
    # Serialize the Candidate data, which includes training details
    serializer = CandidateSerializer(candidates, many=True)
    # print(f'Serializer: {serializer}')
    # Return the serialized data as response
    return Response(serializer.data)







# views.py

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import ModuleProgress, Candidate
from trainingApp.models import Module
from userApp.models import User
from communityHealthWorkApp.models import CommunityHealthWorker

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_module_as_studied(request, candidate_id, module_id):
    # Get the logged-in user
    user = request.user

    # Fetch the CommunityHealthWorker for the logged-in user
    worker = get_object_or_404(CommunityHealthWorker, created_by=user)

    # Get the candidate using the candidate_id and verify it belongs to the worker
    candidate = get_object_or_404(Candidate, id=candidate_id, worker=worker)

    # Get the module using the module_id and ensure it belongs to the candidate's training
    module = get_object_or_404(Module, id=module_id, training=candidate.training)

    # Update or create a ModuleProgress entry for this candidate and module
    progress, created = ModuleProgress.objects.get_or_create(candidate=candidate, module=module)
    progress.is_studied = True
    progress.studied_at = timezone.now()
    progress.save()

    # Check if all modules are now completed for the training
    all_completed = candidate.has_completed_training()

    return JsonResponse({
        "module_id": module_id,
        "candidate_id": candidate_id,
        "all_modules_completed": all_completed
    })


# Add this function to views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_candidate_module_progress(request, candidate_id):
    try:
        # Verify the candidate belongs to the current user
        worker = get_object_or_404(CommunityHealthWorker, created_by=request.user)
        candidate = get_object_or_404(Candidate, id=candidate_id, worker=worker)
        
        # Get all module progress records for this candidate
        progress_records = ModuleProgress.objects.filter(candidate=candidate)
        
        # Format the data for the response
        progress_data = [{
            'id': record.id,
            'module': record.module.id,
            'module_name': record.module.name,
            'is_studied': record.is_studied,
            'studied_at': record.studied_at
        } for record in progress_records]
        
        return Response(progress_data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)