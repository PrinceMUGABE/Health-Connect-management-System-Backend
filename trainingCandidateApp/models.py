from django.db import models
from django.utils import timezone
from communityHealthWorkApp.models import CommunityHealthWorker
from trainingApp.models import Training, Module

# Candidate model tracks individual candidates participating in trainings
class Candidate(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
    ]

    worker = models.ForeignKey(CommunityHealthWorker, on_delete=models.CASCADE, related_name='candidates', null=True)
    training = models.ForeignKey(Training, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    picture_data = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('worker', 'training')  # Ensure a worker registers for a training only once

    def __str__(self):
        return f'{self.worker} - {self.status}'

    def has_completed_training(self):
        """
        Check if the candidate has studied all modules in their assigned training.
        """
        total_modules = self.training.modules.count()
        studied_modules = self.module_progresses.filter(is_studied=True).count()
        return total_modules == studied_modules


# ModuleProgress model tracks individual module completion status for each candidate
class ModuleProgress(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="module_progresses")
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    is_studied = models.BooleanField(default=False)
    studied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('candidate', 'module')  # Ensure one progress entry per module per candidate

    def __str__(self):
        return f"{self.candidate} - {self.module.name} (Studied: {self.is_studied})"
