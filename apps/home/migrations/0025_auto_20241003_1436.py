# Generated by Django 3.2.6 on 2024-10-03 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_auto_20241003_1413'),
    ]

    operations = [
        migrations.RenameField(
            model_name='officers',
            old_name='student',
            new_name='Student',
        ),
        migrations.RenameField(
            model_name='officers',
            old_name='user',
            new_name='User',
        ),
    ]