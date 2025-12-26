from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm


def landing_view(request):
    """Landing page - redirects to dashboard if logged in."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.is_admin():
            return redirect('backoffice:dashboard')
        return redirect('finance:dashboard')
    return render(request, 'accounts/landing.html')


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('finance:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.is_admin():
            return redirect('backoffice:dashboard')
        return redirect('finance:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'profile') and not user.profile.is_active:
                messages.error(request, 'Your account has been deactivated. Please contact an administrator.')
                return render(request, 'accounts/login.html')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect based on role
            if hasattr(user, 'profile') and user.profile.is_admin():
                return redirect('backoffice:dashboard')
            return redirect('finance:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def about_view(request):
    """About page explaining the app."""
    return render(request, 'accounts/about.html')

