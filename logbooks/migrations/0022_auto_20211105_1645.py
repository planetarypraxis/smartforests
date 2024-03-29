# Generated by Django 3.2.9 on 2021-11-05 16:45

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('smartforests', '0007_auto_20211104_1444'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wagtailcore', '0066_collection_management_permissions'),
        ('logbooks', '0021_auto_20211104_1303'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContributorsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE,
                 parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='ContributorPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE,
                 parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('geographical_location', models.CharField(
                    blank=True, max_length=250, null=True)),
                ('coordinates', django.contrib.gis.db.models.fields.PointField(
                    blank=True, null=True, srid=4326)),
                ('byline', models.CharField(blank=True, max_length=1000, null=True)),
                ('bio', wagtail.fields.RichTextField(blank=True, null=True)),
                ('avatar', models.ForeignKey(blank=True, null=True,
                 on_delete=django.db.models.deletion.SET_NULL, to='smartforests.cmsimage')),
                ('user', models.OneToOneField(blank=True, null=True,
                 on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Location',
                'verbose_name_plural': 'Locations',
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
