# Generated by Django 3.2.8 on 2021-11-04 17:49

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail_footnotes.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('logbooks', '0023_auto_20211105_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='importantpages',
            name='radio_index_page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    related_name='+', to='logbooks.radioindexpage'),
        ),
        migrations.AlterField(
            model_name='episodepage',
            name='body',
            field=wagtail.fields.StreamField([('text', wagtail_footnotes.blocks.RichTextBlockWithFootnotes(features=['h3', 'bold', 'italic', 'link', 'ol', 'ul', 'footnotes'], template='logbooks/story_blocks/text.html')), ('quote', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.blocks.CharBlock(required=False)), ('title', wagtail.blocks.CharBlock(
                required=False)), ('date', wagtail.blocks.DateBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('embed', wagtail.embeds.blocks.EmbedBlock(template='logbooks/story_blocks/embed.html')), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(required=False)), ('caption', wagtail.blocks.CharBlock())]))]),
        ),
    ]
