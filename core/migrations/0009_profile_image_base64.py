# Generated by Django 5.1.7 on 2025-04-08 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_statuschangehistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image_base64',
            field=models.TextField(blank=True, null=True),
        ),
    ]
