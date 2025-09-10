from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
# Create your views here.
import time

def home(request):
    ''' respond to home request'''
    response_text = f'''
    <html>
    <h1> hello, world <h1>
    the current time is {time.ctime()}.
    <html>
    '''
    return HttpResponse(response_text)

def home_page(request):
    ''' respond to home page request '''
    template_name = 'hw/home.html'
    return render(request, template_name)

def about(request):
    ''' respond to home page request '''
    template_name = 'hw/about.html'
    return render(request, template_name)