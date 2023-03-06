# Generated by Django 3.2.13 on 2023-02-06 12:39

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail_footnotes.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('smartforests', '0009_auto_20230109_1712'),
        ('logbooks', '0035_auto_20220530_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='episodepage',
            name='thumbnail',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='episode_thumbnail', to='smartforests.cmsimage'),
        ),
        migrations.AlterField(
            model_name='episodepage',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail_footnotes.blocks.RichTextBlockWithFootnotes(features=['h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes'], template='logbooks/story_blocks/text.html')), ('quote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('date', wagtail.core.blocks.DateBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock(template='logbooks/story_blocks/embed.html')), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'code', 'blockquote']))]))]),
        ),
        migrations.AlterField(
            model_name='logbookentrypage',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail_footnotes.blocks.RichTextBlockWithFootnotes(features=['h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes'], template='logbooks/story_blocks/text.html')), ('quote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('date', wagtail.core.blocks.DateBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock(template='logbooks/story_blocks/embed.html')), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'code', 'blockquote']))]))]),
        ),
        migrations.AlterField(
            model_name='storypage',
            name='body',
            field=wagtail.core.fields.StreamField([('text', wagtail_footnotes.blocks.RichTextBlockWithFootnotes(features=['h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes'], template='logbooks/story_blocks/text.html')), ('quote', wagtail.core.blocks.StructBlock([('text', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.core.blocks.CharBlock(required=False)), ('title', wagtail.core.blocks.CharBlock(required=False)), ('date', wagtail.core.blocks.DateBlock(required=False)), ('link', wagtail.core.blocks.URLBlock(required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock(template='logbooks/story_blocks/embed.html')), ('image', wagtail.core.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul', 'hr', 'code', 'blockquote']))]))]),
        ),
    ]