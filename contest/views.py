from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.http.response import Http404, JsonResponse
from django.template.defaulttags import register

from .forms import *
from .models import *


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


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
        if request.method == 'POST' and profile.admin:
            if profile.team not in teams:
                team_contest = TeamContest(contest=contest, team=profile.team)
                team_contest.save()
                contest.team_number += 1
                contest.save()
                team_contests = TeamContest.objects.filter(contest=contest)
            else:
                print('You already participate')
        for entry in team_contests:
            teams.append(entry.team)

        return render(request, 'contest_info.html', {'contest': contest, 'teams': teams})

    print('Authentication error')
    return redirect('login')


def matches_page(request):
    if request.user.has_perms('contest.can_change_match', 'contest.can_delete_match'):
        if request.method == 'POST':
            matches_id = request.POST.getlist('match')
            for id in matches_id:
                match = Match.objects.get(id=id)
                match.delete()
        matches = Match.objects.all()
        return render(request, 'matches.html', {'matches': matches})

    print('Access denied')
    raise Http404


def match_management(request, match_id):
    if request.user.has_perms('contest.can_change_match'):
        try:
            match = Match.objects.get(id=match_id)
        except:
            print('Match not found!')
            raise Http404

        required_matches = match.required_matches.all()
        teams = match.teams.all()
        scores = {}
        for match_team in match.matchteam_set.all():
            scores[match_team.team.id] = match_team.score
        print(scores)
        available_teams = []
        for require_match in required_matches:
            for team in require_match.teams.all():
                available_teams.append(team)

        return render(request, 'match_management.html', {'required_matches': required_matches, 'teams': teams,
                                                         'scores': scores, 'available_teams': available_teams,
                                                         'match_id': match_id})

    print('Access denied')
    raise Http404


def match_management_delete_team(request, match_id):
    if request.user.has_perms('contest.can_change_match'):
        if request.method == 'POST':
            teams_id = request.POST.getlist('team')
            for team_id in teams_id:
                match_team = MatchTeam.objects.get(team=team_id, match=match_id)
                match_team.delete()

    return redirect('match_management', match_id)


def match_management_add_team(request, match_id):
    if request.user.has_perms('contest.can_change_match'):
        if request.method == 'POST':
            teams_id = request.POST.getlist('available_teams')
            try:
                match = Match.objects.get(id=match_id)
            except:
                print('Match not found!')
                raise Http404

            required_matches = match.required_matches.all()
            available_teams = []
            for require_match in required_matches:
                for team in require_match.teams.all():
                    available_teams.append(team)

            for team_id in teams_id:
                if team_id not in available_teams:
                    team = Team.objects.get(id=team_id)
                    print(match)
                    match_team = MatchTeam(team=team, match=match)
                    match_team.save()
                else:
                    print('Invalid data')

    return redirect('match_management', match_id)


def update_score(request, match_id, team_id):
    if request.user.has_perms('contest.can_change_match'):
        if request.method == 'POST':
            score = request.POST['score']
            try:
                match = Match.objects.get(id=match_id)
                team = Team.objects.get(id=team_id)
                match_team = MatchTeam.objects.get(team=team, match=match)
            except:
                print('Invalid data')
                raise Http404

            match_team.score = score
            match_team.save()
            print(match_team.score)

    return redirect('match_management', match_id)


def match_definition(request):
    if request.user.has_perm('contest.can_add_match'):
        if request.method == 'POST':
            form = MatchDefinitionForm(request.POST)
            if form.is_valid():
                contest = form.cleaned_data.get('contest')
                date_time = form.cleaned_data.get('date_time')
                level = form.cleaned_data.get('level')
                teams = form.cleaned_data.get('teams')
                required_matches = form.cleaned_data.get('required_matches')
                match = Match(contest=contest, date_time=date_time, level=level)
                match.save()
                try:
                    if len(required_matches) == 0:
                        for team in teams:
                            match_team = MatchTeam(match=match, team=team)
                            match_team.save()

                    else:
                        for required_match in required_matches:
                            match.required_matches.add(required_match.id)

                        required_teams = []
                        for required_match in match.required_matches.all():
                            for team in required_match.teams.all():
                                required_teams.append(team)

                        for team in teams:
                            if team in required_teams:
                                print(match)
                                match_team = MatchTeam(match=match, team=team)
                                match_team.save()
                            else:
                                print('Invalid form')
                                raise Http404
                except:
                    match.delete()

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


def get_teams(request):
    if request.user.has_perm('contest.can_add_match'):
        if request.method == 'GET':
            matches_id = request.GET.getlist('matches[]')
            contest_id = request.GET.get('contest')
            contest = Contest.objects.get(id=contest_id)
            teams = {}

            if len(matches_id) == 0:
                for team_contest in contest.teamcontest_set.all():
                    teams[str(team_contest.team.id)] = str(team_contest.team.name)

            else:
                for match_id in matches_id:
                    try:
                        match = Match.objects.get(id=match_id)
                        for team in match.teams.all():
                            teams[str(team.id)] = str(team.name)

                    except ValueError:
                        return JsonResponse({'status': 'failure', 'error': 'invalid input'})

            return JsonResponse({'status': 'success', 'teams': teams})

        else:
            return JsonResponse({'status': 'failure'})

    print('Access denied!')
    raise Http404


def get_matches(request):
    if request.user.has_perm('contest.can_add_match'):
        if request.method == 'GET':
            contest = request.GET['contest']
            date_time = request.GET['date_time']
            try:
                matches = Match.objects.filter(contest=contest, date_time__lt=date_time)
                matches_dict = {}
                for match in matches:
                    matches_dict[str(match.id)] = str(match)
                    print(match)
                return JsonResponse({'status': 'success', 'matches': matches_dict})
            except ValueError:
                return JsonResponse({'status': 'failure', 'error': 'invalid input'})
        else:
            return JsonResponse({'status': 'failure'})

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
