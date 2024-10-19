# reportApp/views.py

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Report
from .serializers import ReportSerializer

logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_report(request):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)  # Automatically set created_by to the logged-in user
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_report_by_id(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        serializer = ReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Report.DoesNotExist:
        return Response({'error': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_report_by_id(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        if report.created_by != request.user:
            return Response({'error': 'You do not have permission to update this report.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ReportSerializer(report, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Report.DoesNotExist:
        return Response({'error': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_report_by_id(request, report_id):
    try:
        report = Report.objects.get(id=report_id)
        if report.created_by != request.user:
            return Response({'error': 'You do not have permission to delete this report.'}, status=status.HTTP_403_FORBIDDEN)
        
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    except Report.DoesNotExist:
        return Response({'error': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_reports(request):
    reports = Report.objects.all()
    serializer = ReportSerializer(reports, many=True)
    
    # Log the retrieved data
    logger.info(f"Retrieved reports for user {request.user.id}: {serializer.data}")
    
    return Response(serializer.data, status=status.HTTP_200_OK)






# reportApp/views.py



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_user(request):
    reports = Report.objects.filter(created_by=request.user)
    serializer = ReportSerializer(reports, many=True)

    # Log the retrieved data
    logger.info(f"Retrieved reports for user {request.user.id}: {serializer.data}")

    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_reports_by_activity(request, activity):
    reports = Report.objects.filter(activity=activity)
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)