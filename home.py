import streamlit as st

investment_analyst_page = st.Page("investment_analyst.py", title="Investment Anayst", icon=":material/finance:")
financial_advisor_page = st.Page("financial_advisor.py", title="Financial Advisor", icon=":material/savings:")

pg = st.navigation([investment_analyst_page, financial_advisor_page])
st.set_page_config(page_title="Home",layout="wide")#, page_icon=":material/edit:")
pg.run()