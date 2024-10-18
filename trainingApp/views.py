from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Training
from .serializers import TrainingSerializer
import os
from django.conf import settings


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_training(request):
    serializer = TrainingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)  # Associate the training with the logged-in user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_training_by_id(request, pk):
    try:
        training = Training.objects.get(pk=pk)
        serializer = TrainingSerializer(training)
        return Response(serializer.data)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def get_all_trainings(request):
    trainings = Training.objects.all()
    serializer = TrainingSerializer(trainings, many=True)
    return Response(serializer.data)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_training(request, pk):
    try:
        training = Training.objects.get(pk=pk)
        serializer = TrainingSerializer(training, data=request.data, partial=True)

        # If files are provided, use them
        if 'materials' in request.FILES:
            training.materials = request.FILES['materials']

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_training(request, pk):
    try:
        training = Training.objects.get(pk=pk)
        training.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_training_materials(request):
    training_id = request.data.get('training_id')
    materials = request.FILES.get('materials')

    if training_id is None or materials is None:
        return Response({"error": "training_id and materials are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        training = Training.objects.get(pk=training_id)

        # Ensure the materials are saved in the training folder
        training.materials.save(os.path.join(f'trainings/{training.name}/', materials.name), materials)

        return Response({"message": "Materials uploaded successfully."}, status=status.HTTP_201_CREATED)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
