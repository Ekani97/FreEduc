from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def home(request):
    return render (request, 'index.html')

def login(request):
    return render (request, 'login.html')
def inscription(request):
    return render (request, 'inscription.html')
