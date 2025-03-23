# Create a new file called tasks.py
from django.utils import timezone
from .models import Appointment
import logging

logger = logging.getLogger(__name__)

def check_expired_appointments():
    """
    Check for appointments that have passed their due date while still in 'pending' status
    and mark them as 'cancelled'.
    """
    now = timezone.now()
    expired_appointments = Appointment.objects.filter(
        status='pending',
        due_date__lt=now
    )
    
    count = expired_appointments.count()
    if count > 0:
        expired_appointments.update(status='cancelled')
        logger.info(f"Automatically cancelled {count} expired appointments.")