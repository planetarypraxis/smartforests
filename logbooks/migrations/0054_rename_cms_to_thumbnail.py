# Generated by Django 3.2.25 on 2024-10-09 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logbooks', '0053_migrate_thumbnail_to_cms'),
    ]

    operations = [
         migrations.RemoveField(
            model_name='episodepage',
            name='thumbnail_image',
        ),
        migrations.RemoveField(
            model_name='logbookentrypage',
            name='thumbnail_image',
        ),
        migrations.RemoveField(
            model_name='logbookpage',
            name='thumbnail_image',
        ),
        migrations.RemoveField(
            model_name='playlistpage',
            name='thumbnail_image',
        ),
        migrations.RemoveField(
            model_name='storypage',
            name='thumbnail_image',
        ),
        migrations.RenameField(
            model_name='episodepage',
            old_name='cms_thumbnail_image',
            new_name='thumbnail_image',
        ),
        migrations.RenameField(
            model_name='logbookentrypage',
            old_name='cms_thumbnail_image',
            new_name='thumbnail_image',
        ),
        migrations.RenameField(
            model_name='logbookpage',
            old_name='cms_thumbnail_image',
            new_name='thumbnail_image',
        ),
        migrations.RenameField(
            model_name='playlistpage',
            old_name='cms_thumbnail_image',
            new_name='thumbnail_image',
        ),
        migrations.RenameField(
            model_name='storypage',
            old_name='cms_thumbnail_image',
            new_name='thumbnail_image',
        ),
    ]
