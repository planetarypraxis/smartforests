# Generated by Django 3.2.6 on 2021-10-12 15:50

from django.db import migrations
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('smartforests', '0006_auto_20211007_1443'),
        ('logbooks', '0011_auto_20211012_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='logbookpage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='smartforests.AtlasTag', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
