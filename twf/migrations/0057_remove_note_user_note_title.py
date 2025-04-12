# Generated by Django 5.0.11 on 2025-04-12 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twf', '0056_note'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='note',
            name='user',
        ),
        migrations.AddField(
            model_name='note',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
