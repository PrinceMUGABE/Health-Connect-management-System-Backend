# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Candidate
from trainingApp.models import Training
from .serializers import CandidateSerializer
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_candidate(request):
    training_id = request.data.get('training_id')
    firstname = request.data.get('first_name')
    lastname = request.data.get('last_name')

    if not training_id:
        return Response({"detail": "Training ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user has already registered for the training
    if Candidate.objects.filter(user=request.user, training__id=training_id).exists():
        return Response({"detail": "You are already registered for this training."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        training = Training.objects.get(id=training_id)
    except Training.DoesNotExist:
        return Response({"detail": "Training not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create the candidate with user details
    candidate = Candidate(
        user=request.user,
        training=training,
        first_name=firstname,
        last_name=lastname
    )
    candidate.save()
    serializer = CandidateSerializer(candidate)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




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
    # Fetch all the Candidate records where the user matches the logged-in user
    candidates = Candidate.objects.filter(user=request.user)
    
    # Serialize the Candidate data, which includes training details
    serializer = CandidateSerializer(candidates, many=True)
    
    # Return the serialized data as response
    return Response(serializer.data)