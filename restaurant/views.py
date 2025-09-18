# File: views.py
# Author: Run Liu (lr0826@bu.edu), 9/16/2025
# Description: The views python file for the restaurant application

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import time
import random
img_url = "https://console.kr-asia.com/wp-content/uploads/2024/01/Mixue-Bingcheng-Leida-Finance.jpg"
MENU = {
    "Lemonwater": ("Lemon Water", 4.00),
    "Milktea": ("Bubble Milk Tea", 5.00),
    "Juice": ("Big Juicy Juice", 6.00),
    "Gmilktea": ("Green Tea Milk Tea", 2.00),
    "special": ("Special", 0.00),
}
SPECIAL = ["Random Chemical Compound That Gives you Cancer",
"Sugar",
"MSG",
"A lot of Sugar"
]
def main(request):
    ''' directs to the the page with basic information about 
    the restaurant. the main page should include the name, location, 
    hours of operation (displayed as a list or table), and one or more photos 
    appropriate to such a page. '''
    template_name = 'restaurant/main.html'
    context =  {
        "time" : time.ctime(),
        "image" : img_url,
    }
    return render(request, template_name, context)

def order(request):
    ''' directs to the view for the ordering page. This view will 
    need to create a “daily special” item (choose randomly from a list), 
    and add it to the context dictionary for the page.'''
    template_name = 'restaurant/order.html'
    context =  {
        "time" : time.ctime(),
        "special" : random.choice(SPECIAL)
    } 
    return render(request, template_name, context)


def confirmation(request):
    '''directs to the confirmation page to display after the order is placed. 
    The confirmation page will display which items were ordered, the customer 
    information, and the expected time at which the order will be ready 
    (a time to be determined randomly, but within 30-60 minutes of the current 
    ate/time).
    '''
    template = 'restaurant/confirmation.html'
    ordered_items = []
    total = 0.0

    # Regular menu items and special
    for field, (label, price) in MENU.items():
        if request.POST.get(field):  # present in POST
            ordered_items.append({"name": label, "price": price})
            total += price
    # 2) Customer info + special instructions
    customer = {
        "name": request.POST['name'],
        "phone": request.POST['phone'],
        "email": request.POST['email'],
    }
    special_instructions = request.POST['special_instructions']

    # 3) Ready time: random 30–60 minutes from now
    minutes = random.randint(30, 60)
    ready_at = time.ctime(time.time() + minutes * 60)

    context = {
        "items": ordered_items,
        "total": round(total, 2),
        "customer": customer,
        "special_instructions": special_instructions,
        "ready_at": ready_at,    
        "time": time.ctime,
    }

    return render(request, template, context)
    

        
        
    
    
