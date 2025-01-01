import boto3 # type: ignore
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




load_dotenv()

#s3 bucket
s3 = boto3.client('s3',

                region_name=os.getenv("REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                         
            )
BUCKET_NAME='qkr'
CSV_FILE_KEY='gil_qkr.csv'
#gil_qkr.csv

response = s3.get_object(Bucket=BUCKET_NAME, Key=CSV_FILE_KEY)
csv_content = response['Body'].read().decode('utf-8')

#read cookies from csv content
cookies = []
csv_reader = csv.DictReader(StringIO(csv_content))
cookies = [
    {'name': row['\ufeffname'], 'value': row['value'], 'domain': row['domain']}
    for row in csv_reader
]

dynamodb = boto3.resource('dynamodb',
                          region_name=os.getenv("REGION_NAME"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                          )


#dynamoDB tables
matchedListingsTable = dynamodb.Table('ListingsData')
messagesTable = dynamodb.Table('MessagesData')


def all_ongoing_texts_with_client(driver, match_url, cookies):

    
  
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load
    driver.get(match_url)
    driver.delete_all_cookies()
    for cookie in cookies:
        driver.add_cookie(cookie)
    print("cookies added in all_ongoing_texts")
    driver.refresh()

    #message button label -- Message or Message Again
    messageLabel = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@aria-label="Message" or @aria-label="Message Again"]'))
            )
    #if convo already ongoing
    if messageLabel.get_attribute("aria-label") == "Message Again":
        driver.execute_script("arguments[0].click();", messageLabel)
        #check ongoing texts
        all_texts = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
        curr_texts = [i.text for i in all_texts]
        most_recent_message = curr_texts[-1]
        return most_recent_message
    #if first convo
    else:
        return ""


def get_first_message(title, URL,price, minPrice, maxPrice):

    if '.' in str(price):
        temp = str(price).split('.')[0]
    else:
        temp = str(price)

    if len(temp) < 3:
        price = min(int(price), int(maxPrice))

        first_messages = [
                                f"Hello, I hope you’re having a good day. can I come pick this up and pay you ${price} in cash?",
                                f"Hello, I'd like to pay ${price} in cash. can I come pick it up?",
                                f"I can come pick this up and pay you ${price} in cash.",
                                f"I could pay you up to ${price} in cash and I could come pick it up.",
                                f"I can come pick this phone up for ${price} in cash asap. Where are you located?",
                                f"Can I please come pickup for ${price}? where and when can we meet?",
                                f"I can pickup for ${price}in cash. When and where can we meet?",
                                f"Would you do ${price} in cash?",
                                f"I can pay the full ${price} in cash. What's a good meetup spot for you?",
                                f"Hi, can we do ${price} in cash. Where are you located?"

                ]
        return random.choice(first_messages)
    else:

        if int(price) > int(minPrice) and int(price) <= int(maxPrice):

            price = min(int(maxPrice), int(price))

            first_messages = [
                                f"Hello, I hope you’re having a good day. can I come pick this up and pay you ${price} in cash?",
                                f"Hello, I'd like to pay ${price} in cash. can I come pick it up?",
                                f"I can come pick this up and pay you ${price} in cash.",
                                f"I could pay you up to ${price} in cash and I could come pick it up.",
                                f"I can come pick this phone up for ${price} in cash asap. Where are you located?",
                                f"Can I please come pickup for ${price}? where and when can we meet?",
                                f"I can pickup for ${price}in cash. When and where can we meet?",
                                f"Would you do ${price} in cash?",
                                f"I can pay the full ${price} in cash. What's a good meetup spot for you?",
                                f"Hi, can we do ${price} in cash. Where are you located?"

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
        #profile_id = profile_links[1].split('/')[3]
        #messenger_link = "https://www.facebook.com/messages/t/" + profile_id


        #return messenger_link
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

        if response['Item'] == None:
            return ""

        if 'Item' in response and response_value != None:
            return response['Item']['recent_message']
        return ""



    except Exception as e:
        print("Could not find recent message: ", str(e))

def send_message(driver, match_url, message, cookies):

    try:

       

        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load

        #visit match url
        driver.get(match_url)

        #delete cookies
        driver.delete_all_cookies()

        #add cookies
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()

        try:
            messageLabel = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, '//div[@aria-label="Message" or @aria-label="Message Again"]'))
            )

            if messageLabel.get_attribute("aria-label") == "Message":
                #click message button to get text area
                messageLabel.click()
                
                textarea = driver.find_element(By.XPATH, "//textarea[contains(@class, 'x1i10hfl xggy1nq x1s07b3s xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x9f619 xzsf02u x78zum5 x1jchvi3 x1fcty0u x1a2a7pz x6ikm8r x1pi30zi x1swvt13 xtt52l0 xh8yej3 x1ls7aod xcrlgei x1byulpo x1agbcgv x15bjb6t')]")  # Replace with your class
                textarea.clear()  # Optional: Clears any existing text
                textarea.send_keys(message)

                #click send button to send message
                send_button = driver.find_element(By.XPATH, '//div[@aria-label="Send message"]')
                send_button.click()
                print("first message sent")

            elif messageLabel.get_attribute("aria-label") == 'Message Again':
                driver.execute_script("arguments[0].click();", messageLabel)
                
                #input message
                
                messagebar = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')
                messagebar.click()
                print("message again clicked")


                if message != None or message != "":

                    for i in message:
                        messagebar.send_keys(i)
                    messagebar.send_keys(Keys.RETURN)
                    print(f"reply sent successfully")







        except Exception as e:
            print("Could not send message: ", str(e))

    except Exception as e:
        print(f"Error sending message for the item: {match_url}: ", str(e))


def message_clients_helper(driver, listings, cookies):

    #loop through all listings
    # check the messaging if it's
    try:
        for match in listings:
            try:
                match_url = match['listing_url']
                price = match['price']
                title = match['title']
                maxPrice = match['maxPrice']
                minPrice = match['minPrice']



                #profile_id = get_profile_id(driver, match_url, cookies)
                recent_message = all_ongoing_texts_with_client(driver, match_url, cookies)

                if get_recent_message_from_db(match_url) == "end":
                    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                    SUBJECT = "🤝 AGREEMENT MADE"
                    BODY = f"I just reached an agreement with a seller. Check it out here: {match_url}"

                    send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)



                #recent_message gets most recent message between two parties
                message_from_client = all_ongoing_texts_with_client(driver, match_url, cookies)
                if message_from_client != get_recent_message_from_db(match_url) and get_recent_message_from_db(match_url) != "":
                    #get response from bot
                    bot_reply = get_response(message_from_client, match_url)
                    #send message
                    send_message(driver, match_url, bot_reply, cookies)
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
                print(f"Error checking status for {match_url} with a message: ", str(e))

    except Exception as e:
        print("Error occurred: ", str(e))

    pass

