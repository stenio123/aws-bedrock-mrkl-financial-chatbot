## database

import sqlite3

stock_ticker_data = [
    {
        "symbol": "AMZN",
        "name": "Amazon.com, Inc.",
        "currency": "USD",
        "stockExchange": "NasdaqGS",
        "exchangeShortName": "NASDAQ"
    },
    {
        "symbol": "TSLA",
        "name": "Tesla Inc.",
        "currency": "USD",
        "stockExchange": "NasdaqGS",
        "exchangeShortName": "NASDAQ"
    },
    {
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "currency": "USD",
        "stockExchange": "NasdaqGS",
        "exchangeShortName": "NASDAQ"
    },
    {
        "symbol": "META",
        "name": "Meta Platforms, Inc.",
        "currency": "USD",
        "stockExchange": "NasdaqGS",
        "exchangeShortName": "NASDAQ"
    },
    {
        "symbol": "COIN",
        "name": "Coinbase Global, Inc.",
        "currency": "USD",
        "stockExchange": "NasdaqGS",
        "exchangeShortName": "NASDAQ"
    }
]

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except FileExistsError as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except RuntimeError as e:
        print(e)

db_name = "stock_ticker_database.db"
conn = create_connection(db_name)

create_table_sql = """CREATE TABLE IF NOT EXISTS stock_ticker (
	symbol text PRIMARY KEY,
	name text NOT NULL,
	currency text,
	stockExchange text, 
    exchangeShortName text
);"""

# create tables
if conn is not None:
    # create projects table
    create_table(conn, create_table_sql)
else:
    print("Error! cannot create the database connection.")

def insert_data(data):
    for item in data:
        conn.execute("INSERT INTO stock_ticker (symbol, name, currency,stockExchange, exchangeShortName ) VALUES (?, ?, ?, ?,?)", 
                    (item["symbol"], item["name"], item["currency"], item["stockExchange"],item["exchangeShortName"]))
    conn.commit()
    conn.close()

insert_data(stock_ticker_data)