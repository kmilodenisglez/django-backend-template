from django.db import migrations, models


def create_role_text_limits(apps, schema_editor):
    RoleTextLimit = apps.get_model('core', 'RoleTextLimit')

    defaults = {
        'Anonymous': {'title_limit': 80, 'body_limit': 500},
        'RegisteredFree': {'title_limit': 200, 'body_limit': 2000},
        'SubscriberPaid': {'title_limit': 400, 'body_limit': 5000},
        'Moderator': {'title_limit': 400, 'body_limit': 5000},
        'Staff': {'title_limit': 400, 'body_limit': 5000},
        'Admin': {'title_limit': 400, 'body_limit': 5000},
    }

    for role_name, limits in defaults.items():
        RoleTextLimit.objects.update_or_create(
            role_name=role_name,
            defaults={'title_limit': limits['title_limit'], 'body_limit': limits['body_limit']},
        )


def remove_role_text_limits(apps, schema_editor):
    RoleTextLimit = apps.get_model('core', 'RoleTextLimit')
    RoleTextLimit.objects.filter(role_name__in=['Anonymous', 'RegisteredFree', 'SubscriberPaid', 'Moderator', 'Staff', 'Admin']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_default_roleimagelimits'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleTextLimit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=32, unique=True, verbose_name='Role Name')),
                ('title_limit', models.PositiveIntegerField(default=200, verbose_name='Title Limit')),
                ('body_limit', models.PositiveIntegerField(default=2000, verbose_name='Body Limit')),
            ],
            options={
                'verbose_name': 'Role Text Limit',
                'verbose_name_plural': 'Role Text Limits',
                'ordering': ['role_name'],
            },
        ),
        migrations.RunPython(create_role_text_limits, remove_role_text_limits),
    ]
