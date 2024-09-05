# Generated by Django 5.0.4 on 2024-06-16 13:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("twf", "0005_project_geonames_username_project_openai_api_key_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="selected_dictionaries",
            field=models.ManyToManyField(
                help_text="The dictionaries selected for this project.",
                related_name="selected_projects",
                to="twf.dictionary",
                verbose_name="Selected Dictionaries",
            ),
        ),
    ]
