# Generated by Django 3.2.6 on 2024-10-03 06:38

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0025_auto_20241003_1436'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Officers',
            new_name='Officer',
        ),
        migrations.RenameModel(
            old_name='Students',
            new_name='Student',
        ),
        migrations.RenameModel(
            old_name='Transactions',
            new_name='Transaction',
        ),
    ]
