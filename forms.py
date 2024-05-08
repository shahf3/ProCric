# forms.py
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
import bootstrap_datepicker_plus.widgets as datepicker

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'first_name': forms.TextInput(attrs={'autocomplete': 'given-name'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'family-name'}),
        }

class CricketTeamForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    # players = forms.MultipleChoiceField(choices=[] , widget=forms.CheckboxSelectMultiple)
    class Meta:
        model = CricketTeam
        fields = ['name', 'players', 'country']
        widgets = {
            'name': forms.TextInput(attrs={'autocomplete': 'organization'}),
            'players': forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list', 'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        super(CricketTeamForm, self).__init__(*args, **kwargs)
        self.fields['players'].widget.attrs['class'] = 'checkbox-list'
        

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class TournamentForm(forms.ModelForm):
    country = forms.ModelChoiceField(queryset=Country.objects.all())
    teams = forms.ModelMultipleChoiceField(queryset=CricketTeam.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Tournament
        fields = ['name', 'start_date', 'end_date', 'country', 'teams']
        widgets = {
            'start_date': datepicker.DatePickerInput(options={'format': 'DD/MM/YYYY'}),
            'end_date': datepicker.DatePickerInput(options={'format': 'DD/MM/YYYY'}),
        }

    def __init__(self, *args, **kwargs):
        super(TournamentForm, self).__init__(*args, **kwargs)

        # Disable the teams field initially
        self.fields['teams'].widget.attrs['disabled'] = 'disabled'

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                teams_queryset = CricketTeam.objects.filter(country_id=country_id)

                if 'tournament' in self.data:
                    tournament_id = int(self.data.get('tournament'))
                    teams_queryset = teams_queryset.filter(tournaments__id=tournament_id)

                self.fields['teams'].queryset = teams_queryset
                # Enable the teams field after setting the queryset
                self.fields['teams'].widget.attrs.pop('disabled', None)

            except (ValueError, TypeError):
                pass
class TeamSelectionForm(forms.ModelForm):
    class Meta:
        model = CricketTeam
        fields = ['name']

class MatchForm(forms.ModelForm):
    # Select teams from multiple choice field
    team1 = forms.ModelChoiceField(queryset=CricketTeam.objects.all())
    team2 = forms.ModelChoiceField(queryset=CricketTeam.objects.all())

    date_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    class Meta:
        model = Match
        fields = ['team1', 'team2', 'date_time']
    
class MatchPlayedForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['played', 'winner']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'batting_action', 'bowling_action')

class ProfilePictureForm(forms.ModelForm):
    profile_picture = forms.ImageField(label='Profile Picture')

    class Meta:
        model = CustomUser
        fields = ('profile_picture', )

class ContactUsForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    from_email = forms.EmailField()