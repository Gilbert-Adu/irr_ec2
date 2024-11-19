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





dynamodb = boto3.resource('dynamodb',
                          region_name=os.getenv("REGION_NAME"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )

#s3 bucket
s3 = boto3.client('s3',

                region_name=os.getenv("REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                         
            )

#dynamoDB tables
matchedListingsTable = dynamodb.Table('ListingsData')
messagesTable = dynamodb.Table('MessagesData')


BUCKET_NAME='qkr'
CSV_FILE_KEY='qkr.csv'

def get_desktop_path():
    home = str(Path.home())

    if platform.system() == "Windows":
        desktop = os.path.join(home, "Desktop")
    elif platform.system() == "Darwin":
        desktop = os.path.join(home, "Desktop")
    else:
        desktop = os.path.join(home, "Desktop")
    return desktop

cookies_file = os.path.join(get_desktop_path(), "qkr.csv")





response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILE_KEY)
csv_content = response['Body'].read().decode('utf-8')

cookies = []
csv_reader = csv.DictReader(StringIO(csv_content))

def all_ongoing_texts_with_client(driver, profile_url):
    driver.get(profile_url)
    with open(cookies_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            cookie = {
                'name': row['\ufeffname'],
                'value': row['value'],
                'domain': row['domain']
            }
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
                            


def get_profile_id(driver, match_url):
    try:
        driver.get(match_url)

        #add cookies to driver
        with open(cookies_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                cookie = {
                    'name': row['\ufeffname'],
                    'value': row['value'],
                    'domain': row['domain']
                }
                driver.add_cookie(cookie)
        driver.refresh()
        print("cookies added successfully")


        #grab profile id using beautifulsoup
        soup = BeautifulSoup(driver.page_source, 'html5lib') 
        links = soup.findAll('a', attrs={'class': 'x972fbf'})
        profile_links = [i.get('href') for i in links if 'profile' in i.get('href')]
        profile_id = profile_links[0].split('/')[3]
        messenger_link = "https://www.facebook.com/messages/t/" + profile_id

        return messenger_link
    except Exception as e:
        print("error getting profile id: ", str(e))

                
def get_recent_message(match_url):
    try:
        response = messagesTable.get_item(
            Key={
                'product_url': match_url
            }
        )

        return response['Item'] if 'Item' in response else ""

    except Exception as e:
        print("Could not find recent message: ", str(e))

def send_message(driver, profile_url, message):

    try:
        #log in to message url
        driver.get(profile_url)
        with open(cookies_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                cookie = {
                    'name': row['\ufeffname'],
                    'value': row['value'],
                    'domain': row['domain']
                }
                driver.add_cookie(cookie)
        driver.refresh()

        #send message
        messageInput = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')
        messageInput.click()

        for i in message:
            messageInput.send_keys(i)
        messageInput.send_keys(Keys.RETURN)
        print(f"message sent successfully to ${profile_url}")


        

    except Exception as e:
        print(f"Error sending message to {profile_url}: ", str(e))


def message_clients_helper(driver, listings):

    #loop through all listings
    # check the messaging if it's
    try:
        for match in listings:
            try:
                match_url = match['listing_url']
                price = match['price']
                title = match['title']

                profile_id = get_profile_id(driver, match_url)
                recent_message = all_ongoing_texts_with_client(driver, profile_id)

                if get_recent_message(match_url) == "end":
                    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                    SUBJECT = "🤝 AGREEMENT MADE"
                    BODY = f"I just reached an agreement with a seller. Check it out here: {profile_id}"

                    send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)


                #if first message
                if recent_message == "":
                    first_message = get_first_message(title, match_url, price)
                    send_message(driver, profile_id, first_message)
                    #update recent message in DB
                    messagesTable.update_item(
                        Key={'product_url': match_url},
                        UpdateExpression="SET recent_message = :val",
                        ExpressionAttributeValues={':val': first_message},
                        ReturnValues="UPDATED_NEW"
                    )
                    #UPDATE RECENT MESSAGE VARIABLE HERE
                    recent_message = first_message

                    #send email to business
                    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                    SUBJECT = "🟢 STARTED CONVERSATION"
                    BODY = f"I just started a conversation for a ${title} for ${price}. Track the conversation here: ${profile_id}"

                    send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)



                if recent_message != get_recent_message():
                    #get response from bot
                    bot_reply = get_response(recent_message)
                    #send message
                    send_message(driver, profile_id, bot_reply)
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
                    

            except Exception as e:
                print(f"Error getting all current texts for {profile_id} with a message: ", str(e))

    except Exception as e:
        print("Error occurred: ", str(e))

    pass

