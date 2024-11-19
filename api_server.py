from selenium import webdriver  # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.common.keys import Keys # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.firefox.options import Options # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore

from flask import Flask, request, jsonify # type: ignore
from flask_cors import CORS  # type: ignore # Import CORS

from misc import scraper_helper
from messenger import message_clients_helper
from chatbot import add_training_data

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


#driver
firefox_options = Options()
firefox_options.add_argument("--headless")

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


    result = scraper_helper(driver, query, minPrice, maxPrice, taskUrl)

    return jsonify(result)

@app.route('/messaging_endpoint', methods=['POST'])
def messaging_endpoint():
    message_clients_helper(driver)
    return jsonify({"message": "success"})



if __name__ == "__main__":

    #change to port 80
    app.run(host='0.0.0.0', port=4000)
    print("up on 4000")



