import streamlit as st
from streamlit_chat import message

# Initialize conversation history
conversation = []

# Function to get the bot's response
def get_bot_response(income, age):
    # This is just a simple example, you can replace this with your own logic
    # or integrate with a language model API
    if user_input.lower() == "hello":
        return "Hello! How can I assist you today?"
    elif user_input.lower() == "bye":
        return "Goodbye!"
    else:
        return "I'm sorry, I didn't understand your query. Can you please rephrase it?"

# Streamlit app
def app():
    st.title("AI Wizards Fiancial Advisor")
    st.write("Welcome to the your Finacial Advisor! Enter the following information:")

    # Create a form for user input
    with st.form("user_input_form"):

        # Get user input for name
        name = st.text_input("Enter your name:", key="name")

        # Get user input for income
        income = st.number_input("Enter your income:", min_value=0.0, step=100.0, max_value=1000000000.0)

        #Get user input for total networth
        total_networth = st.number_input("Enter your Total Networth:", min_value=0.0, step=1000.0, max_value=1000000000.0)

        # Get user input for age
        age = st.number_input("Enter your age:", min_value=0, step=1, max_value=100)

        #Get user input for investment horizon
        investment_horizon = st.radio("Select your Investment Horizon:", options=["Short Term(Less than 5 years)", "Medium Term(5 to 10 years)", "Long Term(10+ years)"],horizontal=True)

        #Get user input for investment objective
        investment_objective = st.radio("Select your Investment Objective:", options=["Retirement", "Education", "Income Generation"],horizontal=True)

        #Get user input for investment risk
        investment_risk = st.radio("Select your Investment Risk:", options=["Low", "Moderate", "High"],horizontal=True)

        #Get user input for preferred asset class
        preferred_asset_class = st.multiselect("Select your Preferred Asset Class:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs"])

        #Get user input for existing investments
        existing_investments = st.multiselect("Select your Existing Investments:", options=["Stocks", "Bonds", "Mutual Funds", "ETFs", "None"])

        
        # Get user input
        #user_input = st.text_input("You: ", key="user_input")

        # Submit button
        submitted = st.form_submit_button("Submit")
        if submitted:
            bot_response = get_bot_response(user_input)
            conversation.append(("You", user_input))
            conversation.append(("Bot", bot_response))

            # Clear user input
            st.session_state["user_input"] = ""
    
    sample_response="""Based on your income, age, investment horizon, investment objective, investment risk, existing investments, total networth, and the provided information, we recommend the following investment options:\n
             1. Stock A: 10% growth potential, 5-year return, suitable for investors with low risk tolerance
             2. Mutual Fund XYZ: 8% growth potential, 10-year return, suitable for investors with moderate risk tolerance
             3. Mutual Fund ABC: 12% growth potential, 5-year return, suitable for investors with high risk tolerance
             4. ETF DEF: 15% growth potential, 10-year return, suitable for investors with high risk tolerance
             """
    
    with  st.chat_message(name="ai"):
        st.text_area(label="Here are your investment recommendations:",value=sample_response,height=300)

    st.chat_input("Ask your question to improve the response")
    # Display conversation history
    #for sender, message in conversation:
    #    message(f"{sender}: {message}", is_user=(sender == "You"), key=f"{sender}_{len(conversation)}")

if __name__ == "__main__":
    app()
