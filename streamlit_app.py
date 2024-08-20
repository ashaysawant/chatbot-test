import streamlit as st
st.set_page_config(layout="wide")
import requests
import os
import uuid
from itertools import islice
import time
import json
import boto3

from langchain.prompts import PromptTemplate

#Users previous chat history is provided in <history> tags.
# <history>
# {history}
# </history>

PROMPT_TEMPLATE2 = """
System: You are a financial advisor AI system, and provides answers to questions by using fact based and statistical information when possible. 
Use the following pieces of information to provide a concise answer to the question enclosed in <question> tags. 

If the question is not related to financial information, politely inform the user that you can only answer related to financial questions.
Provide suggestion using the 'preferred_asset_class' tag specified in <userData> tag.
Based on the suggestions generated, provide top 5 investment products from each of the 'preferred_asset_class' in a csv format in a separate tag as <investmentOptions>.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

<question>
{question}
</question>

<userData>
{userData}
</userData>

The response should be specific and use statistics or numbers when possible.
"""

api_url = os.environ.get("API_URL")
data_store_api_url = os.environ.get("DATA_STORE_API_URL")
use_lambda_client = os.environ.get("USE_LAMBDA_CLIENT")

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

# using retrieve and generate
def generate_prompt_with_history(question, history,userDict):
    LLM_PROMPT = PromptTemplate(template=PROMPT_TEMPLATE2, input_variables=["question"],optional_variables=["userData"]) #"history",
    userDict["history"]=''
    json_string = json.dumps(userDict)
    qa_prompt = LLM_PROMPT.format(question=question,userData=json_string) #history=history,
    print(qa_prompt)
    return qa_prompt

def get_session_id():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = None

# Function to store user information
def store_user_info(userDict):
    request_body = {
        'body': {
            'user_profile': userDict
            }
    }
    try:
        response = requests.post(data_store_api_url, json=request_body)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        api_response = response.text
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        api_response = 'Sorry, something went wrong. Please try again later.'

# Function to get the bot's response
def get_bot_response(userInput):
    request_body = {
        "message": userInput,
        "sessionId":st.session_state['session_id']
    }
    #print(request_body)
    api_json = dict()
    bot_response = ''
    
    try:
        if use_lambda_client:
            lambda_client = boto3.client('lambda')
            lambda_response = lambda_client.invoke(
                FunctionName='Agent',
                InvocationType='RequestResponse',
                Payload=json.dumps(request_body)
            )
            
            response = json.loads(lambda_response['Payload'].read().decode('utf-8'))
            api_json = response['body']
        else:
            response = requests.post(api_url, json=request_body)
            #print(bot_response)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            api_response = response.text
            api_json = json.loads(api_response)
        #print(api_response)
        bot_response = api_json["output"].replace('$','\\$') #.replace('\\n', '  <br />  ')
        
        #else:
        #    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        bot_response = 'Sorry, something went wrong. Please try again later.'

    if "sessionId" in api_json.keys():
        st.session_state['session_id'] = api_json["sessionId"]
    if "citations" in api_json.keys(): 
        citations = api_json["citations"]
        #print(citations)
        st.session_state.messages.append({"role": "assistant", "content": bot_response, "citations":citations})
    return bot_response

def disable():
    st.session_state["disabled"] = True

def get_user_inputs(ctr):
    # Create a form for user input
    with ctr: 
        with st.form("user_input_form"):

            # Get user input for name
            name = st.text_input("Enter your Name:", key="name",disabled=st.session_state.disabled)

            # Get user input for age
            age = st.number_input("Enter your Age:", min_value=0, step=1, max_value=100,disabled=st.session_state.disabled)

            # Get user input for income
            income = st.number_input("Enter your Annual Income:", min_value=0, step=100, max_value=1000000000,disabled=st.session_state.disabled,value=0)

            #Get user input for total networth
            total_networth = st.number_input("Enter your Total Networth:", min_value=0, step=100, max_value=1000000000,disabled=st.session_state.disabled,value=0)

            #Get user input for investment horizon
            investment_horizon = st.radio("Select your Investment Horizon:", options=["Short Term(Less than 5 years)", "Medium Term(5 to 10 years)", "Long Term(10+ years)"],horizontal=True,disabled=st.session_state.disabled)

            #Get user input for financial goal
            financial_goal = st.radio("Select your Financial Goal:", options=["Retirement", "Education", "Income Generation","Travel","Home Purchase"],horizontal=True,disabled=st.session_state.disabled)

            #Get user input for risk tolerance
            risk_tolerance = st.radio("Select your Risk Tolerance:", options=["Low", "Moderate", "High"],horizontal=True,disabled= st.session_state.disabled)

            #Get user input for preferred asset class
            preferred_asset_class = st.multiselect("Select your Preferred Asset Class:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate", "CDs(Certificate of Deposits)"],disabled=st.session_state.disabled)

            #Get user input for existing investments
            #existing_investments = st.multiselect("Select your Existing Investments:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate", "CDs(Certificate of Deposits)", "None"],disabled=st.session_state.disabled)

            st.write("Enter the value of your Current Portfolio:")
            left,middle, right = st.columns(3)
            with left:
                stocks_investments = st.number_input("Stocks:", min_value=0, step=1, max_value=1000000000, disabled=st.session_state.disabled, value=0)
            with middle:
                bonds_investments = st.number_input("Bonds:", min_value=0, step=1, max_value=1000000000, disabled=st.session_state.disabled, value=0)
            with right:
                real_estate_investments = st.number_input("Real Estate:", min_value=0, step=1, max_value=1000000000, disabled=st.session_state.disabled, value=0)
            
            current_portfolio = {"Stocks":stocks_investments, "Bonds":bonds_investments, "Real Estate":real_estate_investments}
            # Submit button
            submitted = st.form_submit_button("Submit",on_click=disable,disabled=st.session_state.disabled)
            if submitted:
                userDict = {"session_id":st.session_state['session_id'],"name": name, "income": income, "total_networth": total_networth, "age": age, "investment_horizon": investment_horizon, "financial_goal": financial_goal, "risk_tolerance": risk_tolerance, "preferred_asset_class": preferred_asset_class, "current_portfolio": current_portfolio,"history":st.session_state.messages}
                return userDict

def update_user_dict(userDict, history):
    userDict["history"]=history
    return userDict

def generate_prompt(userDict):
    prompt = f"""Generate a personalized investment portfolio based on the following user information: 
    Name: {userDict['name']}, 
    Income: {userDict['income']}, 
    Total Networth: {userDict['total_networth']}, 
    Age: {userDict['age']}, 
    Investment Horizon: {userDict['investment_horizon']}, 
    Financial Goal: {userDict['financial_goal']}, 
    Risk Tolerance: {userDict['risk_tolerance']}, 
    Preferred Asset Class: {', '.join(userDict['preferred_asset_class'])}, 
    Current Portfolio: {userDict['current_portfolio']}
    """

    prompt2 = f"""Generate a personalized investment portfolio based on the following user information for {userDict['name']} with age of {userDict['age']} having annual income of {userDict['income']} and having total networth of {userDict['total_networth']}.
    {userDict['name']} is looking to invest for {userDict['investment_horizon']} with their financial goal of {userDict['financial_goal']}.
    {userDict['name']}'s risk tolerance is {userDict['risk_tolerance']}. Their preferred investment asset classes are {', '.join(userDict['preferred_asset_class'])} and having current portfolio of {userDict['current_portfolio']}.
    """    

    prompt = prompt.replace("\n", "")
    return prompt

def update_chat_messages(container):
    #Display chat messages
    message = st.session_state.messages[-1]
    with container:
        with st.chat_message(message["role"]):
            #resp = message["content"].replace('\\n', '  <br />  ')
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

# Streamlit app
def app():
    get_session_id()
    

    st.markdown("<h1 style='text-align: center;'>AI Wizards Financial Advisor</h1>", unsafe_allow_html=True)
    #st.title("AI Wizards Financial Advisor")
    #st.write("Welcome to the your Financial Advisor! Enter the following information:")
    st.markdown("<p style='text-align: center;'>Welcome to the your Financial Advisor! Enter the following information:</p>", unsafe_allow_html=True)
    
    row1= st.columns(2)    
    with row1[0]:
        left_container = st.container(height=920)
    with row1[1]:
        right_container = st.container(height=840)

    # Initialize conversation history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Enter user information","citations":None}]
    # Create a form for user input
    userDict = get_user_inputs(left_container)
    
    for message in st.session_state.messages:
        with right_container:
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

    # Get the bot's response
    if userDict:
        userPrompt= generate_prompt(userDict)
        question = generate_prompt_with_history(userPrompt,st.session_state.messages,userDict)
        st.session_state.messages.append({"role": "user", "content": userPrompt,"citations":None})
        update_chat_messages(right_container)
        with right_container:
            with st.spinner('Generating response...'):
                bot_response = get_bot_response(question)
        
        
        update_chat_messages(right_container)
        userDict = update_user_dict(userDict, st.session_state.messages)
        
    userInput = row1[1].chat_input("Ask your question to improve the response or type Reset to start from beginning",disabled=not(st.session_state.disabled))

    if userInput:
        if userInput.lower() == "reset":
            st.session_state["disabled"] = False
            userDict=None
            st.rerun()
        
        userDict = st.session_state.user_dict
        st.session_state.messages.append({"role": "user", "content": userInput,"citations":None})
        update_chat_messages(right_container)
        question = generate_prompt_with_history(userInput,st.session_state.messages,userDict)
        with right_container:
            with st.spinner('Generating response...'):
                bot_response = get_bot_response(question)

        update_chat_messages(right_container)
        userDict = update_user_dict(userDict, st.session_state.messages)
    
    # Store user information
    if userDict:
        if st.session_state['session_id'] :
            userDict["session_id"]= st.session_state['session_id']
        store_user_info(userDict)
        
    st.session_state.user_dict = userDict

if __name__ == "__main__":
    app()
