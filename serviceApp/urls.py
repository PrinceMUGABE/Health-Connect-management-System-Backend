from django.urls import path
from .views import create_service, get_service_by_id, get_service_by_name, update_service, delete_service, get_all_services

urlpatterns = [
    path('create/', create_service, name='create_service'),
    path('<int:service_id>/', get_service_by_id, name='get_service_by_id'),
    path('name/<str:name>/', get_service_by_name, name='get_service_by_name'),
    path('update/<int:service_id>/', update_service, name='update_service'),
    path('delete/<int:service_id>/', delete_service, name='delete_service'),
    path('services/', get_all_services, name='get_all_services'),
]
