from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http.response import Http404
from django.db.models.query import QuerySet

from .forms import SignUpForm, TeamCreationForm, InviteForm
from .models import *


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
            return redirect('team_management')

    print('Authentication error')
    return redirect('login')


def team_delete(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.admin:
            if profile.team is None:
                print("You doesn't have any team")
                return redirect('team_creation')
            else:
                if request.method == 'POST':
                    Team.objects.get(id=request.user.profile.team.id).delete()
                    return redirect('home')

                return render(request, 'team_delete.html')
        else:
            print('Access denied!')
            raise Http404

    print('Authentication error')
    return redirect('login')


def team_management(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.team is None:
            print("This user doesn't have team yet.")
            raise Http404
        else:
            team_member = Profile.objects.filter(team=profile.team)
            resign_requests = Resign.objects.filter(team=profile.team)
            try:
                user_resign_request = Resign.objects.get(profile=profile)
            except:
                user_resign_request = ''
            form = InviteForm()
            if request.method == 'POST':
                form = InviteForm(request.POST)
                if form.is_valid():
                    requested_profile = form.cleaned_data.get('profile')
                    if requested_profile not in team_member and requested_profile.team is None:
                        invitation = Invitation(team=profile.team, profile=requested_profile)
                        invitation.save()
                    else:
                        print('User has a team!')
            invitations = Invitation.objects.filter(team=profile.team)
            return render(request, 'team_management.html', {'team_member': team_member, 'team': profile.team,
                                                            'form': form, 'invitations': invitations,
                                                            'resign_requests': resign_requests,
                                                            'user_resign_request': user_resign_request})

    print('Authentication error')
    return redirect('login')


def delete_member(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.admin:
            if profile.team is None:
                print("You doesn't have any team")
                return redirect('team_creation')
            else:
                if request.method == 'POST':
                    members_id = request.POST['member']
                    for id in members_id:
                        member = Profile.objects.get(id=id)
                        if not member.admin:
                            member.team = None
                    return redirect('team_management')
                else:
                    return redirect('team_management')
        else:
            print('Access denied!')
            raise Http404

    print('Authentication error')
    return redirect('login')


def invitation_page(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.team is None:
            if request.method == 'POST':
                profile.team = Team.objects.get(name=request.POST['team'])
                profile.save()
                Invitation.objects.filter(profile=profile).delete()
                return redirect('team_management')
            else:
                invitations = Invitation.objects.filter(profile=profile)
                return render(request, 'invitation.html', {'invitations': invitations})
        else:
            print('User has a team!', profile.team, profile)
            raise Http404

    print('Authentication error')
    return redirect('login')


def change_admin(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.team is None:
            print("User doesn't have a team!", profile.team, profile)
            raise Http404
        else:
            if profile.admin:
                team_member = Profile.objects.filter(team=profile.team)
                if request.method == 'POST':
                    new_admin = Profile.objects.get(user__id=request.POST['profile_id'])
                    new_admin.admin = True
                    profile.admin = False
                    new_admin.save()
                    profile.save()
                    return redirect('home')
                else:
                    return render(request, 'change_admin.html', {'team_member': team_member})
            else:
                print('Access denied!')
                raise Http404

    print('Authentication error')
    return redirect('login')


def resign_request(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.team is None:
            print("User doesn't have a team!", profile.team, profile)
            raise Http404
        else:
            if profile.admin:
                print("Admin can't resign")
                return redirect('team_management')
            else:
                resign = Resign(team=profile.team, profile=profile, pending=True)
                resign.save()
                return redirect('team_management')

    print('Authentication error')
    return redirect('login')


def accept_resign(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile.admin:
            if profile.team is None:
                print("You doesn't have any team")
                return redirect('team_creation')
            else:
                if request.method == 'POST':
                    resigns_id = request.POST['resign']
                    for id in resigns_id:
                        resign = Resign.objects.get(id=id)
                        resigned_memeber = resign.profile
                        resigned_memeber.team = None
                        resigned_memeber.save()
                        resign.delete()
                    return redirect('team_management')
                else:
                    return redirect('team_management')
        else:
            print('Access denied!')
            raise Http404

    print('Authentication error')
    return redirect('login')
