# Generated by Django 3.2.6 on 2024-12-07 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0035_remove_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='Receipt_image',
            field=models.ImageField(null=True, upload_to='receipt_images/'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='Receipt_number',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
