# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from communityHealthWorkApp.models import CommunityHealthWorker

class Appointment(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_created')
    appointed_to = models.ForeignKey(CommunityHealthWorker, on_delete=models.CASCADE, related_name='appointments_assigned')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    details = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} Appointment'
