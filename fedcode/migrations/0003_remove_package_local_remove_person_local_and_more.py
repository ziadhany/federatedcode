# Generated by Django 5.0.1 on 2024-12-10 10:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("fedcode", "0002_alter_package_options_alter_federaterequest_done_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name="package",
            name="local",
        ),
        migrations.RemoveField(
            model_name="person",
            name="local",
        ),
        migrations.AlterField(
            model_name="person",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="person",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("remote_actor__isnull", True), ("user__isnull", False)),
                    models.Q(("remote_actor__isnull", False), ("user__isnull", True)),
                    _connector="OR",
                ),
                name="either_local_or_remote",
            ),
        ),
    ]