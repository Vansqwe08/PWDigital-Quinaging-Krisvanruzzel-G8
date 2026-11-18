from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("A username is required.")
        email = self.normalize_email(email)
        role = extra_fields.pop("role", None)
        if role is None:
            role, _ = UserRole.objects.get_or_create(
                role_name="Applicant",
                defaults={"description": "PWD applicant or cardholder account"},
            )
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        role, _ = UserRole.objects.get_or_create(
            role_name="Admin",
            defaults={"description": "System administrator account"},
        )
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **extra_fields,
        )


class UserRole(models.Model):
    role_name = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("role_name",)

    def __str__(self):
        return self.role_name


class User(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20)
    role = models.ForeignKey(
        UserRole,
        on_delete=models.PROTECT,
        related_name="users",
    )
    profile_photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)
        super().save(*args, **kwargs)
