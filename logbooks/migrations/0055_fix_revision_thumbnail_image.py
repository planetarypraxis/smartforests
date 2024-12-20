# Generated by Django 3.2.25 on 2024-10-09 17:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logbooks', '0054_rename_cms_to_thumbnail'),
    ]

    operations = [
        migrations.RunSQL(
            """
            UPDATE wagtailcore_revision SET content = content || '{"thumbnail_image": null}' where content->>'thumbnail_image' = ''
            """,
            reverse_sql="""
            UPDATE wagtailcore_revision SET content = content || '{"thumbnail_image": ""}' where content->>'thumbnail_image' is null;
            """
        )
    ]
