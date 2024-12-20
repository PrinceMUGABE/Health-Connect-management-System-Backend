from django.urls import path
from .views import (
    create_training,
    create_module,
    upload_material_to_module,
    get_training_by_id,
    get_all_trainings,
    get_all_modules,
    get_modules_by_training,  # New import
    update_training,
    update_module,
    delete_training,
    delete_module,
    get_module_by_id,
)

urlpatterns = [
    path('trainings/', get_all_trainings, name='get_all_trainings'),
    path('create/', create_training, name='create_training'),
    path('<int:pk>/', get_training_by_id, name='get_training_by_id'),
    path('update/<int:pk>/', update_training, name='update_training'),
    path('delete/<int:pk>/', delete_training, name='delete_training'),

    # Module-specific URLs
    path('modules/<int:training_id>/', get_all_modules, name='get_all_modules'),
    path('modules/by_training/<int:training_id>/', get_modules_by_training, name='get_modules_by_training'),  # New URL
    path('module/create/<int:training_id>/', create_module, name='create_module'),
    path('module/update/<int:module_id>/', update_module, name='update_module'),
    path('module/delete/<int:module_id>/', delete_module, name='delete_module'),

    # Material upload within a module
    path('modules/materials/upload/<int:module_id>/', upload_material_to_module, name='upload_material_to_module'),
    path('module/<int:module_id>/', get_module_by_id, name='get_module_by_id'),
]


# Added comment