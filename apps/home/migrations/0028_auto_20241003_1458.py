# Generated by Django 3.2.6 on 2024-10-03 06:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_remove_officer_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='payment_type',
            new_name='Payment_type',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='student',
            new_name='Student',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='Transaction_Date',
            new_name='Transaction_date',
        ),
    ]
