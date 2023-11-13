from django.contrib.auth.models import AbstractUser, Permission, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, MaxLengthValidator, MinLengthValidator, validate_email
from UserManagement.validators import (
    validate_password_symbol,
    validate_password_number,
    validate_password_uppercase,
    validate_password_lowercase,
)


class UserManagement(AbstractUser):
    email = models.EmailField(
        unique=True,
        validators=[
            validate_email,
            EmailValidator(message="Enter a valid email address.")
        ]
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            MinLengthValidator(limit_value=6, message="Username must be at least 6 characters long."),
            MaxLengthValidator(limit_value=30, message="Username must not exceed 30 characters."),
        ]
    )
    password = models.CharField(
        validators=[
            validate_password_symbol,
            validate_password_number,
            validate_password_uppercase,
            validate_password_lowercase,
            MinLengthValidator(limit_value=6, message="Password must be at least 6 characters long."),
            MaxLengthValidator(limit_value=128, message="Password must not exceed 128 characters.")
        ]
    )
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)

    registration_date = models.DateField(auto_now_add=True)
    last_login_date = models.DateField(auto_now=True)

    account_status = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name="users",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="users",
    )

    def save(self, *args, **kwargs):
        if not any(char.isupper() for char in self.password):
            raise models.ValidationError("Password must contain at least one uppercase character.")
        super().save(*args, **kwargs)
