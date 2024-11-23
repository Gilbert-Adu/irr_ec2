from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore

from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS  # type: ignore # Import CORS

from misc import scraper_helper, get_all_listings, get_all_tasks
from messenger import message_clients_helper
from chatbot import add_training_data

import schedule # type: ignore
import time
import boto3 # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import csv
from io import StringIO



app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
#options=firefox_options
driver = webdriver.Firefox(options=firefox_options)

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'successfully working!'})

@app.route('/train_bot', methods=['POST'])
def train_bot():
    data = request.get_json()
    question = data.get("question")
    answer = data.get("answer")
    add_training_data(question, answer)
    return jsonify({'message': 'added question and answer successfully'})

@app.route('/insert_listings', methods=['POST'])
def insert_listings():
    data = request.get_json()
    query = data.get("query")
    minPrice = data.get("minPrice")
    maxPrice = data.get("maxPrice")
    taskUrl = data.get("taskUrl")


    result = scraper_helper(driver, query, minPrice, maxPrice, taskUrl, cookies=cookies)

    return jsonify(result)

@app.route('/messaging_endpoint', methods=['GET'])
def messaging_endpoint():
    listings = get_all_listings()
    #print("length of payload: ", len(listings))
    if listings == [] or len(listings) == 0 or listings == None:
        print("listings is empty; creating new listings from available tasks")
        tasks = get_all_tasks()
        for task in tasks:
            scraper_helper(driver, task['query'], int(task['minPrice']), int(task['maxPrice']), task['url'])
        return jsonify(tasks)
    
    #listings = get_all_listings()
    
    #perform messaging action on listings here
    message_clients_helper(driver, listings, cookies)
    
    
    return jsonify(listings)



if __name__ == "__main__":

    #change to port 80
    app.run(host='0.0.0.0', port=4000)
    print("up on 4000")



