# Generated by Django 3.2.6 on 2024-10-03 06:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20241003_1438'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='officer',
            name='User',
        ),
    ]