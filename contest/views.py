from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http.response import Http404

from .forms import *
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
                    team.score = 0
                    team.save()
                    profile = request.user.profile
                    profile.team = team
                    profile.admin = True
                    profile.save()
                    return redirect('team_management')
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
                        try:
                            invitation.save()
                        except:
                            print('You sent invitation before')
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
                    profile.admin = False
                    profile.save()
                    new_admin.admin = True
                    new_admin.save()
                    return redirect('team_management')
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


def contests_page(request):
    contests = Contest.objects.filter(activation=True)
    return render(request, 'contests.html', {'contests': contests})


def contest_info(request, contest_id):
    if request.user.is_authenticated:
        profile = request.user.profile
        try:
            contest = Contest.objects.get(id=contest_id)
        except:
            print('Contest not found!')
            raise Http404
        team_contests = TeamContest.objects.filter(contest=contest)
        teams = []
        for entry in team_contests:
            teams.append(entry.team)
        if request.method == 'POST' and profile.admin:
            if profile.team not in teams:
                team_contest = TeamContest(contest=contest, team=profile.team)
                team_contest.save()
                contest.team_number += 1
                contest.save()
                teams = TeamContest.objects.filter(contest=contest)
            else:
                print('You already participate')

        return render(request, 'contest_info.html', {'contest': contest, 'teams': teams})

    print('Authentication error')
    return redirect('login')


def match_management(request):
    if request.user.has_perms('contest.can_change_match'):
        print('ok')

    print('Access denied')


def match_definition(request):
    if request.user.has_perm('contest.can_add_match'):
        if request.method == 'POST':
            form = MatchDefinitionForm(request.POST)
            if form.is_valid():
                contest = form.cleaned_data.get('contest')
                date_time = form.cleaned_data.get('date_time')
                level = form.cleaned_data.get('level')
                match = Match(contest=contest, date_time=date_time, level=level)
                match.save()
                teams = form.cleaned_data.get('teams')
                for team in teams:
                    match_team = MatchTeam(match=match, team=team)
                    match_team.save()
                print('Success')
                return redirect('home')
            else:
                print('Invalid form')
                raise Http404
        else:
            form = MatchDefinitionForm()
            return render(request, 'match_definition.html', {'form': form})

    print('Access denied!')
    raise Http404


def dashboard(request):
    if request.user.is_authenticated:
        profile = request.user.profile
        team = profile.team
        print(team)
        matches = team.match_set.all()
        contests = TeamContest.objects.filter(team=team)
        return render(request, 'dashboard.html', {'matches': matches, 'contests': contests, 'team': team})

    print('Authentication error')
    return redirect('login')
