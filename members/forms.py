from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import MyUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=255, required=True)
    company_name = forms.CharField(max_length=255, required=True)
    company_size = forms.IntegerField(required=True)

    class Meta:
        model = MyUser
        fields = ['email', 'name', 'company_name', 'company_size', 'password1', 'password2']



class SignupForm(UserCreationForm):  
    email = forms.EmailField(max_length=200, help_text='Required')  
    class Meta:  
        model = User  
        fields = ('username', 'email', 'password1', 'password2')  