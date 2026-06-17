from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Rating,Order


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }        
        