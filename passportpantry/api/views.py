from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home(request):
    return HttpResponse("Hello, world. You're at the home page.")

@login_required
def profile(request):
    return HttpResponse("Requires Login. You're at the profile page.")
