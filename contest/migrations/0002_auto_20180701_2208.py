# Generated by Django 2.0.5 on 2018-07-01 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='activation',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='player',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]
