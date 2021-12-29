from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect

from .models import CarModel, CarMake
from .restapis import (
    get_dealers_from_cf,
    get_dealer_by_state_or_id,
    get_dealer_reviews_from_cf,
    post_request,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def index(request):
    return render(request, "djangoapp/index.html")


# Create an `about` view to render a static about page
def about(request):
    return render(request, "djangoapp/about.html")


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, "djangoapp/contact.html")


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context["message"] = "Invalid username or password."
            return render(request, "djangoapp/user_login.html", context)
    else:
        return render(request, "djangoapp/user_login.html", context)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect("djangoapp:index")


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, "djangoapp/registration.html", context)
    elif request.method == "POST":
        # Check if user exists
        username = request.POST["username"]
        password = request.POST["psw"]
        first_name = request.POST["firstname"]
        last_name = request.POST["lastname"]
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password,
            )
            login(request, user)
            context["message"] = "Registration was successful."
            context["is_success"] = True
            return render(request, "djangoapp/registration.html", context)
        else:
            context["message"] = "User already exists."
            return render(request, "djangoapp/registration.html", context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://b66bd5c1.us-south.apigw.appdomain.cloud/api/dealership"
        dealerships = get_dealers_from_cf(url)

        # dealerships = get_dealer_by_state_or_id(url, state="CA", dealerId=None)
        # dealerships = get_dealer_by_state_or_id(url, state=None, dealerId=1)

        dealer_names = " ".join([dealer.short_name for dealer in dealerships])
        context["dealer_names"] = dealer_names
        context["dealerships"] = dealerships
        return render(request, "djangoapp/index.html", context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://b66bd5c1.us-south.apigw.appdomain.cloud/api/review"
        # Get reviews from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
        for review in reviews:
            context["dealership"] = review.dealership
        context["reviews"] = reviews
        print("context")
        print(context)
        return render(request, "djangoapp/dealer_details.html", context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    context = {}
    review = dict()
    json_payload = dict()

    review["time"] = datetime.utcnow().isoformat()

    if request.method == "GET":
        url = "https://b66bd5c1.us-south.apigw.appdomain.cloud/api/dealership"

        dealerships = get_dealer_by_state_or_id(url, state=None, dealerId=dealer_id)
        context["dealerships"] = dealerships[0]
        context["dealer_id"] = dealer_id

        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars

        return render(request, "djangoapp/add_review.html", context)

    if request.method == "POST":
        print(request.POST)
        car = CarModel.objects.get(id=int(request.POST["car"]))
        review["review"] = request.POST["review_text"]
        review["name"] = request.POST["name"]
        review["purchase"] = request.POST["purchase"]
        review["purchase_date"] = request.POST["purchase_date"]
        review["car_make"] = car.make.name 
        review["car_model"] = car.name 
        review["car_year"] = car.year.strftime("%Y") 
        review["dealership"] = int(request.POST["dealership"])

        id=request.POST["dealership"]

        json_payload["review"] = review

        url = "https://b66bd5c1.us-south.apigw.appdomain.cloud/api/review"

        reviews = post_request(url, json_payload=json_payload)
        
        context["reviews"] = reviews
        return redirect("/djangoapp/dealer/" + id)
