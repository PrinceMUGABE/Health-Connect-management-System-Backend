from django.db import models
from django.conf import settings
from django.utils import timezone
from communityHealthWorkApp.models import CommunityHealthWorker
from serviceApp.models import Service

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_created')
    appointed_to = models.ForeignKey(CommunityHealthWorker, on_delete=models.CASCADE, related_name='appointments_assigned')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments', null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    details = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        # Add unique constraint to prevent duplicate appointments
        constraints = [
            models.UniqueConstraint(
                fields=['appointed_to', 'first_name', 'last_name', 'due_date'],
                name='unique_appointment'
            )
        ]

    def __str__(self):
        return f'{self.first_name} {self.last_name} Appointment with {self.appointed_to}'
    
    def save(self, *args, **kwargs):
        # If due_date is not set, default to 7 days from now
        if not self.due_date:
            self.due_date = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)