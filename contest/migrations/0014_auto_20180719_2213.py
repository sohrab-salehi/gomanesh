# Generated by Django 2.0.5 on 2018-07-19 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0013_match_required_matches'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='required_matches',
            field=models.ManyToManyField(blank=True, related_name='_match_required_matches_+', to='contest.Match'),
        ),
        migrations.AlterField(
            model_name='match',
            name='teams',
            field=models.ManyToManyField(blank=True, through='contest.MatchTeam', to='contest.Team'),
        ),
    ]