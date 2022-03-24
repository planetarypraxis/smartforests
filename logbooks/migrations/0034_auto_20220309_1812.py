# Generated by Django 3.2.12 on 2022-03-09 18:12

from django.conf import settings
from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logbooks', '0033_auto_20220310_1748'),
    ]

    operations = [
        migrations.RenameField(
            model_name='episodepage',
            old_name='additional_contributing_users',
            new_name='additional_contributors',
        ),
        migrations.RenameField(
            model_name='logbookentrypage',
            old_name='additional_contributing_users',
            new_name='additional_contributors',
        ),
        migrations.RenameField(
            model_name='logbookpage',
            old_name='additional_contributing_users',
            new_name='additional_contributors',
        ),
        migrations.RenameField(
            model_name='storypage',
            old_name='additional_contributing_users',
            new_name='additional_contributors',
        ),
        migrations.RemoveField(
            model_name='episodepage',
            name='additional_contributing_people',
        ),
        migrations.RemoveField(
            model_name='logbookentrypage',
            name='additional_contributing_people',
        ),
        migrations.RemoveField(
            model_name='logbookpage',
            name='additional_contributing_people',
        ),
        migrations.RemoveField(
            model_name='storypage',
            name='additional_contributing_people',
        ),
        migrations.AddField(
            model_name='episodepage',
            name='contributors',
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, help_text='Index list of contributors', related_name='_logbooks_episodepage_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='logbookentrypage',
            name='contributors',
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, help_text='Index list of contributors', related_name='_logbooks_logbookentrypage_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='logbookpage',
            name='contributors',
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, help_text='Index list of contributors', related_name='_logbooks_logbookpage_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='storypage',
            name='contributors',
            field=modelcluster.fields.ParentalManyToManyField(
                blank=True, help_text='Index list of contributors', related_name='_logbooks_storypage_contributors_+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]
