import re

from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm
from PIL import Image

from .models import User


class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username", "email", "mobile_number")
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "username": forms.TextInput(attrs={"autocomplete": "username"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "mobile_number": forms.TextInput(
                attrs={"autocomplete": "tel", "inputmode": "tel"}
            ),
        }

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if not value:
            raise forms.ValidationError("First name is required.")
        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        if not value:
            raise forms.ValidationError("Last name is required.")
        return value

    def clean_mobile_number(self):
        value = self.cleaned_data["mobile_number"].strip()
        if not re.fullmatch(r"\+?[0-9][0-9 ()-]{7,18}[0-9]", value):
            raise forms.ValidationError("Enter a valid mobile number.")
        return value

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        if password1:
            password_validation.validate_password(password1)
        return password2


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "username"})
    )
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "mobile_number", "profile_photo")
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "mobile_number": forms.TextInput(
                attrs={"autocomplete": "tel", "inputmode": "tel"}
            ),
            "profile_photo": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                    "aria-describedby": "help-id_profile_photo",
                }
            ),
        }
        help_texts = {
            "profile_photo": (
                "Optional. Choose an image up to 2 MB, or leave this blank "
                "to keep your current photo."
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_mobile_number(self):
        value = self.cleaned_data["mobile_number"].strip()
        if not re.fullmatch(r"\+?[0-9][0-9 ()-]{7,18}[0-9]", value):
            raise forms.ValidationError("Enter a valid mobile number.")
        return value

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if not photo:
            return photo
        if photo.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Profile photo must not exceed 2 MB.")
        try:
            image = Image.open(photo)
            image.verify()
        except Exception:
            raise forms.ValidationError("Upload a genuine image file.")
        photo.seek(0)
        return photo
