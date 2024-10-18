from django.urls import path
from .views import (
    user_signup, login_view, get_user_by_id, get_all_users,
    update_delete_user, get_user_profile, reset_password
)

urlpatterns = [
    path('signup/', user_signup, name='signup'),
    path('login/', login_view, name='login'),
    path('user/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path('users/', get_all_users, name='get_all_users'),
    path('update/<int:id>/', update_delete_user, name='update_user_by_id'),
    path('delete/<int:id>/', update_delete_user, name='delete_user_by_id'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('reset-password/', reset_password, name='reset_password'),
]
