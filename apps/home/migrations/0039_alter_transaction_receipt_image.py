# Generated by Django 3.2.6 on 2024-12-07 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0038_alter_transaction_receipt_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='Receipt_image',
            field=models.ImageField(null=True, upload_to=''),
        ),
    ]
