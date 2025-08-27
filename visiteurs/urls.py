from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login-modal/', views.login_modal, name='login_modal'),
    path('register-modal/', views.register_modal, name='register_modal'),
]
