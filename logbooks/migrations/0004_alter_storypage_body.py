# Generated by Django 3.2.5 on 2021-08-03 15:40

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('logbooks', '0003_importantpages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storypage',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail.core.blocks.RichTextBlock(features=['h3', 'bold', 'italic', 'link', 'ol', 'ul'])), ('quote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('date', wagtail.core.blocks.DateBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))])), ('embed', wagtail.core.blocks.RichTextBlock(features=['embed'])), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.core.blocks.CharBlock())]))]),
        ),
    ]