# Generated by Django 5.1.3 on 2024-11-20 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_student_address_alter_student_blood_group_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentsubject',
            name='subject',
        ),
        migrations.AddField(
            model_name='studentsubject',
            name='subject',
            field=models.ManyToManyField(to='app.subject'),
        ),
    ]
