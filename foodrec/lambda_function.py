
"""
Yelp Fusion API code sample.
This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.
Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.
This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.
Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""

"""
Client ID
9HzBbblHm5KlXos-fjwKfQ

API Key

"""

# from __future__ import print_function
from botocore.vendored import requests
import argparse
import json
import pprint
import sys
import urllib
import random

# import urllib.request
# contents = urllib.request.urlopen("https://api.yelp.com/v3/businesses/search").read()

# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
API_KEY= ''


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 5

CONFIRM_MSG = ['If it pleases the Crown then ',
                'Really? You mean it? Honest and for true? ',
                'But soft! What piercing light through yonder window breaks?! ',
                'May I favor master with a tender kiss on the forehead. ',
                'Nothing is strange to the wise. ',
                'Oh joy, oh rapture. ',
                'Finally! Praise the lord. ']
                
DENIED_MSG = ['Well, if your majesty is not pleased, we do have something else. ',
                'What if I sing to you? No? Fine! ',
                'Thank you. May I have another? How about ',
                'Pleeeeeeease? No? ',
                'You\'d do it for Randolph Scott! What about ',
                'It seems my princess is in another castle. ',
                'This boldness is not courage. ',
                'Well... a stopped clock is right twice a day. ']                


def lambda_handler(data, context):
    currIntent = data['currentIntent']
    name = currIntent['name']
    slots = currIntent['slots']
    confirmStt = currIntent['confirmationStatus']
    sessAttr = data['sessionAttributes']
    location = slots['location']
    print ("confirmStt is {}".format(str(confirmStt)))
    
    if sessAttr is None:
        sessAttr = {}
        
    print("message coming in: {}".format(json.dumps(data)))
    
    if not location:
        return close(sessAttr, "Failed", "Babe I can't see where you at")
        
    
    if not confirmStt or confirmStt == "None" or not sessAttr:
        
        
        
        try:
            response = query_api("", location)
        except HTTPError as error:
            sys.exit(
                'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                    error.code,
                    error.url,
                    error.read(),
                )
            )
            
        businesses = response.get('businesses')

        if not businesses:
            print(u'No businesses for {0} in {1} found.'.format(term, location))
            return close(sessAttr, "Fulfilled", "ughhh no business found")
        
        business_id = businesses[0]['id']
        restaurant = get_business(API_KEY, business_id)
        
        print ("restarant {}".format(restaurant))
        
        categories = []
        for e in restaurant['categories']:
            categories.append(e['title'])
   
        categories = ", ".join(categories)
        
        msg = "Starting off, "+categories+" sound good?"
        
        sessAttr['businesses'] = json.dumps(businesses)
        sessAttr['curr'] = 0 
        
        restName = restaurant['name']
        # photo = restaurant['photos'][0]
        photo = restaurant['image_url']

        resCard = {"contentType": "application/vnd.amazonaws.card.generic"}
        attach = {}
        attach['title'] = restName
        attach['imageUrl'] = photo
        attach['attachmentLinkUrl'] = restaurant['url']
        resCard["genericAttachments"] = [attach]

        return confirm(sessAttr, "ConfirmIntent", msg, name, slots, resCard)
    
    elif confirmStt == "Confirmed":
        print ("sessionAttributes : {}".format(str(sessAttr)))
        businesses = json.loads(sessAttr['businesses'])
        curr = int(sessAttr['curr'])
        business_id = businesses[curr]['id']
        restaurant = get_business(API_KEY, business_id)
        
        msg = random.choice(CONFIRM_MSG)+"\nHere's some details about the place.\nRating: {}\nPhone Number: {}".format(restaurant['rating'],restaurant['phone'])
         
        adr = " ".join(restaurant['location']['display_address'])
        ggsearch = "https://maps.google.com/?q="+ adr.replace(" ","+")       
        msg = msg + adr + "\n" + ggsearch
        
        return close(sessAttr, "Fulfilled", msg)
    
    else: #confirmStt= Denied
        businesses = json.loads(sessAttr['businesses'])
        curr = int(sessAttr['curr'])
        
        if curr < len(businesses)-1: 
            curr += 1
            
            business_id = businesses[curr]['id']
            restaurant = get_business(API_KEY, business_id)
            
            categories = []
            for e in restaurant['categories']:
                categories.append(e['title'])
   
            categories = ", ".join(categories)
        
            msg = random.choice(DENIED_MSG)+categories+"?"
            
            # sessAttr['businesses'] = businesses
            sessAttr['curr'] = curr  
            
            restName = restaurant['name']
            # photo = restaurant['photos'][0]
            photo = restaurant['image_url']
    
            resCard = {"contentType": "application/vnd.amazonaws.card.generic"}
            attach = {}
            attach['title'] = restName
            attach['imageUrl'] = photo
            attach['attachmentLinkUrl'] = restaurant['url']
            resCard["genericAttachments"] = [attach]

            return confirm(sessAttr, "ConfirmIntent", msg, name, slots, resCard)
        else:
            return close(sessAttr, "Failed", "We're out of options. The queen is too picky.")
  
def confirm(sessAttr, retType, msg, intentName, slots, responseCard):
    msgContent = {"contentType" : "PlainText"}
    msgContent['content'] = msg 
    diagAct = {}
    diagAct['type'] = retType
    diagAct['message'] = msgContent
    diagAct['intentName'] = intentName
    diagAct['slots'] = slots
    diagAct['responseCard'] = responseCard
    message = {}
    message['sessionAttributes'] =  sessAttr
    message['dialogAction'] = diagAct
    
    print("return message: \n{}".format(json.dumps(message)))
    # json.dumps(message)
    return message

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, location):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(term, location):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    response = search(API_KEY, term, location)

    return response


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    # msgContent = {"contentType" : "PlainText"}
    # msgContent['content'] = message 
    
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': { 
                'contentType' : 'PlainText',
                'content' : message
            }
        }
    }
    # msgContent = {"contentType" : "PlainText"}
    # msgContent['content'] = msg 
    # diagAct = {}
    # diagAct['type'] = retType
    # diagAct['message'] = msgContent
    # diagAct['intentName'] = intentName
    # diagAct['slots'] = slots
    # diagAct['responseCard'] = responseCard
    # message = {}
    # message['sessionAttributes'] =  sessAttr
    # message['dialogAction'] = diagAct
    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
# def main():
#     parser = argparse.ArgumentParser()

#     parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
#                         type=str, help='Search term (default: %(default)s)')
#     parser.add_argument('-l', '--location', dest='location',
#                         default=DEFAULT_LOCATION, type=str,
#                         help='Search location (default: %(default)s)')

#     input_values = parser.parse_args()

#     try:
#         query_api(input_values.term, input_values.location)
#     except HTTPError as error:
#         sys.exit(
#             'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
#                 error.code,
#                 error.url,
#                 error.read(),
#             )
#         )


# if __name__ == '__main__':
#     main()