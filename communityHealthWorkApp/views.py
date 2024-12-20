# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import CommunityHealthWorker
from .serializers import CommunityHealthWorkerSerializer

# views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import CommunityHealthWorker
from .serializers import CommunityHealthWorkerSerializer


# Create a new Community Health Worker with validation to prevent duplicates and send email if provided
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_worker(request):
    data = request.data

    # Check if a worker with the same first_name, last_name, and email exists (can also add address or other fields)
    existing_worker = CommunityHealthWorker.objects.filter(
        first_name=data.get('first_name').strip(),
        last_name=data.get('last_name').strip(),
        email=data.get('email').strip() if data.get('email') else None
    ).first()

    if existing_worker:
        return Response(
            {"error": "A worker with this first name, last name, and email already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create the worker if no duplicate found
    worker = CommunityHealthWorker.objects.create(
        created_by=request.user,
        first_name=data.get('first_name').strip(),
        middle_name=data.get('middle_name', '').strip(),
        last_name=data.get('last_name').strip(),
        email=data.get('email').strip() if data.get('email') else None,
        address=data.get('address').strip(),
        status='accepted'  # Default status
    )

    # Send email if the user provided an email address
    if worker.email:
        send_welcome_email(worker)

    # Serialize and return response
    serializer = CommunityHealthWorkerSerializer(worker)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Helper function to send the welcome email
def send_welcome_email(worker):
    subject = "Welcome to the Community Health Work Empowering System"
    message = f"""
    Hello {worker.first_name},

    You have joined as a Health Worker to the Community Health Work Empowering System.

    If you did not create this account, kindly contact +250788457408 immediately for support.

    Your best regards!
    """
    from_email = settings.DEFAULT_FROM_EMAIL  # Make sure to set this in your settings.py
    recipient_list = [worker.email]

    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        fail_silently=False,  # Raise an error if the email fails to send
    )





# Get a worker by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_worker_by_id(request, id):
    try:
        worker = CommunityHealthWorker.objects.get(id=id)
        serializer = CommunityHealthWorkerSerializer(worker)
        return Response(serializer.data)
    except CommunityHealthWorker.DoesNotExist:
        return Response({'detail': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)

# Get all workers
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_workers(request):
    workers = CommunityHealthWorker.objects.all()
    serializer = CommunityHealthWorkerSerializer(workers, many=True)
    return Response(serializer.data)

# Get workers by first name
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workers_by_firstname(request, firstname):
    workers = CommunityHealthWorker.objects.filter(first_name__icontains=firstname)
    serializer = CommunityHealthWorkerSerializer(workers, many=True)
    return Response(serializer.data)

# Get workers by last name
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workers_by_lastname(request, lastname):
    workers = CommunityHealthWorker.objects.filter(last_name__icontains=lastname)
    serializer = CommunityHealthWorkerSerializer(workers, many=True)
    return Response(serializer.data)

# Get workers by address
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_workers_by_address(request, address):
    workers = CommunityHealthWorker.objects.filter(address__icontains=address)
    serializer = CommunityHealthWorkerSerializer(workers, many=True)
    return Response(serializer.data)

# Update a worker by ID
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_worker(request, id):
    try:
        worker = CommunityHealthWorker.objects.get(id=id)
        data = request.data
        worker.first_name = data.get('first_name', worker.first_name)
        worker.middle_name = data.get('middle_name', worker.middle_name)
        worker.last_name = data.get('last_name', worker.last_name)
        worker.email = data.get('email', worker.email)
        worker.address = data.get('address', worker.address)
        worker.status = data.get('status', worker.status)
        worker.save()
        serializer = CommunityHealthWorkerSerializer(worker)
        return Response(serializer.data)
    except CommunityHealthWorker.DoesNotExist:
        return Response({'detail': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)

# Soft delete a worker (change status to 'rejected')
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_worker(request, id):
    try:
        worker = CommunityHealthWorker.objects.get(id=id)
        worker.status = 'rejected'  # Soft delete by changing status
        worker.save()
        return Response({'detail': 'Worker status updated to rejected'}, status=status.HTTP_200_OK)
    except CommunityHealthWorker.DoesNotExist:
        return Response({'detail': 'Worker not found'}, status=status.HTTP_404_NOT_FOUND)



# New view to get the logged-in user's worker information
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_logged_in_worker_info(request):
    try:
        # Get the worker associated with the logged-in user
        worker = CommunityHealthWorker.objects.get(created_by=request.user)
        serializer = CommunityHealthWorkerSerializer(worker)
        return Response(serializer.data)
    except CommunityHealthWorker.DoesNotExist:
        return Response({'detail': 'Worker not found for this user'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)