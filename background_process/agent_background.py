import sys
import os
# from https://stackoverflow.com/questions/16981921/relative-imports-in-python-3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from langchain.agents import load_tools
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain import LLMMathChain
from langchain.agents import initialize_agent 

from utils.llm_wrapper import get_llm
from utils.tools import get_stock_ticker, get_stock_price, get_recent_stock_news, get_financial_statements#, general_search#, analyze_investor_call

llm = get_llm()

# Making tool list

tools=[
    Tool(
        name="get company ticker",
        func=get_stock_ticker,
        description="Get the company stock ticker"
    ),
    Tool(
        name="get stock data",
        func=get_stock_price,
        description="Use when you are asked to evaluate or analyze a stock. This will output historic share price data. You should input the the stock ticker to it "
    ),
    Tool(
        name="get recent news",
        func=get_recent_stock_news,
        description="Use this to fetch recent news about stocks"
    ),

    Tool(
        name="get financial statements",
        func=get_financial_statements,
        description="Use this to get financial statement of the company. With the help of this data companys historic performance can be evaluaated. You should input stock ticker to it"
    ) 


]

updated_prompt="""Human: You are a financial advisor. Give stock recommendations for given query based on following instructions. 
<instructions>
Answer the following questions as best you can. You have access to the following tools:

get company ticker: Use when you need to extract company name and stock ticker. This tool will output company name and stock ticker. You should input the human input to it.
get stock data: Use when you are asked to evaluate or analyze a stock. This will output historic share price data. You should input the stock ticker to it.
get recent news: Use this to fetch recent news about stocks. This will output company stock news. You should innput the company name to it.
get financial statements: Use this to get financial statement of the company. With the help of this data companys historic performance can be evaluaated. You should input stock ticker to it
</instructions>

<analysis steps>
Note- if you fail in satisfying any of the step below, Just move to next one
1) Use "get company ticker" tool to get the company name and stock ticker. Output- company name and stock ticker
2) Use "get stock data" tool to gather stock info. Output- Stock data
3) Use "get recent news" tool to search for latest stock realted news. Output- Stock news
4) Use "get financial statements" tool to get company's historic financial data. Output- Financial statement
5) Analyze the stock based on gathered data and give detail analysis for investment choice. provide numbers and reasons to justify your answer. Mention additional resources that could be used for further research. Output - stock analysis.
</analysis steps>

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do, Also try to follow steps mentioned above
Action: the action to take, should be one of [get company ticker, get stock data, get recent news, get financial statements]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation will repeat once for each <analysis step>.
Thought: I now know the final answer based on my observation
Final Answer: the final answer to the original input question is the full detailed explanation from the Observation provided as bullet points. Provide references and numbers.

Question: {input}

Assistant:
{agent_scratchpad}

"""

zero_shot_agent=initialize_agent(
    llm=llm,
    agent="zero-shot-react-description",
    tools=tools,
    verbose=True,
    max_iteration=2,
    return_intermediate_steps=True,
    handle_parsing_errors=True,
)

zero_shot_agent.agent.llm_chain.prompt.template=updated_prompt

def query_agent(query):
    return zero_shot_agent(f"\n\nHuman: {query} \n\nAssistant:")

def query_agent_company(company):
    query = f"\n\nHuman: Is {company} a good investment choice right now? \n\nAssistant:"
    return zero_shot_agent(query)

def print_formatted_content(json_data):
    # Print the 'input'
    print(f"Input: {input}")

    # Process each intermediate step
    for i, (agent_action, output) in enumerate(json_data['intermediate_steps'], start=1):
        # Print the details of each step
        print(f"Step{i}.tool: {agent_action.tool}")
        print(f"Step{i}.log: ")  # Print the log label
        print(agent_action.log)  # Log content is printed, interpreting '\n' as newlines
        print(f"Step{i}.output: {output}")

    # Print the final answer
    print(f"Final Answer: {json_data['output']}")

def format_content(company, json_data):
    formatted_content = ""

    # Add the 'input'
    formatted_content += f"Is {company} a good investment choice right now?\n\n"
    formatted_content += ""

    # Append the final answer
    formatted_content += f"{json_data['output']}\n"

    return formatted_content


def run_tests():
    response = zero_shot_agent("\n\nHuman: Is Tesla a good investment choice right now? \n\nAssistant:")
    print("Repsonse is ")
    print("  ")
    print(response['output'])
    print("Intermediary steps: ")
    print("  ")
    #print(response['intermediate_steps'])
    print_formatted_content(response)

#run_tests()
def format_content_for_streamlit(json_data):
    formatted_content = []

    # Add the 'input'
    formatted_content += f"Input: {json_data['input']}\n"

    # Process each intermediate step
    for i, (agent_action, output) in enumerate(json_data['intermediate_steps'], start=1):
        # Add the details of each step
        formatted_content.append(f"Step{i}.tool: {agent_action.tool}")
        formatted_content.append(f"Step{i}.log:\n{agent_action.log}")
        formatted_content.append(f"Step{i}.output: {output}")

    # Add the final answer
    formatted_content.append(f"Final Answer: {json_data['output']}")

    # Join all parts with newlines
    return '\n\n'.join(formatted_content)