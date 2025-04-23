from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import CustomUser, Booking

class CustomUserCreationForm(UserCreationForm):
    can_view = forms.BooleanField(required=False)
    can_upload = forms.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'password1', 'password2', 'can_view', 'can_upload')

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time_slot']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        } 