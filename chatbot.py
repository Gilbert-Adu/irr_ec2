import boto3 # type: ignore
import difflib
from emailer import send_email


import os
from dotenv import load_dotenv # type: ignore


load_dotenv()




dynamodb_client = boto3.client('dynamodb',

                          region_name=os.getenv("REGION_NAME"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                          )

dynamodb_resource = boto3.resource('dynamodb',

                          region_name=os.getenv("REGION_NAME"),
                          aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                         
                          )




table = dynamodb_resource.Table('ChatbotTrainingData') #use resource
table_name = "ChatbotTrainingData"

#----train bot functions
def load_training_data():
    response = table.scan()
    questions_answers = {}
    for item in response['Items']:
        question = item['question']
        answer = item['answer']
        questions_answers[question] = answer
    return questions_answers


    
def fetch_questions_from_dynamodb():
    try:
        response = dynamodb_client.scan(TableName=table_name)
        items = response.get('Items', [])
        questions = [item['question']['S'] for item in items]
        return items, questions
    except Exception as e:
        print(f"Error fetching questions from DynamoDB: {e}")
        return [], []

def find_closest_question(user_input, questions):
    closest_matches = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.4)
    return closest_matches[0] if closest_matches else None

def get_answer_from_dynamodb(question, items):
    for item in items:
        if item['question']['S'] == question:
            return item['answer']['S']
    return "Sorry, I couldn't find an answer to your question"

def get_response(user_input, chat_link):
    if user_input != None or user_input != '':
            SENDER_EMAIL = os.getenv("SENDER_EMAIL")
            SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
            RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
            SUBJECT = "🔴 COULD NOT ANSWER A CLIENT QUESTION"
            BODY = f"Hi there, \n On Facebook Marketplace, a client said, {user_input} and I did not know how to respond. \n Here's a link to the chat: {chat_link} Thanks,\n Your Friendly Bot."
            send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)

    else:
        items, questions = fetch_questions_from_dynamodb()
        closest_question = find_closest_question(user_input, questions)
        if closest_question:
            answer = get_answer_from_dynamodb(closest_question, items)
            return answer
        else:
            SENDER_EMAIL = os.getenv("SENDER_EMAIL")
            SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
            RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
            SUBJECT = "🎗️ HELP -- CONTINUE CONVERSATION"
            BODY = f"I did not understand something a client said. \n Can you help? User said: {user_input}. \n Here's a link to the chat: {chat_link} \n Thanks,\n Your Friendly Bot."
            send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)

            return "Ugghhh...give me a sec"

#get_response("can we meet at the community park?")
      
#https://security.google.com/settings/security/apppasswords
        

        
    
    
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