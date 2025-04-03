from django.shortcuts import render

# Create your views here.

def go_home(request):
    return render(request, 'home.html')

def go_navbar(request):
    return render(request, 'navbar.html')