from botocore.vendored import requests
import argparse
import json
import pprint
import sys
import urllib
import os

import boto3
import botocore
from boto3.dynamodb.conditions import Key


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


   

USERS_TABLE = 'foxboss-user-data'
EMAIL_INDEX = 'email-index'
dynamo = boto3.resource('dynamodb')
table = dynamo.Table(USERS_TABLE)


def lambda_handler(event, context):
    # TODO implement
    
    print (event)
    slots = event['currentIntent']['slots']
    name = slots['Name']
    sessAttr = event['sessionAttributes']
    
    if not sessAttr:
        sessAttr={}
        
    if not event['userId']:
        return close(sessAttr,"Failed","what's happening? who are you? Begone")
    
    res = getUserHandler(event, context)
    print (res)
    
    if res['statusCode'] == 400:
        return close(sessAttr,"Failed","something's blew up when the getting the user")
    
    item = res['body'].get('Item')
    # print (item)
    if item is None  and name is None:
        slots['Name'] = None
        return delegate(sessAttr, slots)
        
    elif item is not None and name is None:
        print ("know the dude")
        print (item)
        name = item['name']
        slots['Name'] = name
        return elicit_intent(sessAttr,event['currentIntent']['name'],slots, "WHATZAPPP?? Feeling hungry "+name+"? Whataya wanna eat?")
        
    elif item is None and name is not None:
        print ("insert")
        res = insertUserHandler(event, context)
        return elicit_intent(sessAttr, event['currentIntent']['name'],slots, slots['Name']+"!!! My new bro, wanna eat something?")       
        
    else:
        return close(sessAttr,"Failed", "no idea what's goin on")        


def getUser(id, table):
    user = table.get_item(
        Key={ 'id': id }
    )
    # print("user "+json.dumps(user))
    return user


def insertUser(user, table):
    table.put_item(
        Item=user,
        ConditionExpression="attribute_not_exists(id)"
    )

    return user

# def updateUser(id, user, table):
#     user['id'] = id
#     table.put_item(
#         Item=user,
#         ConditionExpression="attribute_exists(id)"
#     )

#     return user


def respond(err, res=None):
    """ Generates a response conforming to API Gateway's Lambda Proxy Integration. """

    return {
        'statusCode': '400' if err else '200',
        'body': str(err) if err else res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def getUserHandler(event, context):
    """ GET /users/:id """
    id = event['userId']
    print (id)
    print (table)
    try:
        return respond(None, getUser(id, table))
    except Exception as e:
        return respond(e)

def insertUserHandler(event, context):
    """ POST /users """
    id = event['userId']
    slots = event['currentIntent']['slots']
    name = slots['Name']
    user = { 'id' : id, 'name': name}
    try:
        return respond(None, insertUser(user, table))
    except Exception as e:
        return respond(e)

# def updateUserHandler(event, context):
#     """ PUT /users/:id """
#     id = event['pathParameters']['id']
#     user = json.loads(event['body'])
#     try:
#         return respond(None, updateUser(id, user, table))
#     except Exception as e:
#         return respond(e)
        
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
    
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    print("return message: \n{}".format(json.dumps(message)))
    
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


def elicit_intent(session_attributes, intent_name, slots, message):
    print("return message: \n{}".format(json.dumps(message)))
    
    return {
        'sessionAttributes': session_attributes,
        "dialogAction": {
            "type": "ElicitIntent",
            "message": {
              "contentType": "PlainText",
              "content": message
            }
            # ,"responseCard": {
            #     "version": integer-value,
            #     "contentType": "application/vnd.amazonaws.card.generic",
            #     "genericAttachments": [
            #           {
            #              "title":"card-title",
            #              "subTitle":"card-sub-title",
            #              "imageUrl":"URL of the image to be shown",
            #              "attachmentLinkUrl":"URL of the attachment to be associated with the card",
            #              "buttons":[ 
            #                  {
            #                     "text":"button-text",
            #                     "value":"Value sent to server on button click"
            #                  }
            #              ]
            #           } 
            #         ] 
            # }
            }
        }

def close(session_attributes, fulfillment_state,  message):
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
    
    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }