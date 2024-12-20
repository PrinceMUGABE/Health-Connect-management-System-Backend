from django.db import models
from django.conf import settings
from examApp.models import Exam
from trainingCandidateApp.models import Candidate

class ExamResult(models.Model):
    STATUS_CHOICES = [
        ('failed', 'Failed'),
        ('succeeded', 'Succeeded'),
    ]

    created_by = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    total_marks = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='failed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.created_by.user.phone} - {self.exam.training.name} - {self.status}"
