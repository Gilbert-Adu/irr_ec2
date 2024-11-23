from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
import boto3 # type: ignore
import csv
from io import StringIO
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()


#s3 bucket
s3 = boto3.client('s3',

                region_name=os.getenv("REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                         
            )
BUCKET_NAME='qkr'
CSV_FILE_KEY='qkr.csv'
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
options=firefox_options
driver = webdriver.Firefox()

driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load
driver.get("https://www.facebook.com/messages/t/100014276325191")
#https://www.facebook.com/messages/t/
driver.delete_all_cookies()

for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()
        

