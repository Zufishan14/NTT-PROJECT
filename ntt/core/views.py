from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import CustomUserCreationForm, BookingForm
from .models import Booking

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'core/index.html')

@login_required
def home(request):
    if request.user.can_view:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(created_by=request.user)
    return render(request, 'core/home.html', {'bookings': bookings})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now login.')
            return redirect('core:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('core:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'core/change_password.html', {'form': form})

@login_required
def create_booking(request):
    if not request.user.can_upload:
        messages.error(request, 'You do not have permission to create bookings.')
        return redirect('core:home')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.created_by = request.user
            booking.save()
            messages.success(request, 'Booking created successfully.')
            return redirect('core:home')
    else:
        form = BookingForm()
    return render(request, 'core/create_booking.html', {'form': form})