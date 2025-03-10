# Generated by Django 5.0.4 on 2024-07-02 17:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("twf", "0009_collection_collectionitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="collection",
            name="project",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="collections",
                to="twf.project",
            ),
            preserve_default=False,
        ),
    ]
