# Generated by Django 3.2.6 on 2024-05-24 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0022_alter_student_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='first_name',
            field=models.CharField(default='', max_length=75),
        ),
        migrations.AlterField(
            model_name='student',
            name='last_name',
            field=models.CharField(default='', max_length=75),
        ),
        migrations.AlterField(
            model_name='student',
            name='student_num',
            field=models.CharField(default='', max_length=40),
        ),
    ]