from .serializers import CreateAppointmentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Appointment, CommunityHealthWorker
from django.contrib.auth import get_user_model
import logging

User = get_user_model()

# Set up logger
logger = logging.getLogger(__name__)

# Create Appointment
class CreateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Manually extract data from request
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            worker_id = request.data.get('worker')  # Assuming you are sending the worker's ID
            address = request.data.get('address')
            details = request.data.get('details')
            materials = request.FILES.get('materials')  # Handle file upload if needed

            # Validate required fields
            if not first_name or not last_name or not worker_id or not address or not details:
                logger.error("Validation error: All fields are required.")
                return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

            # Validate that the worker exists
            worker = get_object_or_404(CommunityHealthWorker, id=worker_id)

            # Create a new appointment
            appointment = Appointment(
                created_by=request.user,  # Assuming you want to set the user creating the appointment
                appointed_to=worker,  # Set the appointed_to field
                first_name=first_name,
                last_name=last_name,
                address=address,
                details=details,
                # materials = materials,  # Uncomment if you have a field for materials in Appointment model
            )
            
            appointment.save()  # Save the appointment to the database

            logger.info(f"Appointment created successfully: {appointment.id} for {first_name} {last_name}.")
            return Response({"message": "Appointment created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("An error occurred while creating the appointment: %s", e)
            return Response({"error": "An error occurred while creating the appointment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Get Appointment by ID
class GetAppointmentByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)


class UpdateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        # Retrieve the appointment object
        appointment = get_object_or_404(Appointment, pk=pk)

        # Log the request data for debugging
        logger.info(f"Request data: {request.data}")

        # Extract data manually from the request
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        address = request.data.get("address")
        details = request.data.get("details")
        worker_id = request.data.get("worker")

        logger.info(f"Extracted data - First Name: {first_name}, Last Name: {last_name}, Address: {address}, Details: {details}, Worker ID: {worker_id}")

        # Validate that the necessary fields are provided
        if not all([first_name, last_name, address, details, worker_id]):
            logger.error("Missing required fields in the request.")
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the worker object and handle any errors
        try:
            worker = CommunityHealthWorker.objects.get(id=worker_id)
        except CommunityHealthWorker.DoesNotExist:
            logger.error(f"Worker with ID {worker_id} not found.")
            return Response({"error": "Worker not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the appointment object
        appointment.first_name = first_name
        appointment.last_name = last_name
        appointment.address = address
        appointment.details = details
        appointment.appointed_to = worker

        # Save the updated appointment
        appointment.save()

        # Log the successful update
        logger.info(f"Appointment {appointment.id} updated successfully.")

        # Return the updated data
        return Response({
            "id": appointment.id,
            "first_name": appointment.first_name,
            "last_name": appointment.last_name,
            "address": appointment.address,
            "details": appointment.details,
            "appointed_to": {
                "id": worker.id,
                "first_name": worker.first_name,
                "last_name": worker.last_name,
                "email": worker.email,
                "address": worker.address
            }
        }, status=status.HTTP_200_OK)
        
        
        

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
            user = request.user
            print(f'\nFound user is : {user.phone}\n\n')
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





class GetAppointmentsForLoggedInUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the worker associated with the logged-in user
            # worker = CommunityHealthWorker.objects.get(created_by=request.user)
            # Fetch appointments related to the worker
            appointments = Appointment.objects.filter(created_by=request.user)
            serializer = AppointmentSerializer(appointments, many=True)
            logger.info("Appointments for worker fetched successfully.")
            return Response(serializer.data)
        except CommunityHealthWorker.DoesNotExist:
            logger.error(f"Worker not found for user: {request.user}")
            return Response({"error": "Worker not found"}, status=404)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({"error": "An error occurred"}, status=500)






