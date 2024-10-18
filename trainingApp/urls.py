from django.urls import path
from .views import (
    create_training,
    get_training_by_id,
    get_all_trainings,
    update_training,
    delete_training,
    upload_training_materials,
)

urlpatterns = [
    path('create/', create_training, name='create_training'),
    path('<int:pk>/', get_training_by_id, name='get_training_by_id'),
    path('trainings/', get_all_trainings, name='get_all_trainings'),
    path('update/<int:pk>/', update_training, name='update_training'),
    path('delete/<int:pk>/', delete_training, name='delete_training'),
    path('upload_materials/', upload_training_materials, name='upload_training_materials'),
]
