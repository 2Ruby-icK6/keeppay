# Generated by Django 3.2.6 on 2024-10-04 15:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0032_student_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='User',
            new_name='user',
        ),
    ]