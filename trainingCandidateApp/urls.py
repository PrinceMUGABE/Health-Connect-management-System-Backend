# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('candidates/', views.display_all_candidates, name='display_all_candidates'),
    path('create/', views.create_candidate, name='create_candidate'),
    path('<int:candidate_id>/', views.get_candidate_by_id, name='get_candidate_by_id'),
    path('update/<int:candidate_id>/', views.update_candidate, name='update_candidate'),
    path('delete/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'),
    path('training/', views.get_candidates_training, name='get_candidates_training'),
    path('my_trainings/', views.get_user_registered_trainings, name='get_user_registered_trainings'),
    path('candidate/<int:candidate_id>/modules/<int:module_id>/mark-as-studied/', views.mark_module_as_studied, name='mark_module_as_studied'),
    path('<int:candidate_id>/progress/', views.get_candidate_module_progress, name='get_candidate_module_progress'),
]
