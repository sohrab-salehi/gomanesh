from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Contest(models.Model):
    name = models.CharField(max_length=80)
    date = models.DateField()
    place = models.TextField()
    description = models.TextField()
    type = models.CharField(max_length=50)
    team_number = models.IntegerField(default=0)
    poster = models.ImageField(null=True, blank=True)
    activation = models.BooleanField(default=True)

    def __str__(self):
        return '{} ({}): {}  ,Team number: {}'.format(self.name, self.type, self.date, self.team_number)


class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class TeamContest(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('team', 'contest'),)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    admin = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Match(models.Model):
    date_time = models.DateTimeField()
    level = models.CharField(max_length=50)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)
    teams = models.ManyToManyField(Team, through='MatchTeam', through_fields=('match', 'team'))

    class Meta:
        verbose_name_plural = "Matches"

    def __str__(self):
        return 'مسابقه تاریخ {} در رقابت {}'.format(self.date_time, self.contest.name)


class MatchTeam(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = (('team', 'match'),)


class Invitation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('team', 'profile'),)

    def __str__(self):
        return self.team.name + ' --> ' + self.profile.__str__()


class Resign(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    pending = models.BooleanField()

    class Meta:
        unique_together = (('team', 'profile'),)

    def __str__(self):
        status = 'Closed'
        if self.pending:
            status = 'Pending'
        return self.profile.__str__() + ' resign from ' + self.team.name + ' (' + status + ')'
