# Generated by Django 5.1.3 on 2024-11-20 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_remove_studentsubject_subject_studentsubject_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentsubject',
            name='subject',
            field=models.ManyToManyField(to='app.subjectfaculty'),
        ),
    ]
