# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    company = forms.CharField(max_length=100)
    company_size = forms.CharField(max_length=50)
    seo_proficiency = forms.CharField(max_length=50)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['email', 'company', 'company_size', 'seo_proficiency', 'password1', 'password2']
