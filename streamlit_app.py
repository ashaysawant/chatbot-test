import streamlit as st
#from streamlit_chat import message

# Initialize conversation history
conversation = []
if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

# Function to get the bot's response
def get_bot_response(userInput):
    # This is just a simple example, you can replace this with your own logic
    # or integrate with a language model API
    sample_response="""Based on your income, age, investment horizon, investment objective, investment risk, existing investments, total networth, and the provided information, we recommend the following investment options:\n
             1. Stock A: 10% growth potential, 5-year return, suitable for investors with low risk tolerance
             2. Mutual Fund XYZ: 8% growth potential, 10-year return, suitable for investors with moderate risk tolerance
             3. Mutual Fund ABC: 12% growth potential, 5-year return, suitable for investors with high risk tolerance
             4. ETF DEF: 15% growth potential, 10-year return, suitable for investors with high risk tolerance
             """
    return sample_response

def disable():
    st.session_state["disabled"] = True

def get_user_inputs():
    # Create a form for user input

    with st.form("user_input_form"):

        #TODO: need to restore previously entered values

        # Get user input for name
        name = st.text_input("Enter your name:", key="name",disabled=st.session_state.disabled)

        # Get user input for income
        income = st.number_input("Enter your income:", min_value=0.0, step=100.0, max_value=1000000000.0,disabled=st.session_state.disabled)

        #Get user input for total networth
        total_networth = st.number_input("Enter your Total Networth:", min_value=0.0, step=1000.0, max_value=1000000000.0,disabled=st.session_state.disabled)

        # Get user input for age
        age = st.number_input("Enter your age:", min_value=0, step=1, max_value=100,disabled=st.session_state.disabled)

        #Get user input for investment horizon
        investment_horizon = st.radio("Select your Investment Horizon:", options=["Short Term(Less than 5 years)", "Medium Term(5 to 10 years)", "Long Term(10+ years)"],horizontal=True,disabled=st.session_state.disabled)

        #Get user input for investment objective
        investment_objective = st.radio("Select your Investment Objective:", options=["Retirement", "Education", "Income Generation"],horizontal=True,disabled=st.session_state.disabled)

        #Get user input for investment risk
        investment_risk = st.radio("Select your Investment Risk:", options=["Low", "Moderate", "High"],horizontal=True,disabled= st.session_state.disabled)

        #Get user input for preferred asset class
        preferred_asset_class = st.multiselect("Select your Preferred Asset Class:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs"],disabled=st.session_state.disabled)

        #Get user input for existing investments
        existing_investments = st.multiselect("Select your Existing Investments:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs", "None"],disabled=st.session_state.disabled)

        # Submit button
        submitted = st.form_submit_button("Submit",on_click=disable,disabled=st.session_state.disabled)
        if submitted:
            userDict = {"name": name, "income": income, "total_networth": total_networth, "age": age, "investment_horizon": investment_horizon, "investment_objective": investment_objective, "investment_risk": investment_risk, "preferred_asset_class": preferred_asset_class, "existing_investments": existing_investments}
            return userDict

def generate_prompt(userDict):
    prompt = f"""Generate a personalized investment portfolio based on the following user information:
    Name: {userDict['name']}
    Income: {userDict['income']}
    Total Networth: {userDict['total_networth']}
    Age: {userDict['age']}
    Investment Horizon: {userDict['investment_horizon']}
    Investment Objective: {userDict['investment_objective']}
    Investment Risk: {userDict['investment_risk']}
    Preferred Asset Class: {', '.join(userDict['preferred_asset_class'])}
    Existing Investments: {', '.join(userDict['existing_investments'])}
    """
    return prompt

# Streamlit app
def app():
    st.title("AI Wizards Fiancial Advisor")
    st.write("Welcome to the your Finacial Advisor! Enter the following information:")

    # Initialize conversation history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Enter user information"}]

    # Create a form for user input
    userDict = get_user_inputs()
        
    # Get the bot's response
    if userDict:
        userPrompt= generate_prompt(userDict)
        st.session_state.messages.append({"role": "user", "content": userPrompt})
    
        bot_response = get_bot_response(userPrompt)
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if st.session_state.messages[-1]["role"] =="assistant" and st.session_state.messages[-1]["content"] !="Enter user information":
        userInput = st.chat_input("Ask your question to improve the response or type Reset to start from beginning")

        if userInput:
            if userInput.lower() == "reset":
                st.session_state["disabled"] = False
                userDict=None
                st.session_state.messages = [{"role": "assistant", "content": "Enter user information"}]
                st.rerun()
            
            with  st.chat_message(name="user"):
                st.text_area(label="You:", value=userInput, height=100)
            
            bot_response = get_bot_response(userInput)
            with  st.chat_message(name="ai"):
                st.text_area(label="Here are your investment recommendations:",value=bot_response,height=300)

if __name__ == "__main__":
    app()
