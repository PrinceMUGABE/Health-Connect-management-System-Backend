from django.urls import path
from .views import get_exam_result, update_exam_result, delete_exam_result, create_exam_result, exam_result_list, get_user_exam_results,get_qualified_workers

urlpatterns = [
    path('results/', exam_result_list, name='exam-results'),
    path('create/', create_exam_result, name='create-exam-result'), 
    path('<int:pk>/', get_exam_result, name='get-exam-result'),
    path('update/<int:pk>/', update_exam_result, name='update-exam-result'),
    path('delete/<int:pk>/', delete_exam_result, name='delete-exam-result'),
    
    path('candidate/', get_user_exam_results, name='candidate-results'),
    path('service/<int:service_id>/', get_qualified_workers, name='workers-in-service'),

    
    
]