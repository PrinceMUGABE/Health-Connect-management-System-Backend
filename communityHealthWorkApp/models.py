# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class CommunityHealthWorker(models.Model):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='health_workers')
    first_name = models.CharField(max_length=50, default='')
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, default='')
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='accepted')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.status}'
