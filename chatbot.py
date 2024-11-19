import torch # type: ignore
from transformers import BertTokenizer, BertModel # type: ignore

import boto3 # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import numpy as np
import time
from bs4 import BeautifulSoup # type: ignore
from csv import DictReader
from emailer import send_email


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



tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')


load_dotenv()




dynamodb = boto3.resource('dynamodb',

                          region_name=os.getenv("REGION_NAME"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                          )



table = dynamodb.Table('ChatbotTrainingData')
#----train bot functions
def load_training_data():
    response = table.scan()
    questions_answers = {}
    for item in response['Items']:
        question = item['question']
        answer = item['answer']
        questions_answers[question] = answer
    return questions_answers

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].numpy()


    
def get_response(user_input, chat_link, questions_answers=load_training_data()):
    user_embedding = get_embedding(user_input)
    best_match = None
    best_score = -1
    best_question = ""

    for question, answer in questions_answers.items():
        question_embedding = get_embedding(question)
        similarity = cosine_similarity(user_embedding, question_embedding)[0][0]

        if similarity > best_score:
            best_score = similarity
            best_match = answer
            best_question = question

    if best_score > 0.8:
        return best_match
    
    else:
        """
        send email to user if can't find response
        get password for gmail here: https://security.google.com/settings/security/apppasswords
        
        me = dcbz hyow plry kzhn

        """

        if user_input != None or user_input != '':
            SENDER_EMAIL = os.getenv("SENDER_EMAIL")
            SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
            RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
            SUBJECT = "🔴 COULD NOT ANSWER A CLIENT QUESTION"
            BODY = f"Hi there, \n On Facebook Marketplace, a client said, {user_input} and I did not know how to respond. \n Here's a link to the chat: {chat_link} Thanks,\n Your Friendly Bot."


            #send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)

            send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)
        
        return 
    
def add_training_data(question, answer, questions_answers=load_training_data()):

    for i in range(len(question)):
        
        questions_answers[question[i]] = answer[i]

        table.put_item(
            Item={'question': question[i], 'answer': answer[i]},
            
            )

    """

    """
    print("question: ", question)
    print("answer: ", answer)
    
    print("Training data added successfully.")



#---end of training