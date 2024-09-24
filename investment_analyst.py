import streamlit as st
import pandas as pd
import numpy as np
import json
from streamlit_pills import pills
import time
import pyperclip
import random

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

<userData>
{userData}
</userData>

The response should be specific and use statistics or numbers when possible.
"""
#Also give reference to your souces.

def update_chat_messages(container):
    #Display chat messages
    message = st.session_state.ia_messages[-1]
    with container:
        with st.chat_message(message["role"]):
            st.markdown(message["content"],unsafe_allow_html=True)
            # if "citations" in message.keys() and message["citations"] is not None:
            #     with st.expander("See Context Information"):
            #         for citation in message["citations"]:
            #             retrievedReferences = citation["retrievedReferences"]
            #             for reference in retrievedReferences:
            #                 st.markdown("Reference : "+reference["content"]["text"].replace('$','\\$'), unsafe_allow_html=True)
            #                 location = reference["location"]
            #                 if "S3" == location["type"]:
            #                     st.caption("Location : "+ location["s3Location"]["uri"], unsafe_allow_html=True)
            #                 elif "WEB" == location["type"]:
            #                     st.caption("Location : "+ location["webLocation"]["url"], unsafe_allow_html=True)
            #                 st.divider()
            # else:
            #     st.empty()


def app():
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
                # if "citations" in message.keys() and message["citations"] is not None:
                #     with st.expander("See Context Information"):
                #         for citation in message["citations"]:
                #             retrievedReferences = citation["retrievedReferences"]
                #             for reference in retrievedReferences:
                #                 st.markdown("Reference : "+reference["content"]["text"].replace('$','\\$'), unsafe_allow_html=True)
                #                 location = reference["location"]
                #                 if "S3" == location["type"]:
                #                     st.caption("Location : "+ location["s3Location"]["uri"], unsafe_allow_html=True)
                #                 elif "WEB" == location["type"]:
                #                     st.caption("Location : "+ location["webLocation"]["url"], unsafe_allow_html=True)
                #                 st.divider()
                # else:
                #     st.empty()

    # with open("data/GDP.json", "r") as file:
    #     gdp = json.load(file,object_hook=as_float)['data']
    #     print(str(gdp))
    #     chart_data = pd.DataFrame(gdp,columns=['date','value'])
    #     ctr.line_chart(chart_data,x="date",y="value")
    # pills_key = random.random()
    selected = pills("Most frequently asked questions", questions,index=None,clearable=True)#,key=random.random())
    # if selected:
    #     userInput = st.chat_input(selected)#,disabled=not(st.session_state.disabled))
    # else:
    #
    if selected:
        # st.session_state.pills_key=None
        msg = st.toast("Copied question to clipboard")
        pyperclip.copy(selected)

        # st_copy_to_clipboard(selected)

    userInput = st.chat_input("Enter your question")#,disabled=not(st.session_state.disabled))
    
    if userInput:
        st.session_state.ia_messages.append({"role": "user", "content": userInput,"citations":None})
        update_chat_messages(ctr)

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

app()
