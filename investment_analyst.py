import streamlit as st
# import pandas as pd
# import numpy as np
import json
import boto3
import requests
from langchain.prompts import PromptTemplate

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

def generate_prompt(question):
    LLM_PROMPT = PromptTemplate(template=PROMPT_TEMPLATE2, input_variables=["question"]) 
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
        api_json = response['body']
        bot_response = api_json["output"]["result"].replace('$','\\$').replace('\[\d*\]','')
        
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

    ctr = st.container(height=400)
    
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

    with st.expander("Most frquently asked questions:"):
        for question in questions:
            st.code(question,language=None)

    userInput = st.chat_input("Enter your question",key='chatInput')
    
    if userInput:
        st.session_state.ia_messages.append({"role": "user", "content": userInput,"citations":None})
        update_chat_messages(ctr)
        question = generate_prompt(userInput)
        with ctr:
            with st.spinner('Generating response...'):
                bot_response = get_bot_response(question)
        update_chat_messages(ctr)
        store_user_info(st.session_state.ia_messages)

app()
