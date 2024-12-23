from transformers import BertTokenizer, BertModel # type: ignore
import boto3 # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import numpy as np
import time
from bs4 import BeautifulSoup # type: ignore
from csv import DictReader
from emailer import send_email
from csv import DictReader
from io import StringIO
import csv
from chatbot import get_response
import random
from misc import get_all_listings






from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore

import platform
import os
from pathlib import Path

from dotenv import load_dotenv # type: ignore




load_dotenv()

dynamodb = boto3.resource('dynamodb',
                          region_name=os.getenv("REGION_NAME"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )


#dynamoDB tables
matchedListingsTable = dynamodb.Table('ListingsData')
messagesTable = dynamodb.Table('MessagesData')


def all_ongoing_texts_with_client(driver, profile_url, cookies):

    
  
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load
    driver.get(profile_url)
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

    all_texts = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
    #print("length of all_texts: ", len([i.text for i in all_texts]))
    #print('all_texts: ', [i.text for i in all_texts])
    curr_texts = [i.text for i in all_texts]

    return "" if curr_texts == [] else curr_texts[-1]

def get_first_message(title, URL, price):

    first_messages = [
                            f"Hello, I hope you’re having a good day. Just saw that you're selling {title}  on marketplace {URL}. I can come pick this up and pay you ${price} in cash.",
                            f"Hello, just saw that you're selling a {title}  on marketplace {URL}. I can pay you ${price} in cash and come pick it up.",
                            f"Hey, just saw that you're selling a {title} on marketplace {URL}. I can come pick this up and pay you ${price} in cash.",
                            f"Hi, just saw that you're selling {title}  on marketplace {URL}. I could pay you up to ${price} in cash and I could come pick it up.",
                            f"Hi, just saw that you're selling {title}  on marketplace {URL}. I can come pick this phone up for ${price} in cash asap. Where are you located?",
                            f"Just saw that you're selling {title}  on marketplace {URL}. Can I please come pickup for ${price}?",
                            f"Just saw that you're selling {title}  on marketplace {URL}. I can pickup for ${price}in cash.",
                            f"Just saw that you're selling {title}  on marketplace {URL}. Would you do ${price} in cash?",
                            f"Just saw that you're selling {title}  on marketplace {URL}. I can pay the full ${price} in cash. What's a good meetup spot for you?",
                            f"Just saw that you're selling {title}  on marketplace {URL}. Let's do the ${price} in cash. Where are you located?"

            ]
    return random.choice(first_messages)
temp = [
"Come meet me here", "Address",
"Can you meet me in","How far are you from",
"Wawa", "McDonalds", "Autozone", "Target",
"House", "Near", "Just off route", "Road",
"Intersection", "Park", "Reserve", "Repair shop","Mall","Police station","Gas station","Bank","Store"
"At&t", "Verizon store", "T-mobile","att","atnt","Spot","Closer","Too far",
"How far are you","Distance","Far away","ETA","5:30PM",
"Morning","Noon","Afternoon","Evening","Tomorrow","Today",
"After school","Are you busy","When are you free",
"Can you meet me at","After lunch","Come now","What time","Later","Early","Work","Instead",
"Actually let’s do","I’d be more comfortable at","best offer","OBO",
"I have 2 phones","Other phone","Would you be interested in any of my other phones",
"Trade","Bulk deal","Bargain","Negotiate","Negotiation","Difference","It’s not $1",
"No it’s not free","free","Better price","Someone's paying more","Better","More","Screen is cracked",
"Did you see the","It’s not","Everybody else","Flooded with messages","I’m looking","Higher","Open","Maybe"
]

def check_convo_end(clients_message):
    try:
            
        for item in temp:
            if item.lower() in clients_message:
                return True
            else:
                return False
                """
                SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                SUBJECT = "🤝 AGREEMENT MADE"
                BODY = f"I just reached an agreement with a seller. Check it out here: {messenger_link}"

                send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)

                """
                
                break
    except Exception as e:
        print("found error in checking convo end: ", str(e))
    return
                            


def get_profile_id(driver, match_url, cookies):
    try:
        driver.implicitly_wait(10)
        driver.get(match_url)
        driver.delete_all_cookies()
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
    
        print("cookies added to driver successfully when getting profile id")



        #grab profile id using beautifulsoup
        soup = BeautifulSoup(driver.page_source, 'html5lib') 
        links = soup.findAll('a', attrs={'class': 'x972fbf'})
        profile_links = [i.get('href') for i in links if 'profile' in i.get('href')]
        #print("current_url: ", driver.current_url)
        #print("match_url: ", match_url)
        #print("profile_links: ", profile_links)
        profile_id = profile_links[1].split('/')[3]
        messenger_link = "https://www.facebook.com/messages/t/" + profile_id


        return messenger_link
    except Exception as e:
        print("error getting profile id: ", str(e))

                
def get_recent_message_from_db(match_url):
    try:
        response = messagesTable.get_item(
            Key={
                'product_url': match_url
            }
        )

        response_value = response['Item']['recent_message']

        if 'Item' in response and response_value != None:
            return response['Item']['recent_message']
        return ""



    except Exception as e:
        print("Could not find recent message: ", str(e))

def send_message(driver, profile_url, message, cookies):

    try:

       

        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])

        driver.get(profile_url)
        driver.delete_all_cookies()
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        #log in to message url

        #send message
        messageInput = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')
        messageInput.click()


        if message != None or message != "":

            for i in message:
                messageInput.send_keys(i)
            messageInput.send_keys(Keys.RETURN)
            print(f"message sent successfully to {profile_url}")
    except Exception as e:
        print(f"Error sending message to {profile_url}: ", str(e))


def message_clients_helper(driver, listings, cookies):

    #loop through all listings
    # check the messaging if it's
    try:
        for match in listings:
            try:
                match_url = match['listing_url']
                price = match['price']
                title = match['title']



                profile_id = get_profile_id(driver, match_url, cookies)
                recent_message = all_ongoing_texts_with_client(driver, profile_id, cookies)

                if get_recent_message_from_db(match_url) == "end":
                    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                    SUBJECT = "🤝 AGREEMENT MADE"
                    BODY = f"I just reached an agreement with a seller. Check it out here: {profile_id}"

                    send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)


                #if first message
                if recent_message == "":
                    first_message = get_first_message(title, match_url, price)
                    send_message(driver, profile_id, first_message, cookies)
                    #update recent message in DB
                    message_payload = {
                        'product_url': match_url,
                        'messenger_link': profile_id,
                        'recent_message': first_message

                    }
                    messagesTable.put_item(Item=message_payload)
                    """
                        messagesTable.update_item(
                        Key={'product_url': match_url},
                        UpdateExpression="SET recent_message = :val",
                        ExpressionAttributeValues={':val': first_message},
                        ReturnValues="UPDATED_NEW"
                    )
                    """
                    #UPDATE RECENT MESSAGE VARIABLE HERE
                    recent_message = first_message

                    #send email to business
                    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                    SUBJECT = "🟢 STARTED CONVERSATION"
                    BODY = f"I just started a conversation for a ${title} for ${price}. Track the conversation here: ${profile_id}"

                    send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)


                #recent_message gets most recent message between two parties
                message_from_client = all_ongoing_texts_with_client(driver, profile_id, cookies)
                if message_from_client != get_recent_message_from_db(match_url) and get_recent_message_from_db(match_url) != "":
                    #get response from bot
                    bot_reply = get_response(message_from_client, profile_id)
                    #send message
                    send_message(driver, profile_id, bot_reply, cookies)
                    #update recent_message in db
                    messagesTable.update_item(
                        Key={'product_url': match_url},
                        UpdateExpression="SET recent_message = :val",
                        ExpressionAttributeValues={':val': bot_reply},
                        ReturnValues="UPDATED_NEW"
                    )
                    if check_convo_end(recent_message):
                        messagesTable.update_item(
                        Key={'product_url': match_url},
                        UpdateExpression="SET recent_message = :val",
                        ExpressionAttributeValues={':val': "end"},
                        ReturnValues="UPDATED_NEW"
                    )
                else:
                    print("chose to not send a message--client hasn't responded--no error here")
                    

            except Exception as e:
                print(f"Error checking status for {profile_id} with a message: ", str(e))

    except Exception as e:
        print("Error occurred: ", str(e))

    pass

