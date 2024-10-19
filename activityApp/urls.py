from django.urls import path
from .views import (
    create_activity,
    get_all_activities,
    get_activities_by_user,
    get_activity_by_id,
    update_activity,
    delete_activity
)

urlpatterns = [
    path('create/', create_activity, name='create_activity'),
    path('activities/', get_all_activities, name='get_all_activities'),
    path('user/', get_activities_by_user, name='get_activities_by_user'),
    path('<int:activity_id>/', get_activity_by_id, name='get_activity_by_id'),
    path('update/<int:activity_id>/', update_activity, name='update_activity'),
    path('delete/<int:activity_id>/', delete_activity, name='delete_activity'),
]
