from django.db import migrations


def seed_roles(apps, schema_editor):
    UserRole = apps.get_model("accounts", "UserRole")
    roles = (
        ("Applicant", "PWD applicant or cardholder account"),
        ("LGU_Staff", "LGU/PDAO staff account"),
        ("Partner", "Partner establishment or verification agency account"),
        ("Admin", "System administrator account"),
    )
    for role_name, description in roles:
        UserRole.objects.update_or_create(
            role_name=role_name,
            defaults={"description": description},
        )


def remove_roles(apps, schema_editor):
    UserRole = apps.get_model("accounts", "UserRole")
    UserRole.objects.filter(role_name__in=["Applicant", "LGU_Staff", "Partner", "Admin"]).delete()


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.RunPython(seed_roles, remove_roles)]
