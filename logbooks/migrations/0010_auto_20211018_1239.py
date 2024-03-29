# Generated by Django 3.2.8 on 2021-10-18 12:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailredirects', '0006_redirect_increase_max_length'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('wagtailmenus', '0023_remove_use_specific'),
        ('wagtailcore', '0062_comment_models_and_pagesubscription'),
        ('wagtailforms', '0004_add_verbose_name_plural'),
        ('logbooks', '0009_auto_20211015_1442'),
    ]

    operations = [
        migrations.RenameModel(
            new_name='LogbookEntryPage',
            old_name='StoryPage',
        ),
        # PostGIS indexes don't get renamed automatically. Do it here so that we don't get name collisions in future.
        migrations.RunSQL(
            'ALTER INDEX logbooks_storypage_coordinates_id RENAME TO logbooks_logbookentrypage_coordinates_id',
            reverse_sql='ALTER INDEX logbooks_logbookentrypage_coordinates_id RENAME TO logbooks_storypage_coordinates_id'
        ),
    ]
