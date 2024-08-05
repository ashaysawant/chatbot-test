import streamlit as st
st.set_page_config(layout="wide")
import requests
import os
import uuid

api_url = os.environ.get("API_URL")
data_store_api_url = os.environ.get("DATA_STORE_API_URL")

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

def get_session_id():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid.uuid4())
    return st.session_state['session_id']

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
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        api_response = 'Sorry, something went wrong. Please try again later.'

# Function to get the bot's response
def get_bot_response(userInput):
    request_body = {
        'message': userInput
    }
    try:
        response = requests.post(api_url, json=request_body)
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        bot_response = response.text
    except requests.exceptions.RequestException as e:
        print(f'Error: {e}')
        bot_response = 'Sorry, something went wrong. Please try again later.'

    return bot_response

def disable():
    st.session_state["disabled"] = True

def get_user_inputs(container):
    # Create a form for user input
    with container: 
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

            #Get user input for investment objective
            investment_objective = st.radio("Select your Investment Objective:", options=["Retirement", "Education", "Income Generation"],horizontal=True,disabled=st.session_state.disabled)

            #Get user input for investment risk
            investment_risk = st.radio("Select your Investment Risk:", options=["Low", "Moderate", "High"],horizontal=True,disabled= st.session_state.disabled)

            #Get user input for preferred asset class
            preferred_asset_class = st.multiselect("Select your Preferred Asset Class:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate", "CDs(Certificate of Deposits)"],disabled=st.session_state.disabled)

            #Get user input for existing investments
            existing_investments = st.multiselect("Select your Existing Investments:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs", "Real Estate", "CDs(Certificate of Deposits)", "None"],disabled=st.session_state.disabled)

            # Submit button
            submitted = st.form_submit_button("Submit",on_click=disable,disabled=st.session_state.disabled)
            if submitted:
                userDict = {"session_id":st.session_state['session_id'],"name": name, "income": income, "total_networth": total_networth, "age": age, "investment_horizon": investment_horizon, "investment_objective": investment_objective, "investment_risk": investment_risk, "preferred_asset_class": preferred_asset_class, "existing_investments": existing_investments}
                return userDict

def generate_prompt(userDict):
    prompt = f"""Generate a personalized investment portfolio based on the following user information: 
    Name: {userDict['name']}, 
    Income: {userDict['income']}, 
    Total Networth: {userDict['total_networth']}, 
    Age: {userDict['age']}, 
    Investment Horizon: {userDict['investment_horizon']}, 
    Investment Objective: {userDict['investment_objective']}, 
    Investment Risk: {userDict['investment_risk']}, 
    Preferred Asset Class: {', '.join(userDict['preferred_asset_class'])}, 
    Existing Investments: {', '.join(userDict['existing_investments'])}
    """
    prompt = prompt.replace("\n", "")
    return prompt

# Streamlit app
def app():
    print(api_url)
    print(get_session_id())
    st.title("AI Wizards Fiancial Advisor")
    st.write("Welcome to the your Finacial Advisor! Enter the following information:")
    
    row1= st.columns(2)
    
    with row1[0]:
        left1 = st.container(height=880)

    with row1[1]:
        right1 = st.container(height=800)

    # Initialize conversation history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Enter user information"}]

    # Create a form for user input
    userDict = get_user_inputs(left1)
    
    # Get the bot's response
    if userDict:
        # Store user information
        store_user_info(userDict)

        userPrompt= generate_prompt(userDict)
        st.session_state.messages.append({"role": "user", "content": userPrompt})
    
        bot_response = get_bot_response(userPrompt)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    #with right:
    userInput = row1[1].chat_input("Ask your question to improve the response or type Reset to start from beginning",disabled=not(st.session_state.disabled))

    if userInput:
        if userInput.lower() == "reset":
            st.session_state["disabled"] = False
            userDict=None
            st.rerun()
        
        st.session_state.messages.append({"role": "user", "content": userInput})            
        bot_response = get_bot_response(userInput)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display chat messages
    for message in st.session_state.messages:
        with right1:
            with st.chat_message(message["role"]):
                st.write(message["content"])

if __name__ == "__main__":
    app()
