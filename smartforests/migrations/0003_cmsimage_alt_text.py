# Generated by Django 3.2.5 on 2021-08-02 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartforests', '0002_cmsdocument_cmsimage_imagerendition'),
    ]

    operations = [
        migrations.AddField(
            model_name='cmsimage',
            name='alt_text',
            field=models.CharField(default='', max_length=1024),
        ),
    ]
