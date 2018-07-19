from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Team, Invitation, Match


class SignUpForm(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    phone_number = forms.CharField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2', )


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ('name',)


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ('profile',)


class MatchDefinitionForm(forms.ModelForm):
    matches = forms.ModelMultipleChoiceField(queryset=Match.objects.all())

    class Meta:
        model = Match
        fields = ('contest', 'date_time', 'level', 'matches', 'teams')
