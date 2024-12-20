from django.urls import path
from .views import (
    user_signup, login_view, get_user_by_id, get_all_users,
    update_delete_user, get_user_profile, reset_password, contact_us, create_user
)

urlpatterns = [
    path('signup/', user_signup, name='signup'),
    path('login/', login_view, name='login'),
    path('user/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path('users/', get_all_users, name='get_all_users'),
    path('update/<int:id>/', update_delete_user, name='update_user_by_id'),
    path('delete/<int:id>/', update_delete_user, name='delete_user_by_id'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('forget_password/', reset_password, name='forget_password'),
    path('contact/', contact_us, name='contact'),
    path('add-user/', create_user, name='add_user'),
]
