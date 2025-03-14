from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import UserManager
from django.db import models


class User(AbstractBaseUser):
    is_staff = models.BooleanField("Staff status", default=False)
    is_superuser = models.BooleanField("Super user status", default=False)
    is_active = models.BooleanField("Active", default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    username = models.CharField("Username", max_length=50, unique=True)
    email = models.EmailField("E-mail", blank=True)
    first_name = models.CharField("First name", max_length=50, blank=True)
    last_name = models.CharField("Last name", max_length=50, blank=True)
    city = models.CharField("City", max_length=50, blank=True)
    country = models.CharField("Country", max_length=50, blank=True)
    balance = models.IntegerField("Balance", default=0)
    is_verified = models.BooleanField("staff status", default=False)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"

    objects = UserManager()