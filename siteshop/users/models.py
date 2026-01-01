from datetime import datetime, timedelta
import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractUser
import secrets
import bcrypt
from django.utils import timezone
from django.contrib.auth.hashers import check_password as django_check_password


class User(AbstractUser):
    patronymic = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="Отчество")

    photo = models.ImageField(
        upload_to="users/%Y/%m/%d/", blank=True, null=True, verbose_name="Фото")

    def set_password(self, raw_password):
        self.password = bcrypt.hashpw(
            raw_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, raw_password):
        if self.password.startswith('$2b$'):
            try:
                return bcrypt.checkpw(
                    raw_password.encode('utf-8'),
                    self.password.encode('utf-8')
                )
            except:
                return False

        else:
            return django_check_password(raw_password, self.password)

    def soft_delete(self):
        self.is_active = False
        self.save()


class Session(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    @classmethod
    def create_session(cls, user):
        session_key = secrets.token_urlsafe(64)
        expires_at = timezone.now() + timedelta(days=7)

        cls.objects.create(
            user=user,
            session_key=session_key,
            expires_at=expires_at
        )
        return session_key

    def is_valid(self):
        return self.is_active and timezone.now() < self.expires_at
