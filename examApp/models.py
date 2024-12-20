from django.db import models
from django.conf import settings
from trainingApp.models import Training  # Assuming the Training model is in the trainings app

class Exam(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exams')
    training = models.ForeignKey(Training, on_delete=models.CASCADE, related_name='exams')
    total_marks = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Exam for {self.training.name} by {self.created_by.phone}"


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)  # Marks for the question, summing up to 100

    def __str__(self):
        return f"Question: {self.text[:50]}... (Exam: {self.exam})"


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Choice: {self.text[:50]}... (Question: {self.question.text[:50]})"
