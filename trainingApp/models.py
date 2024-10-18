from django.db import models
from django.conf import settings

class Training(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainigs')
    name = models.CharField(max_length=255)
    materials = models.FileField(upload_to='trainings/')  # This will create a folder for each training
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
