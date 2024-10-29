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



response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILE_KEY)
csv_content = response['Body'].read().decode('utf-8')

cookies = []
csv_reader = csv.DictReader(StringIO(csv_content))

def all_ongoing_texts_with_client(driver):
    all_texts = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
    return [i.text for i in all_texts]

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

def check_convo_end(clients_message, temp, messenger_link):

    for item in temp:
        if item.lower() in clients_message:
            SENDER_EMAIL = "irescueresale@gmail.com"
            SENDER_PASSWORD = "adml cbcj wyqc jths"
            RECIPIENT_EMAIL = "irescueresale@gmail.com"
            SUBJECT = "🤝 AGREEMENT MADE"
            BODY = f"I just reached an agreement with a seller. Check it out here: {messenger_link}"

            send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)

            break
    return
                            


def message_clients_helper(driver):
    while True:
        print('in the message clients function now')
        matchedListings = matchedListingsTable.scan()
        
        try:
            for item in matchedListings['Items']:
                URL = item['listing_url']
                price = item['price']
                title = item['title']


            # URL = "https://www.facebook.com/marketplace/item/2470984673292700/?ref=browse_tab&referral_code=marketplace_top_picks&referral_story_type=top_picks"

            
            
                driver.get(URL)


                for row in csv_reader:
                    cookies.append({
                        'name': row['\ufeffname'],
                        'value': row['value'],
                        'domain': row['domain']
                    })

            
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.refresh()

                soup = BeautifulSoup(driver.page_source, 'html5lib') 
                links = soup.findAll('a', attrs={'class': 'x972fbf'})
                profile_links = [i.get('href') for i in links if 'profile' in i.get('href')]
                profile_id = profile_links[0].split('/')[3]
                messenger_link = "https://www.facebook.com/messages/t/" + profile_id

                #put profile_id in the driver.get below
                #"https://www.facebook.com/messages/t/100014276325191"
                driver.get(messenger_link)

                time.sleep (10)
                texts = all_ongoing_texts_with_client(driver)
                """
                after this:
                    keep track of the last sent or received message, 
                    check if there's a change in the messages list
                    if yes, it means client messaged so you should send a message back
                    if no, client has not messaged back so no need to send a message
                """
                theElement = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')

                # if it's the first contact
                if len(texts) == 0:
                    messages = [
                        f"Hello, I hope you’re having a good day. Just saw that you're selling {title}  on marketplace {URL}. I can come pick this up and pay you ${price} in cash."
                        f"Hello, just saw that you're selling a {title}  on marketplace {URL}. I can pay you ${price} in cash and come pick it up."
                        f"Hey, just saw that you're selling a {title} on marketplace {URL}. I can come pick this up and pay you ${price} in cash."
                        f"Hi, just saw that you're selling {title}  on marketplace {URL}. I could pay you up to ${price} in cash and I could come pick it up."
                        f"Hi, just saw that you're selling {title}  on marketplace {URL}. I can come pick this phone up for ${price} in cash asap. Where are you located?"
                        f"Just saw that you're selling {title}  on marketplace {URL}. Can I please come pickup for ${price}?"
                        f"Just saw that you're selling {title}  on marketplace {URL}. I can pickup for ${price}in cash."
                        f"Just saw that you're selling {title}  on marketplace {URL}. Would you do ${price} in cash?"
                        f"Just saw that you're selling {title}  on marketplace {URL}. I can pay the full ${price} in cash. What's a good meetup spot for you?"
                        f"Just saw that you're selling {title}  on marketplace {URL}. Let's do the ${price} in cash. Where are you located?"

                    ]
                    message = random.choice(messages)
                    for i in message:
                        theElement.send_keys(i)
                    #send the first message
                    theElement.send_keys(Keys.RETURN)
                    #save the first message to the MessagesData DB
                    driver.implicitly_wait(20)
                    messagesTable.put_item(
                        Item= {
                            'messenger_link': messenger_link,
                            'product_url': URL,
                            'recent_message': message
                        },

                    )



                    SENDER_EMAIL = "irescueresale@gmail.com"
                    SENDER_PASSWORD = "adml cbcj wyqc jths"
                    RECIPIENT_EMAIL = "irescueresale@gmail.com"
                    SUBJECT = "🟢 STARTED A CONVERSATION"
                    BODY = f"Just started chatting with a client. View our conversation here: {messenger_link}"

                    send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)
                                
                    print("sent and saved first message")

                #if we're replying to the client
                elif len(texts) > 0:
                    recent_message = ""
                    payload = messagesTable.get_item(
                        Key={'product_url': URL},
                        ProjectionExpression='recent_message'
                    )
                    print("about to check if item not in payload")
                    if 'Item' not in payload:
                        messagesTable.put_item(
                                    Item={
                                        'messenger_link': messenger_link,
                                        'product_url': URL,
                                        'recent_message': ""
                                    },

                        )
                    
                    
                    currentChat = messagesTable.get_item(Key={'product_url': URL})


                    #get the most recent message sent
                    
                    recent_message = currentChat['Item']['recent_message']
                    #if the most recent message is not the same as the message in the messaging area, we have a response
                    if texts[-1] != recent_message:
                        #get the response from the AI bot and send it
                        message = get_response(texts[-1], messenger_link)
                        recent_message = message
                        for i in message:
                            theElement.send_keys(i)
                        theElement.send_keys(Keys.RETURN)
                        driver.implicitly_wait(20)
    


                        #now update the recent message of that chat
                        #if we can find the current chat item in the DB, we update the most recent message
                        if len(currentChat['Item']) == 1:
                            messagesTable.update_item(
                                Key={'product_url': URL},
                                UpdateExpression='SET recent_message = :val',
                                ExpressionAttributeValues={':val': recent_message}
                            )
                            print("updated the message in the DB")
                        #else we create a new chat in the DB 
                        else:
                            messagesTable.put_item(
                                Item={
                                    'messenger_link': messenger_link,
                                    'product_url': URL,
                                    'recent_message': recent_message
                                },

                
                            )
                #here
                check_convo_end(texts[-1], temp, messenger_link)
            time.sleep(5 * 60)
                
        except Exception as e:
            print("error: ", str(e))





