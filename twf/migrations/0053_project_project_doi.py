# Generated by Django 5.0.11 on 2025-02-12 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twf', '0052_export'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_doi',
            field=models.CharField(blank=True, help_text='The DOI of the project.', max_length=255, null=True, verbose_name='Project DOI'),
        ),
    ]
