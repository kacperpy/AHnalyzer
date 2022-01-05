from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    realm_id = models.IntegerField(default=4455)