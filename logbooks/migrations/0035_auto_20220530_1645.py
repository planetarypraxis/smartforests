# Generated by Django 3.2.13 on 2022-05-30 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('logbooks', '0034_auto_20220309_1812'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contributorpage',
            options={'verbose_name': 'Contributor', 'verbose_name_plural': 'Contributors'},
        ),
        migrations.AlterModelOptions(
            name='episodepage',
            options={'verbose_name': 'Radio Episode', 'verbose_name_plural': 'Radio Episodes'},
        ),
    ]
