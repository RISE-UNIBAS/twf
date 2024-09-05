# Generated by Django 5.0.4 on 2024-06-24 15:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("twf", "0007_alter_project_selected_dictionaries"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dictionary",
            name="label",
            field=models.CharField(
                help_text="The label of the dictionary. This should be unique and descriptive.",
                max_length=100,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="dictionary",
            name="type",
            field=models.CharField(
                help_text="The type of the dictionary. This means the Transkribus tag type.",
                max_length=100,
            ),
        ),
    ]
