# Generated by Django 3.2.8 on 2021-10-28 18:10

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail_footnotes.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('logbooks', '0015_auto_20211028_1317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='logbookpage',
            options={'verbose_name': 'Logbook', 'verbose_name_plural': 'Logbooks'},
        ),
        migrations.RemoveField(
            model_name='importantpages',
            name='menu_items',
        ),
        migrations.AlterField(
            model_name='logbookentrypage',
            name='body',
            field=wagtail.fields.StreamField([('text', wagtail_footnotes.blocks.RichTextBlockWithFootnotes(features=['h3', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes'], template='logbooks/story_blocks/text.html')), ('quote', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.blocks.CharBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=False)), ('date', wagtail.blocks.DateBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock(template='logbooks/story_blocks/embed.html')), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.blocks.CharBlock())]))]),
        ),
        migrations.AlterField(
            model_name='storypage',
            name='body',
            field=wagtail.fields.StreamField([('text', wagtail_footnotes.blocks.RichTextBlockWithFootnotes(features=['h3', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes'], template='logbooks/story_blocks/text.html')), ('quote', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.blocks.CharBlock(required=False)), ('title', wagtail.blocks.CharBlock(required=False)), ('date', wagtail.blocks.DateBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock(template='logbooks/story_blocks/embed.html')), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.blocks.CharBlock())]))]),
        ),
    ]
