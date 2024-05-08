from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django import forms
from cities_light.models import City, Country
from django.conf import settings
import bootstrap_datepicker_plus as datepicker
from django.db.models import Sum
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db import transaction

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    tournaments = models.ManyToManyField('Tournament', related_name='players', blank=True)
    BATTING_CHOICES = [
        ('left', 'Left-Handed Batter'),
        ('right', 'Right-Handed Batter'),
    ]
    BOWLING_CHOICES = [
        ('left', 'Left-Handed Bowler'),
        ('right', 'Right-Handed Bowler'),
    ]
    batting_action = models.CharField(max_length=255, choices=BATTING_CHOICES, null=True, blank=True)
    bowling_action = models.CharField(max_length=255, choices=BOWLING_CHOICES, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    profile_picture = models.ImageField(default='default_profile_picture.jpg', upload_to='media/', null=True, blank=True, unique=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        related_query_name='customuser',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    def __str__(self):
        return self.username

class CricketTeam(models.Model):
    name = models.CharField(max_length=255)
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='captain_teams')
    players = models.ManyToManyField(CustomUser, related_name='teams')
    # city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.name

class Match(models.Model):
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    match_number = models.PositiveIntegerField()
    team1 = models.ForeignKey(CricketTeam, on_delete=models.CASCADE, related_name='team1_matches')
    team2 = models.ForeignKey(CricketTeam, on_delete=models.CASCADE, related_name='team2_matches')
    date_time = models.DateTimeField()
    winner = models.ForeignKey(CricketTeam, on_delete=models.CASCADE, null=True, blank=True, related_name='winning_matches')
    played = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.team1} vs {self.team2} - {self.date_time}"

class Tournament(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    schedule = models.TextField(default='{"matches": []}')
    teams = models.ManyToManyField(CricketTeam, related_name='tournaments')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, default=1)
    #city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    teams = models.ManyToManyField(CricketTeam, through='TeamStatistics')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, default=1)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)

    finalized = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class TeamStatistics(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    team = models.ForeignKey(CricketTeam, on_delete=models.CASCADE)
    

    won = models.PositiveIntegerField(default=0)
    lost = models.PositiveIntegerField(default=0)
    draw = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)

class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['name', 'start_date', 'end_date'] 
        