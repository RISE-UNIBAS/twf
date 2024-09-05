# Generated by Django 5.0.4 on 2024-09-05 20:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("twf", "0014_project_document_metadata_fields_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectionitem",
            name="document_configuration",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="datevariation",
            name="normalized_variation",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="dictionaryentry",
            name="authorization_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="document",
            name="metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="page",
            name="metadata",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="page",
            name="parsed_data",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="pagetag",
            name="additional_information",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name="project",
            name="document_metadata_fields",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="A dictionary of metadata fields for documents.",
                verbose_name="Document Metadata Fields",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="ignored_tag_types",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="A list of tag types to ignore and a list of tag typeswhich are special (e.g. dates).",
                verbose_name="Special Tag Types",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="page_metadata_fields",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="A dictionary of metadata fields for pages.",
                verbose_name="Page Metadata Fields",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="tag_type_translator",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text="A dictionary to translate tag types into dictionary types if they are not equal.",
                verbose_name="Tag Type Translator",
            ),
        ),
    ]
