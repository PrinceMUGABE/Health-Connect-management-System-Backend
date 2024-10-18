# models.py
from django.db import models
from trainingApp.models import Training
from django.conf import settings

class Candidate(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidates')
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    
    # New fields for first name and last name
    first_name = models.CharField(max_length=30, default='', null=True)
    last_name = models.CharField(max_length=30, default='', null=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'training')  # Ensure a user can register for a training only once

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.training.name} - {self.status}'
