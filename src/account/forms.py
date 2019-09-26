from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import User, Account
from django.core.validators import RegexValidator
import re


class UserCreationForm(forms.ModelForm):

    first_name = forms.CharField(label="First name", widget=forms.TextInput(
        attrs={'placeholder': 'First Name',
               'class': 'is-medium'
               }))
    last_name = forms.CharField(label="Last name",  widget=forms.TextInput(
        attrs={'class': 'is-small'}
    ))
    email = forms.EmailField(label="Email", required=True)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)

    def clean_email(self):
        data = self.cleaned_data['email']
        return data.lower()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    COUNTRY_CHOICES = (
        ('Nigeria', 'Nigeria'),
        ('Ghana', 'Ghana'),
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")
    phone = forms.CharField(
        validators=[phone_regex], max_length=13, required=True)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        pattern = r"((?:\+234|234|0|)(?:8|7|9)(?:0|1)(?:\d{8}))"
        match = re.fullmatch(pattern, phone)

        if not match:
            raise forms.ValidationError("Enter a valid phone number.")
        return phone

    class Meta:
        model = Account
        fields = ('phone', 'country', )


class AuthenticationForm(AuthenticationForm):
    def clean_username(self):
        data = self.cleaned_data['username']
        return data.lower()
