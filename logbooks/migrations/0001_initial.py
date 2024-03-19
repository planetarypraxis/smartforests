# Generated by Django 3.2.5 on 2021-08-02 11:26

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.contrib.taggit
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0062_comment_models_and_pagesubscription'),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='AtlasTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_object', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='tagged_items', to='wagtailcore.page')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logbooks_atlastag_items', to='taggit.tag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LogbookIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StoryIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='StoryPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('body', wagtail.fields.StreamField([('text', wagtail.blocks.RichTextBlock(features=['h3', 'bold', 'italic', 'link', 'ol', 'ul'])), ('quote', wagtail.blocks.StructBlock([('text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link'])), ('author', wagtail.blocks.CharBlock(required=False)), ('date', wagtail.blocks.DateBlock(required=False)), ('link', wagtail.blocks.URLBlock(required=False))])), ('embed', wagtail.blocks.RichTextBlock(features=['embed'])), ('image', wagtail.blocks.StructBlock([('caption', wagtail.blocks.CharBlock()), ('image', wagtail.images.blocks.ImageChooserBlock())]))])),
                ('tags', modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='logbooks.AtlasTag', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='LogbookPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('tags', modelcluster.contrib.taggit.ClusterTaggableManager(blank=True, help_text='A comma-separated list of tags.', through='logbooks.AtlasTag', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
