# urls.py
from django.urls import path
from .views import (
    CreateAppointmentView,
    GetAppointmentByIdView,
    UpdateAppointmentView,
    DeleteAppointmentView,
    GetAllAppointmentsView,
    GetAppointmentsByAddressView,
    GetAppointmentsByFirstNameView,
    GetAppointmentsByLastNameView,
    GetAppointmentsByCreatedByView,
    GetAppointmentsByAppointedToView,
    GetAppointmentsForLoggedInWorkerView,
    GetAppointmentsForLoggedInUser,
    UpdateAppointmentStatusView,
    GetAppointmentsByStatusView
    
)


urlpatterns = [
    path('appointments/', GetAllAppointmentsView.as_view(), name='get-all-appointments'),
    path('create/', CreateAppointmentView.as_view(), name='create-appointment'),
    path('<int:pk>/', GetAppointmentByIdView.as_view(), name='get-appointment-by-id'),
    path('update/<int:pk>/', UpdateAppointmentView.as_view(), name='update-appointment'),
    path('delete/<int:pk>/', DeleteAppointmentView.as_view(), name='delete-appointment'),
    path('address/<str:address>/', GetAppointmentsByAddressView.as_view(), name='get-appointments-by-address'),
    path('firstname/<str:first_name>/', GetAppointmentsByFirstNameView.as_view(), name='get-appointments-by-first-name'),
    path('lastname/<str:last_name>/', GetAppointmentsByLastNameView.as_view(), name='get-appointments-by-last-name'),
    path('created_by/<str:phone>/', GetAppointmentsByCreatedByView.as_view(), name='get-appointments-by-created-by'),
    path('appointed_to/<int:worker_id>/', GetAppointmentsByAppointedToView.as_view(), name='get-appointments-by-appointed-to'),
    path('worker_appointments/', GetAppointmentsForLoggedInWorkerView.as_view(), name='worker-appointments'),
    path('user_appointments/', GetAppointmentsForLoggedInUser.as_view(), name='worker-appointments'),
    path('status/<int:pk>/', UpdateAppointmentStatusView.as_view(), name='update-appointment-status'),
    path('by-status/<str:status_value>/', GetAppointmentsByStatusView.as_view(), name='get-appointments-by-status'),
]

