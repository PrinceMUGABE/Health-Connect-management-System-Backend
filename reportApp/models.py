# reportApp/models.py

from django.db import models
from django.conf import settings

class Report(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    activity = models.CharField(max_length=255)
    number = models.PositiveIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Report by {self.created_by} on {self.activity}'
