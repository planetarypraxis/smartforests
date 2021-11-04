# Generated by Django 3.2.9 on 2021-11-04 13:03

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit


class Migration(migrations.Migration):

    dependencies = [
        ('smartforests', '0006_tag'),
        ('logbooks', '0020_auto_20211104_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atlastag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logbooks_atlastag_items', to='smartforests.tag'),
        ),
        migrations.AlterField(
            model_name='episodepage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='logbooks.AtlasTag', to='smartforests.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='logbookentrypage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='logbooks.AtlasTag', to='smartforests.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='logbookpage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='logbooks.AtlasTag', to='smartforests.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='storypage',
            name='tags',
            field=modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='logbooks.AtlasTag', to='smartforests.Tag', verbose_name='Tags'),
        ),
    ]
