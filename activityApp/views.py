import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Activity
from .serializers import ActivitySerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_activity(request):
    logger.info("Received data for creating activity: %s", request.data)
    serializer = ActivitySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        logger.info("Activity created successfully: %s", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.error("Error creating activity: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_activities(request):
    activities = Activity.objects.all()
    serializer = ActivitySerializer(activities, many=True)
    logger.info("Returned all activities: %s", serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_activities_by_user(request):
    activities = Activity.objects.filter(created_by=request.user)
    serializer = ActivitySerializer(activities, many=True)
    logger.info("Returned activities for user %s: %s", request.user.id, serializer.data)
    return Response(serializer.data)

@api_view(['GET'])
def get_activity_by_id(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        serializer = ActivitySerializer(activity)
        logger.info("Returned activity %s: %s", activity_id, serializer.data)
        return Response(serializer.data)
    except Activity.DoesNotExist:
        logger.error("Activity not found: %s", activity_id)
        return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_activity(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        if activity.created_by != request.user:
            logger.warning("User %s attempted to edit activity %s without permission.", request.user.id, activity_id)
            return Response({'error': 'You do not have permission to edit this activity.'}, status=status.HTTP_403_FORBIDDEN)

        logger.info("Received data for updating activity %s: %s", activity_id, request.data)
        serializer = ActivitySerializer(activity, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Activity updated successfully: %s", serializer.data)
            return Response(serializer.data)
        logger.error("Error updating activity: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Activity.DoesNotExist:
        logger.error("Activity not found for update: %s", activity_id)
        return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_activity(request, activity_id):
    try:
        activity = Activity.objects.get(id=activity_id)
        if activity.created_by != request.user:
            logger.warning("User %s attempted to delete activity %s without permission.", request.user.id, activity_id)
            return Response({'error': 'You do not have permission to delete this activity.'}, status=status.HTTP_403_FORBIDDEN)

        activity.delete()
        logger.info("Activity deleted successfully: %s", activity_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    except Activity.DoesNotExist:
        logger.error("Activity not found for deletion: %s", activity_id)
        return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
