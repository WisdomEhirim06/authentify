from django.contrib.auth.models import AbstractBaseUser
from django.db import models

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']


    def __str__(self):
        return self.email


class Phone(models.Model):
    user_profile = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)


class Organization(models.Model):
    org_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User)