# Generated by Django 5.1.2 on 2024-12-27 17:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fedcode", "0004_alter_vulnerability_unique_together"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="person",
            name="avatar",
        ),
    ]
