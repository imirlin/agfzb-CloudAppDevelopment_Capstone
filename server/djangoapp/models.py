from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.name + " (" + self.description + ")"


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    car_makes = models.ManyToManyField(CarMake)
    name = models.CharField(max_length=100, primary_key=True)
    dealer_id = models.IntegerField()
    type = models.CharField(
        max_length=48, choices=[("Sedan", "Sedan"), ("SUV", "SUV"), ("WAGON", "WAGON")]
    )
    year = models.DateField(null=True)

    def __str__(self):
        return self.name + " (" + self.type + ")"


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:
    def __init__(
        self, id, city, st, state, address, zip, lat, long, short_name, full_name
    ):
        self.id = id
        self.city = city
        self.state = state
        self.st = st
        self.address = address
        self.zip = zip
        self.lat = lat
        self.long = long
        self.short_name = short_name
        self.full_name = full_name

    def __str__(self):
        return "Name: " + self.full_name + ", State: " + self.st


# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview:
    def __init__(
        self,
        id,
        name,
        dealership,
        review,
        purchase,
        purchase_date,
        car_make,
        car_model,
        car_year,
        review_sentiment,
    ):
        self.id = id or 0
        self.name = name
        self.dealership = dealership
        self.review = review
        self.purchase = purchase
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.review_sentiment = review_sentiment

    def __str__(self):
        return "Review: " + self.review #+ ", Review sentiment: " + self.review_sentiment
