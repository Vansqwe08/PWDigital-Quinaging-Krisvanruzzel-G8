from django.contrib.auth.decorators import login_required

from accounts.decorators import role_required
from django.shortcuts import render


@login_required
@role_required("Applicant")
def applicant_dashboard(request):
    return render(request, "dashboard/applicant_dashboard.html")


@login_required
@role_required("Applicant")
def applicant_health_access(request):
    return render(request, "dashboard/applicant_health_access.html")


@login_required
@role_required("Applicant")
def applicant_qr_code(request):
    return render(request, "dashboard/applicant_qr_code.html")


@login_required
@role_required("LGU_Staff")
def lgu_dashboard(request):
    return render(request, "dashboard/lgu_dashboard.html")


@login_required
@role_required("Partner")
def partner_dashboard(request):
    return render(request, "dashboard/partner_dashboard.html")


@login_required
@role_required("Admin")
def admin_dashboard(request):
    return render(request, "dashboard/admin_dashboard.html")
