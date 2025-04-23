from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'  # Add URL namespacing

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('password/', views.change_password, name='change_password'),
    path('booking/create/', views.create_booking, name='create_booking'),
] 