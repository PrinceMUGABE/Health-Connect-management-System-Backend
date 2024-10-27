# models.py in trainingApp
from django.db import models
from django.conf import settings
from serviceApp.models import Service

class Training(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trainings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'service')

    def __str__(self):
        return f"{self.name} ({self.service.name if self.service else 'No Service'})"

class Module(models.Model):
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='modules')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.training.name}"

class TrainingMaterial(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='materials', null=True)
    file = models.FileField(upload_to='training_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Material for {self.module.name}"