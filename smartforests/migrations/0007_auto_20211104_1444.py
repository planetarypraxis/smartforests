# Generated by Django 3.2.9 on 2021-11-04 14:44

from django.db import migrations, models
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('smartforests', '0006_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='description',
            field=wagtail.core.fields.RichTextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='tag',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]