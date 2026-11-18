from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ProfileForm, RegistrationForm, UserLoginForm
from .models import UserRole


def register(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard_redirect")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            applicant, _ = UserRole.objects.get_or_create(
                role_name="Applicant",
                defaults={"description": "PWD applicant or cardholder account"},
            )
            user = form.save(commit=False)
            user.role = applicant
            user.set_password(form.cleaned_data["password1"])
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("accounts:login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


class PWDigitalLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("accounts:dashboard_redirect")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


def dashboard_redirect(request):
    role_name = getattr(getattr(request.user, "role", None), "role_name", None)
    routes = {
        "Applicant": "dashboard:applicant",
        "LGU_Staff": "dashboard:lgu",
        "Partner": "dashboard:partner",
        "Admin": "dashboard:admin",
    }
    if role_name not in routes:
        messages.error(request, "Your account has no valid dashboard role.")
        return redirect("accounts:login")
    return redirect(routes[role_name])


def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
