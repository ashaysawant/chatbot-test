import streamlit as st
import json
import boto3
import requests
from streamlit_extras.stylable_container import stylable_container
import logging
from botocore.exceptions import ClientError
# import pandas as pd
# import numpy as np

logger = logging.getLogger(__name__)

questions = ["What is Microsoft's expected revenue and earnings growth?", 
                 "Is it better to inevst in Growth stocks or value stocks right now?", 
                 "Summarize Apple's latest earnings report."]

PROMPT_TEMPLATE2 = """
System: You are an Investment Analyst AI system, and provides answers to questions by using fact based and statistical information when possible. 
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags. 

If the question is not related to financial information, politely inform the user that you can only answer related to financial questions.
Always provide a recommendation to buy the stock of the company or not, given the information available, 
give brutally honest opinions if you think we should buy it tell us to buy
and also be honest with it when you think we shouldn't buy, by the numbers available
also try to analyse if we should invest in short term or long term. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

<question>
{question}
</question>

The response should be specific and use statistics or numbers when possible.
"""
#Also give reference to your souces.


class ComprehendDetect:
    """Encapsulates Comprehend detection functions."""

    def __init__(self, comprehend_client):
        """
        :param comprehend_client: A Boto3 Comprehend client.
        """
        self.comprehend_client = comprehend_client

    # snippet-end:[python.example_code.comprehend.ComprehendDetect]

    # snippet-start:[python.example_code.comprehend.DetectEntities]
    def detect_entities(self, text, language_code):
        """
        Detects entities in a document. Entities can be things like people and places
        or other common terms.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The list of entities along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_entities(
                Text=text, LanguageCode=language_code
            )
            entities = response["Entities"]
            logger.info("Detected %s entities.", len(entities))
        except ClientError:
            logger.exception("Couldn't detect entities.")
            raise
        else:
            return entities

    # snippet-end:[python.example_code.comprehend.DetectEntities]

    # snippet-start:[python.example_code.comprehend.DetectSentiment]
    def detect_sentiment(self, text, language_code):
        """
        Detects the overall sentiment expressed in a document. Sentiment can
        be positive, negative, neutral, or a mixture.

        :param text: The document to inspect.
        :param language_code: The language of the document.
        :return: The sentiments along with their confidence scores.
        """
        try:
            response = self.comprehend_client.detect_sentiment(
                Text=text, LanguageCode=language_code
            )
            logger.info("Detected primary sentiment %s.", response["Sentiment"])
        except ClientError:
            logger.exception("Couldn't detect sentiment.")
            raise
        else:
            return response

    # snippet-end:[python.example_code.comprehend.DetectSentiment]

def get_company_symbols(userInput):

    comp_detect = ComprehendDetect(boto3.client("comprehend"))
    entities = comp_detect.detect_entities(userInput, "en")
    # entities = '[{"Score":0.9897878170013428,"Type":"ORGANIZATION","Text":"Microsoft","BeginOffset":8,"EndOffset":17}]'
    entities_json = json.loads(entities)
    print(entities_json)
    symbols = []
    for entity in entities_json:
        print(entity)
        # entity_json = json.loads(entity)
        if entity['Type'] == 'ORGANIZATION':
            symbol = get_ticker(entity['Text'])
            if symbol:
                symbols.append(symbol)
    return symbols

def get_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    company_code = data['quotes'][0]['symbol']
    return company_code

def generate_prompt(question):
    LLM_PROMPT = PROMPT_TEMPLATE2.format(question=question)
    qa_prompt = LLM_PROMPT.format(question=question)
    return qa_prompt

# Function to get the bot's response
def get_bot_response(userInput):
    request_body = {
        "message": userInput,
        "sessionId":st.session_state['ia_session_id']
    }
    api_json = dict()
    bot_response = ''
    
    try:
        lambda_client = boto3.client('lambda')
        lambda_response = lambda_client.invoke(
            FunctionName='agent_is',
            InvocationType='RequestResponse',
            Payload=json.dumps(request_body)
        )
        response = json.loads(lambda_response['Payload'].read().decode('utf-8'))
        print(response)
        api_json = response['body']
        # bot_response = api_json["output"]["result"].replace('$','\\$').replace('\[\d*\]','')
        bot_response = api_json["output"].replace('$','\\$')
        
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        bot_response = 'Sorry, something went wrong. Please try again later.'

    if "ia_sessionId" in api_json.keys():
        st.session_state['ia_session_id'] = api_json["sessionId"]
    if "citations" in api_json.keys(): 
        citations = api_json["citations"]
        st.session_state.ia_messages.append({"role": "assistant", "content": bot_response, "citations":citations})
    return bot_response

# Function to store user information
def store_user_info(chat_history):
    request_body = {
        'body': {
            'sessionId':st.session_state['ia_session_id'],
            'chat_history': chat_history
            }
    }
    try:
        lambda_client = boto3.client('lambda')
        lambda_response = lambda_client.invoke(
            FunctionName='StoreProfile_IS',
            InvocationType='RequestResponse',
            Payload=json.dumps(request_body)
        )
        
        response = json.loads(lambda_response['Payload'].read().decode('utf-8'))
        #print(response)
        api_json = response['body']
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        bot_response = 'Sorry, something went wrong while storing the data. Please try again later.'


def update_chat_messages(container):
    #Display chat messages
    message = st.session_state.ia_messages[-1]
    with container:
        with st.chat_message(message["role"]):
            st.markdown(message["content"],unsafe_allow_html=True)
            if "citations" in message.keys() and message["citations"] is not None:
                with st.expander("See Context Information"):
                    for citation in message["citations"]:
                        retrievedReferences = citation["retrievedReferences"]
                        for reference in retrievedReferences:
                            st.markdown("Reference : "+reference["content"]["text"].replace('$','\\$'), unsafe_allow_html=True)
                            location = reference["location"]
                            if "S3" == location["type"]:
                                st.caption("Location : "+ location["s3Location"]["uri"], unsafe_allow_html=True)
                            elif "WEB" == location["type"]:
                                st.caption("Location : "+ location["webLocation"]["url"], unsafe_allow_html=True)
                            st.divider()
            else:
                st.empty()

def as_float(obj):
    """Checks each dict passed to this function if it contains the key "value"
    Args:
        obj (dict): The object to decode

    Returns:
        dict: The new dictionary with changes if necessary
    """
    if "value" in obj:
        obj["value"] = float(obj["value"])
    return obj


def app():
    if 'ia_session_id' not in st.session_state:
        st.session_state['ia_session_id'] = None
    st.image("IA_Banner.png")
    hide_img_fs = '''
    <style>
    button[title="View fullscreen"]{
        visibility: hidden;}
    </style>
    '''
    st.markdown(hide_img_fs, unsafe_allow_html=True)
    row = st.columns([1,3,2])

    with row[0]:
        # with st.expander("Most frquently asked questions:"):
        with  stylable_container(
            "codeblock",
            """
            code {
                white-space: pre-wrap !important;
            }
            """,
        ):
        # st.container(height=500):
            st.write("Most frquently asked questions:")
            for question in questions:
                st.code(question,language=None)
    
    with row[1]:
        ctr = st.container(height=500)
    
    with row[2]:
        market_info = st.container(height=500)
        market_info.write("Market Information")

    if "ia_messages" not in st.session_state.keys():
        st.session_state.ia_messages = [{"role": "assistant", "content": "Ask your personal Investment Analyst a question to get started!","citations":None}]
    
    for message in st.session_state.ia_messages:
        with ctr:
            with st.chat_message(message["role"]):
                st.markdown(message["content"],unsafe_allow_html=True)
                if "citations" in message.keys() and message["citations"] is not None:
                    with st.expander("See Context Information"):
                        for citation in message["citations"]:
                            retrievedReferences = citation["retrievedReferences"]
                            for reference in retrievedReferences:
                                st.markdown("Reference : "+reference["content"]["text"].replace('$','\\$'), unsafe_allow_html=True)
                                location = reference["location"]
                                if "S3" == location["type"]:
                                    st.caption("Location : "+ location["s3Location"]["uri"], unsafe_allow_html=True)
                                elif "WEB" == location["type"]:
                                    st.caption("Location : "+ location["webLocation"]["url"], unsafe_allow_html=True)
                                st.divider()
                else:
                    st.empty()

    
    userInput = st.chat_input("Enter your question",key='chatInput')
    
    if userInput:
        st.session_state.ia_messages.append({"role": "user", "content": userInput,"citations":None})
        update_chat_messages(ctr)
        tickers = get_company_symbols(userInput)
        
        if tickers:
            st.session_state.tickers = tickers
            market_info.write(st.session_state.tickers)
        question = generate_prompt(userInput)

        with ctr:
            with st.spinner('Generating response...'):
                bot_response = get_bot_response(question)
        update_chat_messages(ctr)
        store_user_info(st.session_state.ia_messages)

app()

