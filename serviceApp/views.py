from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Service
from .serializers import ServiceSerializer

# Create a Service
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_service(request):
    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get Service by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_service_by_id(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        serializer = ServiceSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

# Get Service by Name
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_service_by_name(request, name):
    try:
        service = Service.objects.get(name=name)
        serializer = ServiceSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

# Update a Service
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        if service.created_by != request.user:
            return Response({'error': 'You can only update your own services'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)

# Delete a Service
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        if service.created_by != request.user:
            return Response({'error': 'You can only delete your own services'}, status=status.HTTP_403_FORBIDDEN)
        
        service.delete()
        return Response({'message': 'Service deleted successfully'}, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_services(request):
    services = Service.objects.all()
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)