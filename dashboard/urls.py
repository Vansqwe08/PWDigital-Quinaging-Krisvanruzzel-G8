from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("applicant/", views.applicant_dashboard, name="applicant"),
    path("lgu/", views.lgu_dashboard, name="lgu"),
    path("partner/", views.partner_dashboard, name="partner"),
    path("admin/", views.admin_dashboard, name="admin"),
]
