# Generated by Django 3.2.18 on 2023-04-24 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('smartforests', '0012_tag_translation_constraints'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=100, verbose_name='slug'),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('translation_key', 'locale'), ('locale', 'name')},
        ),
    ]
