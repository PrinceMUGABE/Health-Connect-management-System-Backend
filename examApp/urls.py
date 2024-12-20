from django.urls import path, include
from .views import (
    create_exam, ExamViewSet, GetExamsByTrainingView, GetExamsByUserView,
    AddQuestionView, AddChoiceView, UpdateExamView, UpdateQuestionView,
    DeleteExamView, DeleteQuestionView, GetAllExamsView  # Import the new view
    
)

from rest_framework.routers import DefaultRouter
from .views import ExamViewSet

# Create a router and register the ExamViewSet
router = DefaultRouter()


urlpatterns = [
    path('create/', create_exam, name='create-exam'),
    path('<int:pk>/', ExamViewSet.as_view({'get': 'retrieve'}), name='get-exam-by-id'),
    path('training/<int:pk>/', GetExamsByTrainingView.as_view(), name='get-exam-by-training'),
    path('user/', GetExamsByUserView.as_view(), name='get-exams-by-user'),
    path('exams/', GetAllExamsView.as_view(), name='get-all-exams'),  # New URL for all exams
    path('update/<int:pk>/', UpdateExamView.as_view(), name='update-exam'),
    path('<int:exam_id>/add-question/', AddQuestionView.as_view(), name='add-question'),
    path('question/<int:question_id>/add-choice/', AddChoiceView.as_view(), name='add-choice'),
    path('question/update/<int:pk>/', UpdateQuestionView.as_view(), name='update-question'),
    path('delete/<int:pk>/', DeleteExamView.as_view(), name='delete-exam'),
    path('question/delete/<int:pk>/', DeleteQuestionView.as_view(), name='delete-question'),

    
]
