# views.py in trainingApp
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Training, Module, TrainingMaterial
from .serializers import TrainingSerializer, ModuleSerializer, TrainingMaterialSerializer
from serviceApp.models import Service
from .models import Module
from trainingCandidateApp.models import ModuleProgress


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_training(request):
    """
    Create a new training with the associated service.
    """
    name = request.data.get('name')
    service_id = request.data.get('service_id')

    if not name or not service_id:
        return Response({"error": "Both name and service_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({"error": "Service not found."}, status=status.HTTP_404_NOT_FOUND)

    if Training.objects.filter(service=service, name=name).exists():
        return Response({"error": "Training with this name already exists for the selected service."},
                        status=status.HTTP_400_BAD_REQUEST)

    training = Training.objects.create(
        name=name,
        service=service,
        created_by=request.user,
    )
    serializer = TrainingSerializer(training)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_module(request, training_id):
    """
    Creates a new module within a specific training.
    """
    try:
        training = Training.objects.get(pk=training_id)
    except Training.DoesNotExist:
        return Response({"error": "Training not found."}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()
    data['training'] = training.id  # Ensure this is set correctly

    # Debugging: Check the data being passed to the serializer
    print(f"Data before serialization: {data}")

    serializer = ModuleSerializer(data=data)
    if serializer.is_valid():
        module = serializer.save()  # Save the module

        if 'materials' in request.FILES:
            materials = request.FILES.getlist('materials')
            for material in materials:
                TrainingMaterial.objects.create(module=module, file=material)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Debugging: Check the serializer errors
    print(f"Serializer errors: {serializer.errors}")
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_material_to_module(request, module_id):
    """
    Uploads training materials to a specific module.
    """
    try:
        module = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        print('Module not found.')
        return Response({"error": "Module not found."}, status=status.HTTP_404_NOT_FOUND)

    files = request.FILES.getlist('materials')
    if not files:
        return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    for file in files:
        TrainingMaterial.objects.create(module=module, file=file)

    return Response({"message": "Materials uploaded successfully."}, status=status.HTTP_201_CREATED)




import logging
logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_training_by_id(request, pk):
    """
    Retrieve a training by its ID, including modules and candidate progress.
    """
    try:
        training = Training.objects.get(pk=pk)
        candidate_id = request.query_params.get('candidate_id')
        candidate_progress = {}

        # Fetch progress if candidate_id is provided
        if candidate_id:
            progress_qs = ModuleProgress.objects.filter(candidate_id=candidate_id, module__training=training)
            candidate_progress = {progress.module_id: progress.is_studied for progress in progress_qs}

        serializer = TrainingSerializer(training)
        training_data = serializer.data

        # Add progress information to each module
        for module in training_data.get('modules', []):
            module['is_completed'] = candidate_progress.get(module['id'], False)

        # Log the training data to the terminal
        logger.info("Training Data Retrieved: %s", training_data)

        return Response(training_data)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def get_all_trainings(request):
    """
    Retrieve all trainings.
    """
    trainings = Training.objects.all()
    serializer = TrainingSerializer(trainings, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_modules(request, training_id):
    """
    Retrieve all modules of a specific training.
    """
    try:
        training = Training.objects.get(pk=training_id)
        modules = training.modules.all()
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)
    except Training.DoesNotExist:
        return Response({"error": "Training not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_training(request, pk):
    """
    Update a training.
    """
    try:
        training = Training.objects.get(pk=pk)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = TrainingSerializer(training, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_module(request, module_id):
    """
    Update a specific module within a training.
    """
    try:
        module = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ModuleSerializer(module, data=request.data, partial=True)
    
    # Check if there are new materials in the request
    if 'materials' in request.FILES:
        # If there are new materials, delete existing materials
        module.materials.all().delete()

        # Save the new materials
        materials = request.FILES.getlist('materials')  # Get the list of files
        for material in materials:
            TrainingMaterial.objects.create(module=module, file=material)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_training(request, pk):
    """
    Delete a training by its ID.
    """
    try:
        training = Training.objects.get(pk=pk)
        training.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Training.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_module(request, module_id):
    """
    Delete a specific module within a training.
    """
    try:
        module = Module.objects.get(pk=module_id)
        module.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Module.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_modules_by_training(request, training_id):
    """
    Retrieve all modules associated with a specific training by training ID.
    """
    try:
        training = Training.objects.get(pk=training_id)
    except Training.DoesNotExist:
        return Response({"error": "Training not found."}, status=status.HTTP_404_NOT_FOUND)

    modules = training.modules.all()
    serializer = ModuleSerializer(modules, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




from rest_framework.generics import get_object_or_404

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_module_by_id(request, module_id):
    """
    Retrieve a specific module by its ID along with associated training materials.
    """
    try:
        module = Module.objects.get(pk=module_id)
    except Module.DoesNotExist:
        return Response({"error": "Module not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ModuleSerializer(module)
    return Response(serializer.data, status=status.HTTP_200_OK)
