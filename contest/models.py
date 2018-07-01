from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


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
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = (('profile', 'contest'),)

    def __str__(self):
        return self.profile.first_name + ' ' + self.profile.last_name


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
