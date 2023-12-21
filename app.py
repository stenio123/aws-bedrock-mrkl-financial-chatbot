from pathlib import Path

import streamlit as st

from langchain.agents import AgentType
from langchain.agents import initialize_agent, Tool
from langchain.callbacks import StreamlitCallbackHandler
#from langchain.chains import LLMMathChain
from langchain.llms import OpenAI
from datetime import datetime

from streamlit_cognito_auth import CognitoAuthenticator

from utils.llm_wrapper import get_llm
from utils.tools import get_stock_ticker, get_stock_price, get_date, get_recent_stock_news, get_financial_statements, query_call_transcript, search_with_links#, analyze_investor_call

import os
from dotenv import load_dotenv
load_dotenv()

# If running from container, ensure you pass these as env vars
cognito_client_id=os.getenv('COGNITO_CLIENT_ID')
cognito_user_pool_id=os.getenv('COGNITO_USER_POOL_ID')
cognito_client_secret=os.getenv('COGNITO_CLIENT_SECRET')
cognito_domain_name=os.getenv('COGNITO_DOMAIN_NAME')

authenticator = CognitoAuthenticator(
    app_client_id=cognito_client_id,
    pool_id=cognito_user_pool_id,
    #app_client_secret=cognito_client_secret,
)

is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()


def logout():
    authenticator.logout()


with st.sidebar:
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("Logout", "logout_btn", on_click=logout)

def handle_form_submission():
    user_input = st.session_state.user_input

    if user_input:  # Check if there is user input
        output_container = st.container()
        output_container.chat_message("user").write(user_input)

        answer_container = output_container.chat_message("assistant", avatar="🤖")
        st_callback = StreamlitCallbackHandler(answer_container)

        answer = mrkl.run(user_input, callbacks=[st_callback])

        answer_container.write(answer)
        st.session_state.user_input = ""  # Clear the input after processing
        st.session_state.input_key += 1  # Increment the key to reset the input field
        st.session_state.disabled = True  # Disable input after submission

def reset_form():
    # Resetting the user input and clearing the UI
    st.session_state.user_input = ""
    st.session_state.input_key += 1  # Increment the key to reset the input field
    st.session_state.disabled = False  # Re-enable input
    st.experimental_rerun()

"# 🤖🔗 MRKL"

# Tools setup
llm = get_llm()

tools=[
    Tool(
        name="Get company ticker",
        func=get_stock_ticker,
        description="Use this when you need to retrieve a company stock ticker symbol. Input only the company name. Output is the stock ticker symbol"
    ),
    Tool(
        name="Get stock data",
        func=get_stock_price,
        description="Use when you are asked to evaluate or analyze the price of a stock or company. Required input: use only company stock ticker symbol, do not add anything else to the input. Output is the historical stock price data for the given stock ticker symbol. "
    ),
    Tool(
        name="Get financial statements",
        func=get_financial_statements,
        description="""
                        This tool will return the company's latest financial statement, which can be used to evaluate its historic performance.
                        With this tool It is crucial to provide ONLY the company's stock ticker symbol as input. 
                        Do not include any additional words, phrases, or contextual information. 
                        For instance, input 'TSLA' rather than 'Tesla' or 'Tesla's financial statement'.

                        Example usage:
                        - Correct: Input 'TSLA'
                        - Incorrect: Input 'Tesla Q3 2022 financial statement'
                        - Correct: Input 'TSLA'
                        - Incorrect: Input 'Tesla'
                        - Correct: Input 'AMZN'
                        - Incorrect: Input 'Amazon'"""
    ),
    Tool(
        name="Get date",
        func=get_date,
        description="useful for retrieving todays date",
    ), 
    Tool(
        name="Search",
        func=search_with_links,
        description="useful for when you need to answer questions about future risks, opportunities, current events, or if you cant find the answer with previous tools. Can be used to retrieve financial call transcripts for companies other than Amazon. You should ask targeted questions",
    ), 
    Tool(
        name="Get Non-Amazon call transcript",
        func=search_with_links,
        description="Useful for retrieving information related to investor calls for any company other than Amazon.Input: targeted questions with keywords from the user query",
    ), 
    Tool(
    name="Get Amazon call transcript",
    func=query_call_transcript,
    description="This tool is designed to interpret queries related to Amazon's investor calls and provide summarized information accordingly. Instead of retrieving the entire call transcript, it analyzes the content to return a concise summary relevant to the user's specific question about the call. Input: user's query regarding topics discussed in Amazon's investor call."
)
    
]

# Initialize agent
updated_prompt_template = """Human: You are a financial advisor. Give stock recommendations, analysis or support to related questions.

Todays date is {todays_date}
When asked related to a company, stock or financial analysis, if necessary but not provided the stock symbol by user, use "Get company ticker" to retrieve stock ticker. If that fails, use the "Search" tool. 
Use all available tools if they will help answering the question.
After each observation, assess whether additional information is needed or if you are ready to formulate a final answer. Avoid repeating actions that have already provided sufficient information. 

If you encounter unclear or unexpected responses:
- Re-evaluate the information and consider an alternative action using only the available tools.
- If necessary, rephrase your action input for clarity.
- Use the 'Search' tool to gather more context.
- DO NOT ASK USER FOR ADDITIONAL INFORMATION OR INPUTS

If you are unable to continue, stop and present Final Answer justifying steps taken.

Use the following format:
Question: the input question you must answer
Thought: Consider what information is needed to answer the question. Prioritize actions that provide unique and relevant information.
Action: the action to take, should be one of [Get company ticker, Get stock data, Get financial statements, Search, Get Amazon call transcript, Get Non-Amazon call transcript]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation will repeat N times until you have sufficient information.
Thought: I now know the final answer based on my observation
Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points. Provide references, links and numbers if available.

"""
updated_prompt = updated_prompt_template.format(
    todays_date=datetime.now().strftime("%Y-%m-%d")
)
final_updated_prompt = updated_prompt + """
Question: {input}

Assistant:
{agent_scratchpad}
"""

mrkl = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True,verbose=True)
mrkl.agent.llm_chain.prompt.template=final_updated_prompt



# Initialize session state for user input, input key, and disabled flag if they don't exist
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0
if 'disabled' not in st.session_state:
    st.session_state.disabled = False

# Display the form for the user's question
with st.form(key=f"question_form_{st.session_state.input_key}"):
    st.session_state.user_input = st.text_input("Hello, how may I help you?", key=f"question_input_{st.session_state.input_key}", disabled=st.session_state.disabled)
    submit_clicked = st.form_submit_button("Submit Question")

# Call the function to handle form submission
if submit_clicked:
    handle_form_submission()

# Button for resetting the form, placed outside the form
if st.button("Ask Another Question"):
    reset_form()