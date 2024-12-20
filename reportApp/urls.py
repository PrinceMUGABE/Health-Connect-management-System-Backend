# reportApp/urls.py

from django.urls import path
from .views import (
    create_report,
    get_report_by_id,
    get_reports_by_activity,
    get_reports_by_user,
    update_report_by_id,
    delete_report_by_id,
    get_all_reports,
)

urlpatterns = [
    path('create/', create_report, name='create_report'),
    path('<int:report_id>/', get_report_by_id, name='get_report_by_id'),
    path('activity/<str:activity>/', get_reports_by_activity, name='get_reports_by_activity'),
    path('user/', get_reports_by_user, name='get_reports_by_user'),
    path('update/<int:report_id>/', update_report_by_id, name='update_report_by_id'),
    path('delete/<int:report_id>/', delete_report_by_id, name='delete_report_by_id'),
    path('reports/', get_all_reports, name='get_all_reports'),
]
