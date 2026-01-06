from django.db import migrations


def create_default_role_limits(apps, schema_editor):
    RoleImageLimit = apps.get_model('core', 'RoleImageLimit')

    defaults = {
        'RegisteredFree': 10,
        'SubscriberPaid': 20,
        'Moderator': 20,
        'Staff': 20,
        'Admin': 20,
    }

    for role_name, max_images in defaults.items():
        RoleImageLimit.objects.update_or_create(
            role_name=role_name, defaults={'max_images': max_images}
        )


def remove_default_role_limits(apps, schema_editor):
    RoleImageLimit = apps.get_model('core', 'RoleImageLimit')
    role_names = ['RegisteredFree', 'SubscriberPaid', 'Moderator', 'Staff', 'Admin']
    RoleImageLimit.objects.filter(role_name__in=role_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_role_limits, remove_default_role_limits),
    ]
