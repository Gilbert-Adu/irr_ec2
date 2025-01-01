from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from bs4 import BeautifulSoup # type: ignore

import boto3 # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import csv
from io import StringIO


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
#driver
firefox_options = Options()
firefox_options.add_argument("--headless")
#options=firefox_options
driver = webdriver.Firefox()

driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load
#https://www.facebook.com/messages/t/9323097651042149/
driver.get("https://www.facebook.com/marketplace/item/1237638907302046/?referralSurface=messenger_lightspeed_banner&referralCode=messenger_banner")
driver.delete_all_cookies()
for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()
#soup = BeautifulSoup(driver.page_source, 'html5lib')
target_class = 'x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xk50ysn xzsf02u x1yc453h'
#message_div = soup.find('span', attrs={'class': target_class})

try:
    messageInput = driver.find_element(By.XPATH, '//div[@aria-label="Message" or @aria-label="Message Again"]')
    print("aria: ", messageInput.get_attribute("aria-label"))
    


    
    if messageInput.get_attribute("aria-label") == 'Message Again':
        #messageInput.click()
        driver.execute_script("arguments[0].click();", messageInput)

        print("asked to message again")

        all_texts = driver.find_elements(By.XPATH, '//div[@dir="auto"]')
        #print("length of all_texts: ", len([i.text for i in all_texts]))
        print('all_texts: ', [i.text for i in all_texts])
        curr_texts = [i.text for i in all_texts]

        #input message
        message = "hello can i come pick this up this weekend?"
        messagebar = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')
        messagebar.click()


        if message != None or message != "":

            for i in message:
                messagebar.send_keys(i)
            #messagebar.send_keys(Keys.RETURN)
            print(f"message sent successfully")



    elif messageInput.get_attribute("aria-label") == "Message":
        messageInput.click()
        print("clicked message input")
        #if started chat here
        #started_chat = soup.find('div', attrs={'class': target_class})

        textarea = driver.find_element(By.XPATH, "//textarea[contains(@class, 'x1i10hfl xggy1nq x1s07b3s xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x9f619 xzsf02u x78zum5 x1jchvi3 x1fcty0u x1a2a7pz x6ikm8r x1pi30zi x1swvt13 xtt52l0 xh8yej3 x1ls7aod xcrlgei x1byulpo x1agbcgv x15bjb6t')]")  # Replace with your class

        textarea.clear()  # Optional: Clears any existing text
        textarea.send_keys("can i get it for 120?")
        print("text inputted")
        send_button = driver.find_element(By.XPATH, '//div[@aria-label="Send message"]')
        #send_button.click()
        print("message sent")






except Exception as e:
    print("Error: ", e)







#https://www.facebook.com/messages/t/9323097651042149/
