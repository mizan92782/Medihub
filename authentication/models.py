from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from core.enum import RoleChoices


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        if password is None:
            raise ValueError("Password required")
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', RoleChoices.ADMIN)
        return self.create_user(email=email, password=password, **extra_fields)
        
    def create_staffuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.REGULAR)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_blood_donor = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def isAdmin(self):
        return self.is_superuser
    def isStaff(self):
        return self.is_staff
    def isAuthenticate(self):
        return self.is_authenticated

    def __str__(self):
        return self.email
