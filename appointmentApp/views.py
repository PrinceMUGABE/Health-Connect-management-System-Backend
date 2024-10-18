from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Appointment, CommunityHealthWorker
from .serializers import AppointmentSerializer, CreateAppointmentSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# Create Appointment
class CreateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Get Appointment by ID
class GetAppointmentByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)


# Update Appointment
class UpdateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = CreateAppointmentSerializer(appointment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Appointment
class DeleteAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Get All Appointments
class GetAllAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        appointments = Appointment.objects.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# Get Appointments by Address
class GetAppointmentsByAddressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, address):
        appointments = Appointment.objects.filter(address__icontains=address)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# Get Appointments by First Name
class GetAppointmentsByFirstNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, first_name):
        appointments = Appointment.objects.filter(first_name__icontains=first_name)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# Get Appointments by Last Name
class GetAppointmentsByLastNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, last_name):
        appointments = Appointment.objects.filter(last_name__icontains=last_name)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# Get Appointments by Created By (Phone)
class GetAppointmentsByCreatedByView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, phone):
        user = get_object_or_404(User, phone=phone)
        appointments = Appointment.objects.filter(created_by=user)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


# Get Appointments by Appointed To (Community Health Worker)
class GetAppointmentsByAppointedToView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, worker_id):
        worker = get_object_or_404(CommunityHealthWorker, id=worker_id)
        appointments = Appointment.objects.filter(appointed_to=worker)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    
    
    
    
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Appointment
from communityHealthWorkApp.models import CommunityHealthWorker
from .serializers import AppointmentSerializer
import logging

logger = logging.getLogger(__name__)

class GetAppointmentsForLoggedInWorkerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the worker associated with the logged-in user
            worker = CommunityHealthWorker.objects.get(created_by=request.user)
            # Fetch appointments related to the worker
            appointments = Appointment.objects.filter(appointed_to=worker)
            serializer = AppointmentSerializer(appointments, many=True)
            logger.info("Appointments for worker fetched successfully.")
            return Response(serializer.data)
        except CommunityHealthWorker.DoesNotExist:
            logger.error(f"Worker not found for user: {request.user}")
            return Response({"error": "Worker not found"}, status=404)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": "An error occurred"}, status=500)
