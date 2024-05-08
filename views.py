
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import CustomAuthenticationForm
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from random import shuffle
from datetime import datetime, timedelta
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .forms import CustomUserChangeForm
from django.views.decorators.http import require_POST

@require_POST
def check_player_existence(request):
    print(request.POST)
    email = request.POST.get('email', None)

    if email:
        # Check if a user with the given email exists
        user_exists = CustomUser.objects.filter(email=email).first()

        if user_exists:
            return JsonResponse({'exists': True, 'player_id': user_exists.id})
        else:
            return JsonResponse({'exists': False, 'player_id': None})

    return JsonResponse({'error': 'Email parameter is missing'}, status=400)

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        try:
            if form.is_valid():
                form.save()
                return redirect('login')
            else:
                print(form.errors)
        except Exception as e:
            print(f"An error occurred during registration: {e}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def create_team(request):
    if request.method == 'POST':
        form = CricketTeamForm(request.POST)
        print(form.errors)
        if form.is_valid():
            team = form.save(commit=False)
            team.captain = request.user

            if 'country' in request.POST:
                try:
                    country_id = int(request.POST.get('country'))
                    team.country = Country.objects.get(pk=country_id)
                except (ValueError, TypeError, Country.DoesNotExist):
                    pass

            team.save()
            form.save_m2m()
            return redirect('team_list')
    else:
        form = CricketTeamForm()

    return render(request, 'create_team.html', {'form': form})

@login_required
def team_list(request):
    query = request.GET.get('q')
    teams = CricketTeam.objects.all()

    if query:
        # If there is a search query, filter the teams based on name and captain username
        teams = teams.filter(Q(name__icontains=query) | Q(captain__username__icontains=query))

    return render(request, 'team_list.html', {'teams': teams, 'query': query})

@login_required
def tournament_list(request):
    user = request.user
    all_tournaments = Tournament.objects.all()
    user_tournaments = user.tournaments.all()

    if request.method == 'POST':
        show_user_tournaments = bool(request.POST.get('user_tournaments'))
        if show_user_tournaments:
            tournaments = user_tournaments
        else:
            tournaments = all_tournaments
    else:
        tournaments = all_tournaments
        show_user_tournaments = False

    return render(request, 'tournament_list.html', {'tournaments': tournaments, 'show_user_tournaments': show_user_tournaments})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)

                return redirect('home')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            match = form.save()
            return redirect('match_detail', match_id=match.id)
    else:
        form = MatchForm()
    return render(request, 'create_match.html', {'form': form})

def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return render(request, 'match_detail.html', {'match': match})

@login_required
def create_tournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST)
        if form.is_valid():
            tournament = form.save(commit=False)
            tournament.save()
            form.save_m2m()

            return redirect('tournament_details', tournament_id=tournament.id)
    else:
        form = TournamentForm()

    return render(request, 'create_tournament.html', {'form': form})

def tournament_details(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    try:
        schedule = json.loads(tournament.schedule)
    except TypeError:
        print("nothing in database")
        schedule = {'matches': []}
    if request.method == 'POST':
        match_form = MatchForm(request.POST)
        MatchForm.tournament_id = tournament_id
        if match_form.is_valid():
            match_data = match_form.cleaned_data
            match_number = len(schedule['matches']) + 1
            print(match_data)
            schedule['matches'].append({
                'team1': match_data['team1'].name,
                'team2': match_data['team2'].name,
                'date_time': match_data['date_time'].isoformat(),
                'match_number': match_number,
            })
            print(schedule)
            tournament.schedule = json.dumps(schedule)
            tournament.save()
            new_match = Match(
                tournament=tournament,
                team1=match_data['team1'],
                team2=match_data['team2'],
                date_time=match_data['date_time'],
                match_number=match_number,
            )
            new_match.save()
            return redirect('tournament_details', tournament_id=tournament.id)
        else:
            print(match_form.errors)
    else:
        match_form = MatchForm()

    participating_teams = tournament.teams.all()
    all_teams = CricketTeam.objects.filter(teamstatistics__tournament__id=tournament.id).values_list('name', flat=True)
    matches = Match.objects.filter(tournament_id=tournament)
    matches_list = [match.match_number for match in matches if match.played == True]
    print(matches_list)
    return render(request, 'tournament_details.html', {'tournament': tournament, 'all_teams': all_teams, 'schedule': schedule, 'match_form': match_form, 'matches': matches_list})

@login_required
def delete_selected_teams(request):
    if request.method == 'POST':
        team_ids_to_delete = request.POST.getlist('teams_to_delete')

        if team_ids_to_delete:
            for team_id in team_ids_to_delete:
                team = get_object_or_404(CricketTeam, id=team_id)

                if request.user == team.captain:
                    team.delete()
                    messages.success(request, 'Selected teams deleted successfully.')
                else:
                    messages.error(request, f'You do not have permission to delete team: {team.name}.')

            return HttpResponseRedirect(reverse('team_list'))

        else:
            messages.warning(request, 'No teams selected for deletion.')

    return HttpResponseRedirect(reverse('team_list'))

def logout_view(request):
    logout(request)
    return redirect('home')

def about_us(request):
    return render(request, 'about-us.html')

def change_password(request):
    return render(request, 'change_password.html')

def my_profile(request):
    return render(request, 'my_profile.html')

def about_us(request):
    return render(request, 'about-us.html')

def references(request):
    return render(request, 'references.html')

def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = form.cleaned_data['from_email']

            try:
                send_mail(subject, message, from_email, ['alishhafaizan12@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('home')
    else:
        form = ContactUsForm()

    return render(request, 'contact-us.html', {'form': form})
        
def my_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('my_profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'my_profile.html', {'form': form})

def upload_profile_pic(request):
    if request.method == 'POST':
        profile_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if profile_form.is_valid():
            print(profile_form.cleaned_data['profile_picture'])
            profile_form.save()
            print('Form is valid')
            return redirect('my_profile')
    else:
        profile_form = ProfilePictureForm(instance=request.user)
    return render(request, 'change_profile_pic.html', {'form': profile_form})

def scoring(request, match_id, tournament_id):
 
    team1 = Match.objects.get(match_number=match_id, tournament=tournament_id).team1_id
    team2 = Match.objects.get(match_number=match_id, tournament=tournament_id).team2_id
    print(team1, team2)

    # Get or create TeamStatistics objects for both teams in the tournament
    team1_stats = TeamStatistics.objects.get(id=team1)
    team2_stats = TeamStatistics.objects.get(id=team2)

    # Update statistics based on the match result
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))

            if data['winner'] == 'team1':
                team1_stats.won += 1
                team2_stats.lost += 1
            else:
                team2_stats.won += 1
                team1_stats.lost += 1
            
            team1_stats.save()
            team2_stats.save()
            
            match_instance = Match.objects.get(match_number=match_id, tournament=tournament_id)
            match_instance.played = True
            match_instance.save()

        except Exception as e:
            print(f"An error occurred while updating statistics: {e}")
    context = {
        'match_id': match_id,
        'tournament_id': tournament_id,
    }
    return render(request, 'scoring.html', {'form': context})

def finalize_tournament(request, tournament_id):
    tournament = Tournament.objects.get(pk=tournament_id)

    if request.method == 'POST':
        # Parse the JSON schedule string into a Python dictionary
        schedule_data = json.loads(tournament.schedule)
        print(schedule_data)
        print(type(schedule_data))

        # Iterate through the schedule and create a Match instance for each match
        for match_data in schedule_data['matches']:
            match_form = MatchForm({
                'tournament': tournament,
                'team1': match_data['team1'],
                'team2': match_data['team2'],
                'date_time': match_data['date_time'],
            })

            if match_form.is_valid():
                match_form.save()
            else:
                # Handle form validation errors
                messages.error(request, 'Error creating matches. Please check the form data.')

        # Update the tournament as finalized
        tournament.finalized = True
        tournament.save()

        messages.success(request, 'Tournament finalized successfully!')
        return redirect('tournament_details', tournament_id=tournament.id, )

    context = {
        'tournament': tournament,
        'match_form': MatchForm(),
    }

    return render(request, 'tournament_details.html', context)

def tournament_results(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    team_statistics_data = TeamStatistics.objects.filter(tournament=tournament)
    for team_statistic in team_statistics_data:
        points = 2 * team_statistic.won
    return render(request, 'tournament_results.html', {'tournament': tournament, 'team_statistics_data': team_statistics_data, 'points': points})