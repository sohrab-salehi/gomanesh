from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http.response import Http404
from django.db.models.query import QuerySet

from .forms import SignUpForm, TeamCreationForm, InviteForm
from .models import Contest, Team, Profile, Invitation


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.username = form.cleaned_data.get('email')
            user.profile.first_name = form.cleaned_data.get('first_name')
            user.profile.last_name = form.cleaned_data.get('last_name')
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def team_creation(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.team is None:
            if request.method == 'POST':
                form = TeamCreationForm(request.POST)
                if form.is_valid():
                    name = form.cleaned_data.get('name')
                    team = Team(name=name)
                    try:
                        team.contest = Contest.objects.get(activation=True)
                    except:
                        print("Doesn't find any active contest")
                        raise Http404
                    team.score = 0
                    team.save()
                    profile = request.user.profile
                    profile.team = team
                    profile.admin = True
                    profile.save()
                    return redirect('home')
            else:
                form = TeamCreationForm()

            return render(request, 'team_creation.html', {'form': form})
        else:
            print('You already have a team!')

    raise Http404


def team_management(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.team is None:
            print("This user doesn't have team yet.")
            raise Http404
        if profile.admin:
            team_member = Profile.objects.filter(team=profile.team)
            form = InviteForm()
            if request.method == 'POST':
                form = InviteForm(request.POST)
                if form.is_valid():
                    requested_profile = form.cleaned_data.get('profile')
                    if requested_profile not in team_member:
                        invitation = Invitation(team=profile.team, profile=requested_profile)
                        invitation.save()
                    else:
                        print('User already is in team!')
            invitations = Invitation.objects.filter(team=profile.team)
            return render(request, 'team_management.html', {'team_member': team_member, 'team': profile.team,
                                                            'form': form, 'invitations': invitations})
        else:
            print('Access denied!')
            raise Http404

    print('Authentication error')
    raise Http404


