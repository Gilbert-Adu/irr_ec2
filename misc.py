from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from bs4 import BeautifulSoup # type: ignore
import os
from pathlib import Path
import platform
from csv import DictReader
import boto3 # type: ignore
from io import StringIO
import csv
from dotenv import load_dotenv # type: ignore
from messenger import send_message, get_first_message
from emailer import send_email
import re


load_dotenv()



dynamodb = boto3.resource('dynamodb',

                        region_name=os.getenv("REGION_NAME"),
                        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                        )



table = dynamodb.Table('ListingsData')
messagesTable = dynamodb.Table('MessagesData')
tasksTable = dynamodb.Table('TasksTable')



def get_all_listings():
    try:
        response = table.scan()
        items = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        return items
    
    except Exception as e:
        print("could not get all LISTINGS: ", str(e))


#retrieves all tasks from DB
def get_all_tasks():
    try:
        response = tasksTable.scan()
        items = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        return items
    
    except Exception as e:
        print("could not get all TASKS: ", str(e))






def match_criteria(title, query):

    title = title.replace(" ", "")
    query = query.replace(" ", "")

    if query.lower() in title.lower():
        if ("promax" in query.lower()) and ("promax" in title.lower()):
            return True
        if ("promax" not in query.lower()) and ("promax" in title.lower()):
            return False
        if ("pro" in query.lower()) and ("pro" in title.lower()):
            return True
        if ("max" in query.lower()) and ("max" in title.lower()):
            return True
        if ("max" not in query.lower()) and ("max" not in title.lower()):
            return True
        if ("pro" not in query.lower()) and ("pro" not in title.lower()):
            return True
        return False
    return False



def scraper_helper(driver, query, minPrice, maxPrice, taskUrl, cookies):

        

        driver.implicitly_wait(10)

        driver.get(taskUrl)
        driver.delete_all_cookies()
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        matches = []

        #print("url: ", taskUrl)


        listings = soup.find_all('div', class_='x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24')

        #change to all listings
        print("total matches: ", len(listings))
        for i in range(len(listings)):
            title = listings[i].find('span', class_='x1lliihq x6ikm8r x10wlt62 x1n2onr6')
            if title is not None:
                title = title.get_text()
            #link_element = listings[i].find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1s688f x1lku1pv')
            link_div = listings[i].find('div', class_="x3ct3a4")
            #print("link_div_type: ", type(link_div))
            link_element = ""
            if link_div is not None:
                link_element = link_div.find('a')
            desc_text = ""
            if title is not None:
                #print("link_a: ", link_element)

                    


                #print("first listing: ", listings[i])
                #link_element = listings[i].find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1sur9pj xkrqix3 x1s688f x1lku1pv')
                href_value = link_element.get('href')
                price = listings[i].find('span', class_='x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1lkfr7t x1lbecb7 x1s688f xzsf02u').get_text()
                
                listing_url = "https://www.facebook.com" + href_value
                if '$' in price and ',' in price:
                    #print("price: ", price)
                    price = int(price[1:].replace(",", ""))
                elif '$' in price and ',' not in price:
                    #print("price: ", price)
                    price = int(price[1:])
                if match_criteria(title, query) and (price >= minPrice) and (price <= maxPrice):
                    # and minPrice <= int(price) <= maxPrice

                    
                    
                    driver.implicitly_wait(10)  # Waits for 10 seconds for the page to load
                    driver.get(listing_url)
                    driver.delete_all_cookies()
                    for cookie in cookies:
                        driver.add_cookie(cookie)
                    
                    driver.refresh()
                    


                    

                    desc_page = driver.page_source
                    desc_page_soup = BeautifulSoup(desc_page, 'html.parser')
                    descriptions = desc_page_soup.find_all('span', class_="x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u")
                    desc_text = ""
                    if descriptions is None or descriptions == []:
                        desc_text = ""
                    else:
                        desc_text = descriptions[1].get_text()

                    
                    # wanted some checks done on the text in the description

                    """
                        put matches into database
                    """
                    
                    try:
                        
                        if query.lower() in title.lower() and "case" not in title.lower() and "protector" not in title.lower() and "charger" not in title.lower():
                            print(f"title is {title.lower()} and query is {query.lower()}")
                            print(f"Match found for : {title}")

                            table.update_item(
                            Key={'listing_url': listing_url},
                            UpdateExpression="""
                                SET
                                    title = :title,
                                    description = :description,
                                    price = :price,
                                    task_url = :task_url,
                                    minPrice = :minPrice,
                                    maxPrice = :maxPrice
                            """,
                            ExpressionAttributeValues={
                                ':title': title,
                                ':description': desc_text,
                                ':price': price,
                                ':task_url': taskUrl,
                                ':minPrice': minPrice,
                                ':maxPrice': maxPrice
                            },
                            ReturnValues="ALL_NEW"
                            )
                            print("matched listing inserted into database")
                            message = get_first_message(title, listing_url,price, minPrice, maxPrice)
                            send_message(driver, listing_url, message, cookies)
                            print("messaged from here")

                            message_payload = {
                                'product_url': listing_url,
                                'messenger_link': listing_url,
                                'recent_message': message

                            }
                            messagesTable.put_item(Item=message_payload)
                            print("recent data inputted in the DB")

                            #email business

                            SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                            SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                            RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                            SUBJECT = "🟢 STARTED CONVERSATION"
                            BODY = f"I just started a conversation for a ${title} for ${price}. Track the conversation here: ${listing_url}"

                            send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)
                            print("business email successfully")

                        else:
                            print(f"Will not insert {title} as it does not meet reqs")

                    except Exception as e:
                        print("could not insert into listing DB", str(e))
                            
                    
            #driver.quit()
        return

                    
#when listings is empty

