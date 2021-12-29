import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth


# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    api_key = None
    params = dict()
    if "api_key" in kwargs:
        api_key = kwargs["api_key"]
        params["text"] = kwargs["text"]
        params["version"] = kwargs["version"]
        params["features"] = kwargs["features"]
        params["return_analyzed_text"] = kwargs["return_analyzed_text"]

    try:
        if api_key:
            response = requests.get(
                url,
                headers={"Content-Type": "application/json"},
                params=params,
                auth=HTTPBasicAuth("apikey", api_key),
            )
        else:
            response = requests.get(
                url, headers={"Content-Type": "application/json"}, params=kwargs
            )
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a `post_request` to make HTTP POST request
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))    

    try:
        response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                params=kwargs,
                json=json_payload,
            )
        
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    print(response)
    print('-----------\n\n')
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the list in JSON as dealershipsList
        dealershipsList = json_result["dealershipsList"]
        # For each dealer object
        for dealer_doc in dealershipsList:
            # Create a CarDealer object
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                state=dealer_doc["state"],
                zip=dealer_doc["zip"],
            )
            results.append(dealer_obj)

    return results


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        # Get the list in JSON as dealershipsList
        reviewsList = json_result["reviewsList"]
        print("reviewsList ---------------")
        print(reviewsList)
        # For each dealer object
        for review in reviewsList:
            # Create a DealerReview object
            review_obj = DealerReview(
                # id=review["id"],
                id=review.get("id",0),
                name=review["name"],
                dealership=review["dealership"],
                review=review["review"],
                purchase=review.get("purchase", False),
                purchase_date=review.get("purchase_date","N/A"),
                car_make=review.get("car_make","car_make"),
                car_model=review.get("car_model","car_model"),
                car_year=review.get("car_year","car_year"),
                review_sentiment=analyze_review_sentiments(review["review"]),
            )
            results.append(review_obj)

    return results


# Method to get dealers from a cloud function by attribute
def get_dealer_by_state_or_id(url, state, dealerId):
    results = []
    json_result = get_request(url, state=state, dealerId=dealerId)
    if json_result:
        dealershipsList = json_result["dealershipsList"]
        for dealer_doc in dealershipsList:
            dealer_obj = CarDealer(
                address=dealer_doc["address"],
                city=dealer_doc["city"],
                full_name=dealer_doc["full_name"],
                id=dealer_doc["id"],
                lat=dealer_doc["lat"],
                long=dealer_doc["long"],
                short_name=dealer_doc["short_name"],
                st=dealer_doc["st"],
                state=dealer_doc["state"],
                zip=dealer_doc["zip"],
            )
            results.append(dealer_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealerreview):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/32838fcd-18b9-41b2-9c9a-08c28ba20f63"
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/32838fcd-18b9-41b2-9c9a-08c28ba20f63/v1/analyze"
    api_key = "XIs-LVxOehE4gZOOWtJAWsFmpOfIjTK5-oaoXx76E-EK"

    # features = {"keywords": {"emotion": True, "sentiment": True},}
    # features = ["categories","classifications","concepts","emotion","entities","keywords","metadata","relations","semantic_roles","sentiment"]
    features = ["sentiment"]

    version = "2021-08-01"

    json_result = get_request(
        url,
        text=dealerreview,
        api_key=api_key,
        features=features,
        version=version,
        return_analyzed_text=True,
    )

    if "sentiment" in json_result:
        json_result = json_result['sentiment']['document']
    else: 
        json_result = {'score': 0, 'label': 'unset'}

    match json_result['label']:
        case 'negative':
            json_result['color'] = 'danger'
            json_result['fa'] = 'fa-frown-o'
        case 'neutral':
            json_result['color'] = 'warning'
            json_result['fa'] = 'fa-meh-o'
        case 'positive':
            json_result['color'] = 'success'
            json_result['fa'] = 'fa-smile-o'
        case 'unset':
            json_result['color'] = ''
            json_result['fa'] = ''

    print("\n-----------------------------")
    print(json_result)
    print("----------------------------- \n")


    return json_result
