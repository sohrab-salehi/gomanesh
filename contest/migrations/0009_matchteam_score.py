# Generated by Django 2.0.5 on 2018-07-08 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0008_auto_20180708_0744'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchteam',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
