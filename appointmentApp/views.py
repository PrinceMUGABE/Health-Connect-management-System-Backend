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
# views.py
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import logging
from .models import Appointment
from communityHealthWorkApp.models import CommunityHealthWorker
from serviceApp.models import Service

# Set up logging
logger = logging.getLogger(__name__)

class CreateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract data from request
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            worker_id = request.data.get('worker')
            service_id = request.data.get('service')
            address = request.data.get('address')
            details = request.data.get('details')
            
            # Log received data for debugging
            logger.info(f"Received appointment data: {request.data}")
            
            # Validate required fields
            missing_fields = []
            if not first_name:
                missing_fields.append("First name")
            if not last_name:
                missing_fields.append("Last name")
            if not worker_id:
                missing_fields.append("Worker")
            if not service_id:
                missing_fields.append("Service")
            if not address:
                missing_fields.append("Address")
            if not details:
                missing_fields.append("Details")
                
            if missing_fields:
                error_msg = f"Missing required fields: {', '.join(missing_fields)}"
                logger.error(error_msg)
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate worker exists
            try:
                worker = get_object_or_404(CommunityHealthWorker, id=worker_id)
            except Exception as e:
                logger.error(f"Invalid worker ID: {worker_id}. Error: {str(e)}")
                return Response({"error": f"Worker with ID {worker_id} not found."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate service exists
            try:
                service = get_object_or_404(Service, id=service_id)
            except Exception as e:
                logger.error(f"Invalid service ID: {service_id}. Error: {str(e)}")
                return Response({"error": f"Service with ID {service_id} not found."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Set default due date to 7 days from now if not provided
            due_date = request.data.get('due_date')
            if not due_date:
                due_date = timezone.now() + timezone.timedelta(days=7)
                logger.info(f"Using default due date: {due_date}")
            
            # Check for duplicate appointments
            existing_appointments = Appointment.objects.filter(
                appointed_to=worker,
                first_name=first_name,
                last_name=last_name,
                due_date__date=timezone.datetime.strptime(due_date, '%Y-%m-%d').date() if isinstance(due_date, str) else due_date.date(),
                status='pending'
            )
            
            if existing_appointments.exists():
                logger.warning(f"Duplicate appointment attempt: {first_name} {last_name} with worker {worker_id} on {due_date}")
                return Response(
                    {"error": "An appointment with this worker on the same date already exists."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create a new appointment
            appointment = Appointment(
                created_by=request.user,
                appointed_to=worker,
                first_name=first_name,
                last_name=last_name,
                address=address,
                details=details,
                due_date=due_date,
                status='pending',
                service=service  # Assuming you have a service field in your model
            )
            
            appointment.save()
            
            logger.info(f"Appointment created successfully: ID {appointment.id} for {first_name} {last_name}.")
            return Response({
                "message": "Appointment created successfully.",
                "appointment_id": appointment.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.exception(f"Error creating appointment: {str(e)}")
            return Response({
                "error": f"An error occurred while creating the appointment: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Get Appointment by ID
class GetAppointmentByIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging

# Get your logger instance
logger = logging.getLogger(__name__)

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
        due_date = request.data.get("due_date")
        status_val = request.data.get("status")  # Renamed to avoid conflict with imported status

        logger.info(f"Extracted data - First Name: {first_name}, Last Name: {last_name}, Address: {address}, Details: {details}, Worker ID: {worker_id}, Due Date: {due_date}, Status: {status_val}")

        # Validate that the necessary fields are provided
        if not all([first_name, last_name, address, details, worker_id]):  # Removed due_date from the check as it might be optional
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
        
        if due_date:
            appointment.due_date = due_date
        
        # Update status if provided and valid
        if status_val and status_val in dict(Appointment.STATUS_CHOICES):
            appointment.status = status_val

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
            "due_date": appointment.due_date,
            "status": appointment.status,
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




# Add to views.py
class UpdateAppointmentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            appointment = get_object_or_404(Appointment, pk=pk)
            status_value = request.data.get('status')
            
            if not status_value or status_value not in dict(Appointment.STATUS_CHOICES):
                return Response({"error": "Valid status is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            appointment.status = status_value
            appointment.save()
            
            logger.info(f"Appointment {appointment.id} status updated to {status_value}.")
            return Response({"message": f"Appointment status updated to {status_value}."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.exception("An error occurred while updating appointment status: %s", e)
            return Response({"error": "An error occurred while updating appointment status."}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            
            
            
            
            
            
# Add to views.py
class GetAppointmentsByStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, status_value):
        if status_value not in dict(Appointment.STATUS_CHOICES):
            return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)
            
        appointments = Appointment.objects.filter(status=status_value)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    
    
    
    
    



