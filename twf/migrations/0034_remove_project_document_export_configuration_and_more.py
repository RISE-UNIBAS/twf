# Generated by Django 5.0.9 on 2024-11-02 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twf', '0033_project_conf_export_project_conf_tasks_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='document_export_configuration',
        ),
        migrations.RemoveField(
            model_name='project',
            name='metadata_google_doc_id_column',
        ),
        migrations.RemoveField(
            model_name='project',
            name='metadata_google_sheet_id',
        ),
        migrations.RemoveField(
            model_name='project',
            name='metadata_google_sheet_range',
        ),
        migrations.RemoveField(
            model_name='project',
            name='metadata_google_title_column',
        ),
        migrations.RemoveField(
            model_name='project',
            name='metadata_google_valid_columns',
        ),
        migrations.RemoveField(
            model_name='project',
            name='page_export_configuration',
        ),
    ]
