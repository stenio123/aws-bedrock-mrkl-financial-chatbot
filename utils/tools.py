from bs4 import BeautifulSoup
import re
import requests
import json
from datetime import date, timedelta, datetime
import warnings
warnings.filterwarnings("ignore")

import yfinance as yf
yf.pdr_override() 

#from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.agents import load_tools, AgentType, Tool, initialize_agent
from pandas_datareader import data as pdr
import pandas as pd

from utils.llm_wrapper import get_llm
from utils.db_tool_helper import get_db_chain
from utils.rag_tool_helper import get_rag_chain_response, run_rag_search

def get_stock_ticker(query):
    template = """You are a helpful assistant who extract company name from the human input.Please only output the company"""
    human_template = "{text}"

    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", human_template),
    ])

    llm = get_llm()
    llm_chain = LLMChain(
        llm=llm,
        prompt=chat_prompt
    )
    output = llm_chain(query)

    company_name=output['text'].strip()
    db_chain = get_db_chain()
    company_ticker = db_chain("\n\nHuman: What is the ticker symbol for " + str(company_name) + " in stock ticker table? \n\nAssistant:")

    return company_name, company_ticker['result']

def get_stock_price(ticker, history=10):
    print("Looking for prices of stock:")
    print (ticker)
    today = date.today()
    start_date = today - timedelta(days=history)
    data = pdr.get_data_yahoo(ticker, start=start_date, end=today)
    dataname= ticker+'_'+str(today)
    return data, dataname

# Fetch top 5 google news for given company name
def google_query(search_term):
    if "news" not in search_term:
        search_term=search_term+" stock news"
    url=f"https://www.google.com/search?q={search_term}"
    url=re.sub(r"\s","+",url)
    return url

def get_recent_stock_news(company_name):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}

    g_query=google_query(company_name)
    res=requests.get(g_query,headers=headers).text
    soup=BeautifulSoup(res,"html.parser")
    news=[]
    # TODO: this is very brittle and will probably break eventually
    # Consider using https://newsapi.org/ instead if not working
    for n in soup.find_all("div","n0jPhd ynAwRc tNxQIb nDgy9d"):
        news.append(n.text)
    for n in soup.find_all("div","IJl0Z"):
        news.append(n.text)

    if len(news)>6:
        news=news[:4]
    else:
        news=news
    news_string=""
    for i,n in enumerate(news):
        news_string+=f"{i}. {n}\n"
    top5_news="Recent News:\n\n"+news_string
    
    return top5_news

def stock_news_search(company_name):
    search=DuckDuckGoSearchRun()
    return search("Stock news about " + company_name)

search = DuckDuckGoSearchAPIWrapper()
def search_with_links(query, num_results=5):
    search_results = search.results(query, num_results)
    formatted_results = []

    for result in search_results:
        title = result['title']
        snippet = result['snippet']
        link = result['link']
        formatted_results.append(f"{title}\n{snippet}\nURL: {link}\n")

    return formatted_results

# Get financial statements from Yahoo Finance
def get_financial_statements(ticker):
    if "." in ticker:
        ticker=ticker.split(".")[0]
    else:
        ticker=ticker
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1]>=3:
        balance_sheet=balance_sheet.iloc[:,:3]    # Only captures last 3 years of data
    balance_sheet=balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet

def query_call_transcript(question):
    return run_rag_search("general information on " + question)

def get_date():
    return (F'Today is {datetime.now().strftime("%Y-%m-%d")}')

def analyze_stock(query):
    company_name,ticker=get_stock_ticker(query)
    print("start analyze job for ", ticker)
    print({"Query":query,"company_name":company_name,"Ticker":ticker})
    stock_data=get_stock_price(ticker,history=10)
    stock_financials=get_financial_statements(ticker)
    stock_news=get_recent_stock_news(company_name)
    print("Retrieving stock data, latest financials and news ....")

    llm = get_llm()
    available_information=f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    analysis=llm(f"""\n\nHuman: Give detail stock analysis, Use the available data and provide investment recommendation. \
             The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
             User question: {query} \
             You have the following information available about {company_name}. Write (5-8) pointwise investment analysis to answer user query, At the end conclude with proper explaination.Try to Give positives and negatives  : \
              {available_information} \
                \n\nAssistant: """
             )
    return analysis

def run_tests():
    company_name, company_ticker = get_stock_ticker("What is the main business of Amazon?")
    print(company_name, company_ticker)
    print(get_stock_price("TSLA"))
    print(get_recent_stock_news("Meta"))
    print(stock_news_search("TSLA"))
    print(get_financial_statements("AMZN"))
    analyze_result=anazlyze_stock("Is Amazon a good investment choice right now?")
    print(analyze_result)

#general_search(" what is Amazon company?")
#run_tests()