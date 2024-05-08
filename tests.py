# tests.py
from django.test import TestCase
from django.urls import reverse
from .models import CustomUser, CricketTeam, Match, Tournament
from .forms import CustomUserCreationForm, CricketTeamForm, MatchForm, TournamentForm
import cities_light.models as cities

class ModelTestCase(TestCase):
    def setUp(self):
        ireland_country = cities.Country.objects.create(name='Ireland', code2='IE', code3='IRL')
        # Create test instances for models
        self.user = CustomUser.objects.create(username='testuser', email='test@example.com')
        self.team = CricketTeam.objects.create(name='Test Team', captain=self.user, country=cities.Country.objects.get(name='Ireland'))
        self.tournament = Tournament.objects.create(name='Test Tournament', start_date='2024-01-01', end_date='2024-02-01', country=cities.Country.objects.get(name='Ireland'))

    def test_user_model(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_team_model(self):
        self.assertEqual(str(self.team), 'Test Team')

    def test_tournament_model(self):
        self.assertEqual(str(self.tournament), 'Test Tournament')

    def test_match_model(self):
        match = Match.objects.create(tournament=self.tournament, team1=self.team, team2=self.team, date_time='2024-01-15 12:00', location='Test Location')
        self.assertEqual(str(match), 'Test Team vs Test Team - 2024-01-15 12:00')

class FormTestCase(TestCase):

    def tearDown(self):
        CustomUser.objects.all().delete()
        CricketTeam.objects.all().delete()
        Tournament.objects.all().delete()

    def setUp(self):
        ireland_country = cities.Country.objects.create(name='Ireland', code2='IE', code3='IRL')
        # Create a CustomUser instance or any other required setup
        self.CustomUser = CustomUser.objects.create(username='testuser', email='test@example.com')
        self.team = CricketTeam.objects.create(name='Test Team', captain=self.CustomUser, country=cities.Country.objects.get(name='Ireland'))
       
        self.tournament = Tournament.objects.create(name='Test Tournament', start_date='2024-01-01', end_date='2024-02-01', country=cities.Country.objects.get(name='Ireland')) 

    def test_user_creation_form_valid(self):
        form_data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'first_name': 'Test2',
            'last_name': 'User2',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form is not valid. Errors: {form.errors}")

    def test_user_creation_form_invalid(self):
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'first_name': 'Test',
            'last_name': 'User',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_cricket_team_form_invalid(self):
        form_data = {
            'name': 'Test Team',
            'captain': CustomUser.objects.create(username='captain', email='captain@example.com'),
            'players': [],
            'country': '102',
        }
        form = CricketTeamForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_tournament_form_valid(self):
        form_data = {
            'name': 'Test Tournament',
            'start_date': '01/01/2024',
            'end_date': '02/01/2024',
            'country': cities.Country.objects.get(name='Ireland').id,
            'teams': [self.team],
        }
        form = TournamentForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form is not valid. Errors: {form.errors}")

    def test_tournament_form_invalid(self):
        form_data = {
            'name': 'Test Tournament',
            'start_date': '01/01/2024',
            'end_date': '02/01/2024',
            'country': '102',
            'teams': [], 
        }
        form = TournamentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_match_form_valid(self):
        form_data = {
            'tournament': self.tournament.id,
            'team1': self.team.id,
            'team2': self.team.id,
            'date_time': '2024-01-15T12:00',
            'location': 'Test Location',
        }
        form = MatchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_match_form_invalid(self):
        form_data = {
            'tournament': self.tournament.id,
            'team1': self.team.id,
            'team2': self.team.id,
            'date_time': 'invalid-date-time',
            'location': 'Test Location',
        }
        form = MatchForm(data=form_data)
        self.assertFalse(form.is_valid())
