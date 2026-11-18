from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("applicant/", views.applicant_dashboard, name="applicant"),
    path(
        "applicant/health-access/",
        views.applicant_health_access,
        name="applicant_health_access",
    ),
    path(
        "applicant/qr-code/",
        views.applicant_qr_code,
        name="applicant_qr_code",
    ),
    path("lgu/", views.lgu_dashboard, name="lgu"),
    path("partner/", views.partner_dashboard, name="partner"),
    path("admin/", views.admin_dashboard, name="admin"),
]
