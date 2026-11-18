from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("role_name", "description")
    search_fields = ("role_name",)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username", "email", "first_name", "last_name",
        "role", "is_active", "is_staff", "created_at",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("created_at", "last_login", "date_joined")
    fieldsets = UserAdmin.fieldsets + (
        ("PWDigital Account", {"fields": ("mobile_number", "role", "profile_photo", "created_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "mobile_number"),
        }),
    )
