# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_worker, name='create_worker'),
    path('<int:id>/', views.get_worker_by_id, name='get_worker_by_id'),
    path('workers/', views.get_all_workers, name='get_all_workers'),
    path('firstname/<str:firstname>/', views.get_workers_by_firstname, name='get_workers_by_firstname'),
    path('lastname/<str:lastname>/', views.get_workers_by_lastname, name='get_workers_by_lastname'),
    path('address/<str:address>/', views.get_workers_by_address, name='get_workers_by_address'),
    path('update/<int:id>/', views.update_worker, name='update_worker'),
    path('delete/<int:id>/', views.delete_worker, name='delete_worker'),
    path('me/', views.get_logged_in_worker_info, name='get_logged_in_worker_info'),
]
