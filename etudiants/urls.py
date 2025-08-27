
from django.urls import path
from . import views

urlpatterns = [
    path('hpme?', views.home, name='etudiant_home'),
]
