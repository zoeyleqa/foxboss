# Foxboss
---------------------




<p align="center">
  <img width="460" height="300" src="pictures/overview.png">
</p>

  Do you have that annoying friend who says "whatever" when you ask what he wants to eat but then complains or shuts down all your suggestions? Or do you sometime just get hungry but don't know what to eat in the area?
***Foxboss*** is a chatbot (currently on Slack only) who looks up on Yelp using your provided location to find good stuff in the area and suggest them to you. He likes to put salt in his words with some snide comments because he's not as cool as your friends who have suffered enough from your pickiness.  
  
![architecture diagram](pictures/Foxboss-chatbot.png)
  
Used Services
-------------
* Amazon Lex
* DynamoDB
* Lambda

<p align="center">
  <img width="500" height="350" src="pictures/AWS_use.png">
</p>


How it works 
-------------

<p align="center">
  <img width="500" height="350" src="pictures/usage_example.png">
</p>

Amazon Lex was designed with 2 intents: `greetings` and `whatever`. 

![AWS Services](pictures/AWS_lex_greetings.PNG)

- Greeting is used to greet the user. With Lex, the chatbot can understands casual greeting quote like "hey", "hi", "Hi there it's Jake", etc. and extract the name of the user if provided. If not, it will use a lambda function in folder `greetings` to see if 
the user is new (user's name isn't in the database) or has spoken to the bot before by checking DynamoDB. The user's name will be inserted into the database with a specific ID if it's not in it. Else, ***Foxboss*** will address the user by name getting from the database with a cool greeting swag. Following that, the bot will ask what the user wants to eat. By saying sample utterances: "whatever", "I don't care", "Anything", "I'm hungry", the user will be switch to the `whatever` intent mode.

![AWS Services](pictures/AWS_lex_whatever.PNG)

- ***Foxboss*** will ask for the user's location using Lex and save in the slot `location`. Next, a fulfillment lambda function takes the location, sends a query to Yelp using Yelp Fusion API, receives restaurants' details (SEARCHLIMIT = 5), presents restaurant's categories and picture to the user with sassiness. The restaurants' details are put in a list `businesses` and save into the `session_attributes` along with the current restaurant suggestion `curr`. If the user says "No", the bot will suggests the next restaurant in the list. If the user rejects all available suggestions, the bot will stop and again, give a sassy comments about that. If the user say "Yes" on a restaurant, ***Foxboss*** will give him a few details of the restaurant and the address. A google map link is also included.

Demo
----------------

After standard greetings, ***Foxboss*** asks for your location, specifically the city you're in. Then, it starts giving food suggestion along with an image from the restaurant. If you say "No", it gives you a sassy comment and the next suggestion. If you say "Yes", it gives you the restaurant details.

<p align="center">
  <img width="500" height="350" src="pictures/foxboss1.gif">
</p>

After 5 suggestions (SEARCHLIMIT can expand), the chatbot will stop suggesting and give the user a final sassy comment.

<p align="center">
  <img width="500" height="350" src="pictures/foxboss2.gif">
</p>

Future Changes
----------------
  ***Foxboss*** functionalities can be expanded to 
  * taking specific food order
  * saving favorite places in the database
  * remember visited places to suggest if the user is in the mood "craving for something but don't know what it is". 
  * could be implemented into Alexa, expand to other messenging platform like Facebook or mobile applications.

***Special thanks to Andrew John Del Bene for the chatbot's sassy comments input***

Made by [Quynh-Anh (Zoey) Le](https://github.com/zoeyleqa)
----------------------------
ヾ(◍°∇°◍)ﾉﾞ
