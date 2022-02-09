# Generated by Django 3.2.12 on 2022-02-08 19:08

from django.conf import settings
from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logbooks', '0030_auto_20220208_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='episodepage',
            name='excluded_contributors',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, help_text='Contributors who should be hidden from public citation', related_name='_logbooks_episodepage_excluded_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='logbookentrypage',
            name='excluded_contributors',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, help_text='Contributors who should be hidden from public citation', related_name='_logbooks_logbookentrypage_excluded_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='logbookpage',
            name='excluded_contributors',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, help_text='Contributors who should be hidden from public citation', related_name='_logbooks_logbookpage_excluded_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='storypage',
            name='excluded_contributors',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, help_text='Contributors who should be hidden from public citation', related_name='_logbooks_storypage_excluded_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
    ]