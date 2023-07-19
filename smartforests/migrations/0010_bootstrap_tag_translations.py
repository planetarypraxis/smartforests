# Generated by Django 3.2.18 on 2023-04-24 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('smartforests', '0009_auto_20230109_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='locale',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale'),
        ),
        migrations.AddField(
            model_name='tag',
            name='translation_key',
            field=models.UUIDField(editable=False, null=True),
        ),
    ]
