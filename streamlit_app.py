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
        # Get user input for income
        income = st.number_input("Enter your income:", min_value=0.0, step=100.0, max_value=1000000000.0)

        # Get user input for age
        age = st.number_input("Enter your age:", min_value=0, step=1, max_value=100)

        #Get user input for investment horizon
        investment_horizon = st.radio("Select your Investment Horizon:", options=["Short Term", "Medium Term", "Long Term"],horizontal=True)

        #Get user input for investment objective
        investment_objective = st.radio("Select your Investment Objective:", options=["Retirement", "Education", "Income Generation"],horizontal=True)

        #Get user input for investment risk
        investment_risk = st.radio("Select your Investment Risk:", options=["Low", "Moderate", "High"],horizontal=True)

        
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
    
    # Display conversation history
    #for sender, message in conversation:
    #    message(f"{sender}: {message}", is_user=(sender == "You"), key=f"{sender}_{len(conversation)}")

if __name__ == "__main__":
    app()
