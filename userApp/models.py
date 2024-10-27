from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone number must be set')

        # Create a regular user with phone and other extra fields
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        # Set the default values for superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Ensure superuser has the correct privileges
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Explicitly set the role to "admin" for superusers
        extra_fields.setdefault('role', 'ceho')

        return self.create_user(phone, password, **extra_fields)


# User model with custom manager
class User(AbstractUser):
    ROLE_CHOICES = [
        ('ceho', 'Health Authority'),
        ('chw', 'Community Health Worker'),
        ('citizen', 'Citizen'),
    ]

    phone = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='citizen')
    
    created_at = models.DateTimeField(auto_now_add=True)

    username = None  # Remove the username field
    USERNAME_FIELD = 'phone'  # Use phone for authentication
    REQUIRED_FIELDS = []  # No additional fields required for superusers

    objects = UserManager()  # Attach the custom manager

    def __str__(self):
        return f'{self.phone} ({self.get_role_display()})'
