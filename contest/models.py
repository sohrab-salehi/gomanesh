from django.db import models
from django.contrib.auth.models import User


class Contest(models.Model):
    name = models.CharField(max_length=80)
    date = models.DateField()
    place = models.TextField()
    description = models.TextField()
    type = models.CharField(max_length=50)
    poster = models.ImageField(null=True, blank=True)

    def __str__(self):
        return 'Contest: {}'.format(self.date)


class Team(models.Model):
    name = models.CharField(max_length=50)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = (('name', 'contest'),)

    def __str__(self):
        return self.name


class Group(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    teams = models.ManyToManyField(Team, through='GroupTeam', through_fields=('group', 'team'))


class GroupTeam(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)


class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('user', 'contest'),)

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Match(models.Model):
    date_time = models.DateTimeField()
    level = models.CharField(max_length=50)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    teams = models.ManyToManyField(Team, through='MatchTeam', through_fields=('match', 'team'))

    class Meta:
        verbose_name_plural = "Matches"


class MatchTeam(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
