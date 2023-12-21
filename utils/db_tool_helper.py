from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from utils.llm_wrapper import get_llm

from pathlib import Path

# This is because we are in the utils folder, a sibling of the db folder
db_file_path = Path(__file__).resolve().parent.parent / 'db' / 'stock_ticker_database.db'
db = SQLDatabase.from_uri(f"sqlite:///{db_file_path}")

from langchain.prompts.prompt import PromptTemplate

_DEFAULT_TEMPLATE = """Human: Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
<format>
Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Result of SQLResult only"
</format>
Assistant: Understood, I will use the above format and only provide the answer.

Only use the following tables:
<tables>
CREATE TABLE stock_ticker (
	symbol text PRIMARY KEY,
	name text NOT NULL,
	currency text,
	stockExchange text, 
    exchangeShortName text
)
</tables>

If someone asks for the table stock ticker table, they really mean the stock_ticker table.
<examples>
Question: 
        What is the ticker symbol for Amazon in stock ticker table?
        Params: 
        Company name (name): Amazon
        
SQLQuery:SELECT symbol FROM stock_ticker WHERE name LIKE '%Amazon%'

</examples>

Question: {input}

"""

PROMPT = PromptTemplate(
    input_variables=["input", "dialect"], template=_DEFAULT_TEMPLATE
)


#response = db_chain("\n\nHuman: What is the ticker symbol for Tesla in stock ticker table? \n\nAssistant:")
#print(response)

def get_db_chain():
    llm = get_llm()

    db_chain = SQLDatabaseChain.from_llm(
        llm, 
        db, 
        verbose=True, 
        return_intermediate_steps=True, 
        prompt=PROMPT, 
        )

    return db_chain