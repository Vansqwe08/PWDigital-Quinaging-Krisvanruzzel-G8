from django.test import TestCase
from django.urls import reverse

from accounts.models import User, UserRole


class ApplicantPlaceholderPageTests(TestCase):
    def setUp(self):
        applicant_role, _ = UserRole.objects.get_or_create(role_name="Applicant")
        partner_role, _ = UserRole.objects.get_or_create(role_name="Partner")
        self.applicant = User.objects.create_user(
            username="placeholder_applicant",
            email="placeholder_applicant@example.com",
            password="StrongPass!729",
            role=applicant_role,
        )
        self.partner = User.objects.create_user(
            username="placeholder_partner",
            email="placeholder_partner@example.com",
            password="StrongPass!729",
            role=partner_role,
        )

    def test_placeholder_pages_render_empty_content_and_active_navigation(self):
        pages = (
            (
                "dashboard:applicant_health_access",
                "/dashboard/applicant/health-access/",
                "dashboard/applicant_health_access.html",
            ),
            (
                "dashboard:applicant_qr_code",
                "/dashboard/applicant/qr-code/",
                "dashboard/applicant_qr_code.html",
            ),
        )
        self.client.force_login(self.applicant)

        for route_name, expected_path, template_name in pages:
            with self.subTest(route_name=route_name):
                path = reverse(route_name)
                self.assertEqual(path, expected_path)
                response = self.client.get(path)

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template_name)
                self.assertContains(
                    response,
                    f'<a class="sidebar-link is-active"\n       href="{expected_path}"\n       aria-current="page">',
                )
                self.assertNotContains(response, 'class="content-card')
                self.assertNotContains(response, 'class="welcome-hero')

    def test_placeholder_pages_require_applicant_login(self):
        pages = (
            "dashboard:applicant_health_access",
            "dashboard:applicant_qr_code",
        )

        for route_name in pages:
            with self.subTest(route_name=route_name):
                path = reverse(route_name)
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    f"{reverse('accounts:login')}?next={path}",
                )

                self.client.force_login(self.partner)
                self.assertEqual(self.client.get(path).status_code, 403)
                self.client.logout()
