# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/9/2025
# Description: The views python file for the quotes application
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import random
import time
# Create your views here.

quotes = ["All the world's a stage, And all the men and women merely players",
"This above all: to thine own self be true",
"Brevity is the soul of wit",
]

images = ["https://upload.wikimedia.org/wikipedia/commons/2/21/William_Shakespeare_by_John_Taylor%2C_edited.jpg",
"https://www.nationalaffairs.com/storage/app/resized/8a4/63e/441/Valiunas-Thumbnail_resized_8a463e441ad50ad3bfbf14d718865390bfed5359.jpg",
"https://wilson.fas.harvard.edu/sites/g/files/omnuum9406/files/styles/hwp_1_1__1440x1440_scale/public/jeffreywilson/files/why_shakespeare_01.jpg?itok=IFGaCtcn",
]

def about(request):
    ''' respond to about page request which is a page with short biographical information 
    about the person whose quotes you are displaying, as well as a note about 
    the creator of this web application '''
    template_name = 'quotes/about.html'
    context =  {
        "time" : time.ctime(),
    }
    return render(request, template_name, context)

def quote(request):
    ''' respond to quote page request which select one of each of these at random, 
    and set them as context variables for use in the HTML template.. '''
    template_name = 'quotes/quote.html'
    context = {
        "time" : time.ctime(),
        "quote": random.choice(quotes),
        "image": random.choice(images),

    }
    return render(request, template_name, context)
def show_all(request):
    ''' respond to show_all page which will add the entire list of quotes and images 
    to the context data for the view. Finally, delegate presentation to the show_all.html 
    HTML template for display. '''
    template_name = 'quotes/show_all.html'
    context = {
        "time" : time.ctime(),
        "quotes": quotes,
        "images": images,

    }
    return render(request, template_name, context)