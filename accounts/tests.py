from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from .models import User, UserRole


class AccountTestMixin:
    def setUp(self):
        super().setUp()
        self.roles = {
            name: UserRole.objects.get_or_create(role_name=name)[0]
            for name in ("Applicant", "LGU_Staff", "Partner", "Admin")
        }

    def create_user(self, username, role_name="Applicant", **extra):
        defaults = {
            "email": f"{username}@example.com",
            "mobile_number": "09171234567",
            "first_name": "Test",
            "last_name": "User",
        }
        defaults.update(extra)
        return User.objects.create_user(username=username, role=self.roles[role_name], password="StrongPass!729", **defaults)


class RegistrationTests(AccountTestMixin, TestCase):
    def test_valid_registration_assigns_applicant_and_hashes_password(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "Maria", "last_name": "Santos", "username": "maria",
            "email": "maria@example.com", "mobile_number": "09171234567",
            "password1": "StrongPass!729", "password2": "StrongPass!729",
        })
        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(username="maria")
        self.assertEqual(user.role.role_name, "Applicant")
        self.assertTrue(user.password.startswith("pbkdf2_"))
        self.assertNotEqual(user.password, "StrongPass!729")

    def test_invalid_email_duplicate_username_duplicate_email_and_missing_fields(self):
        self.create_user("existing")
        cases = [
            {"first_name": "A", "last_name": "B", "username": "valid1", "email": "not-email",
             "mobile_number": "09171234567", "password1": "StrongPass!729", "password2": "StrongPass!729"},
            {"first_name": "A", "last_name": "B", "username": "existing", "email": "new@example.com",
             "mobile_number": "09171234567", "password1": "StrongPass!729", "password2": "StrongPass!729"},
            {"first_name": "A", "last_name": "B", "username": "valid2", "email": "existing@example.com",
             "mobile_number": "09171234567", "password1": "StrongPass!729", "password2": "StrongPass!729"},
            {"first_name": "", "last_name": "", "username": "", "email": "",
             "mobile_number": "", "password1": "", "password2": ""},
        ]
        for data in cases:
            with self.subTest(data=data):
                response = self.client.post(reverse("accounts:register"), data)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)

    def test_mismatched_password_is_rejected(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "A", "last_name": "B", "username": "mismatch",
            "email": "mismatch@example.com", "mobile_number": "09171234567",
            "password1": "StrongPass!729", "password2": "DifferentPass!729",
        })
        self.assertTrue(response.context["form"].errors)

    def test_public_registration_cannot_choose_privileged_role(self):
        response = self.client.post(reverse("accounts:register"), {
            "first_name": "A", "last_name": "B", "username": "public",
            "email": "public@example.com", "mobile_number": "09171234567",
            "password1": "StrongPass!729", "password2": "StrongPass!729",
            "role": self.roles["Admin"].pk,
        })
        self.assertEqual(User.objects.get(username="public").role.role_name, "Applicant")


class LoginRoleAccessTests(AccountTestMixin, TestCase):
    def test_login_logout_and_role_redirect(self):
        user = self.create_user("applicant")
        response = self.client.post(reverse("accounts:login"), {"username": "applicant", "password": "StrongPass!729"})
        self.assertRedirects(
            response,
            reverse("accounts:dashboard_redirect"),
            fetch_redirect_response=False,
        )
        self.assertRedirects(
            self.client.get(reverse("accounts:dashboard_redirect")),
            reverse("dashboard:applicant"),
            fetch_redirect_response=False,
        )
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_invalid_and_inactive_login(self):
        response = self.client.post(reverse("accounts:login"), {"username": "missing", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        user = self.create_user("inactive", is_active=False)
        response = self.client.post(reverse("accounts:login"), {"username": "inactive", "password": "StrongPass!729"})
        self.assertEqual(response.status_code, 200)

    def test_role_dashboards_and_unauthenticated_protection(self):
        applicant = self.create_user("applicant")
        lgu = self.create_user("lgu", "LGU_Staff")
        partner = self.create_user("partner", "Partner")
        admin = self.create_user("admin", "Admin")
        cases = [
            (applicant, "dashboard:applicant", 200),
            (applicant, "dashboard:lgu", 403),
            (lgu, "dashboard:lgu", 200),
            (lgu, "dashboard:partner", 403),
            (partner, "dashboard:partner", 200),
            (partner, "dashboard:admin", 403),
            (admin, "dashboard:admin", 200),
        ]
        for user, route, status in cases:
            self.client.force_login(user)
            self.assertEqual(self.client.get(reverse(route)).status_code, status)
        self.client.logout()
        response = self.client.get(reverse("dashboard:applicant"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('dashboard:applicant')}")

    def test_dashboards_distinguish_available_and_planned_features(self):
        applicant = self.create_user("applicant")
        lgu = self.create_user("lgu", "LGU_Staff")
        partner = self.create_user("partner", "Partner")
        admin = self.create_user("admin", "Admin")

        self.client.force_login(applicant)
        response = self.client.get(reverse("dashboard:applicant"))
        self.assertContains(response, "Manage your profile")
        self.assertContains(response, "not available yet")

        for user, route in (
            (lgu, "dashboard:lgu"),
            (partner, "dashboard:partner"),
        ):
            with self.subTest(route=route):
                self.client.force_login(user)
                self.assertContains(
                    self.client.get(reverse(route)),
                    "not available in this phase",
                )

        self.client.force_login(admin)
        self.assertContains(
            self.client.get(reverse("dashboard:admin")),
            "Available now",
        )


class ProfileTests(AccountTestMixin, TestCase):
    def test_view_update_duplicate_email_and_fields_cannot_change(self):
        user = self.create_user("profile")
        self.create_user("other")
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)
        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Updated", "last_name": "Name",
            "email": "updated@example.com", "mobile_number": "09179876543",
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.username, "profile")
        self.assertEqual(user.role.role_name, "Applicant")

        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Updated", "last_name": "Name",
            "email": "other@example.com", "mobile_number": "09179876543",
            "username": "changed", "role": self.roles["Admin"].pk,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_valid_image_upload_and_invalid_image_rejection(self):
        user = self.create_user("photo")
        self.client.force_login(user)
        image = Image.new("RGB", (20, 20), "blue")
        stream = BytesIO()
        image.save(stream, format="JPEG")
        valid = SimpleUploadedFile("photo.jpg", stream.getvalue(), content_type="image/jpeg")
        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Test", "last_name": "User",
            "email": "photo@example.com", "mobile_number": "09171234567",
            "profile_photo": valid,
        })
        self.assertRedirects(response, reverse("accounts:profile"))
        user.refresh_from_db()
        self.assertTrue(user.profile_photo)

        invalid = SimpleUploadedFile("fake.jpg", b"not an image", content_type="image/jpeg")
        response = self.client.post(reverse("accounts:profile"), {
            "first_name": "Test", "last_name": "User",
            "email": "photo@example.com", "mobile_number": "09171234567",
            "profile_photo": invalid,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors["profile_photo"])
