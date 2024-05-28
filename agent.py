import streamlit as st

import openai
import getpass
import sqlite3
import os

from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.utilities import SQLDatabase
from langchain_openai import OpenAI
from langchain.agents import create_sql_agent
import os
from dotenv import load_dotenv
load_dotenv()


# File path
database_file_path = './sql_lite_database1.db'
api_key = st.secrets["OPENAI_API_KEY"]

# Check if database file exists and delete if it does
if os.path.exists(database_file_path):
    os.remove(database_file_path)
    message = "File 'sql_lite_database1.db' found and deleted."
else:
    message = "File 'sql_lite_database1.db' does not exist."

# Step 1: Connect to the database or create it if it doesn't exist
conn = sqlite3.connect(database_file_path)

# Step 2: Create a cursor
cursor = conn.cursor()

# Step 3: Create tables
create_table_query1 = """
                        create table Sailors(sid int PRIMARY KEY,
                         sname varchar(20),
                          rating int,
                           age float,
                            check(rating>=1 and rating<=10)
                        );
                        """

create_table_query2 = """
                        create table Boats(bid int PRIMARY KEY,
                         bname varchar(20),
                          color varchar(20)
                          );
                        """

create_table_query3 = """
                        create table Reserves(sid int,
                         bid int,
                          day date,
                           PRIMARY KEY(sid,bid,day),
                            FOREIGN KEY(sid) REFERENCES Sailors(sid),
                             FOREIGN KEY(bid) REFERENCES Boats(bid)
                             ); 
                        """

queries = [create_table_query1, create_table_query2, create_table_query3]
# queries = [create_table_query1, create_table_query2]

for query in queries:
    # execute queries
    cursor.execute(query)

# Step 4: Insert data into tables Agents, Orders and Customers
insert_query = """
insert into Sailors values (22, 'Dustin', 7, 45.0); 
insert into Sailors values (29, 'Brutus', 1, 33.0); 
insert into Sailors values (31, 'Lubber', 8, 55.0); 
insert into Sailors values (32, 'Andy', 8, 25.0); 
insert into Sailors values (58, 'Rusty', 10, 35.0); 
insert into Sailors values (64, 'Horatio', 7, 35.0); 
insert into Sailors values (71, 'Zorba', 10, 16.0); 
insert into Sailors values (74, 'Horatio', 9, 35.0); 
insert into Sailors values (85, 'Art', 3, 25.5); 
insert into Sailors values (95, 'Bob', 3, 63.5); 

insert into Boats values (101, 'Interlake', 'blue'); 
insert into Boats values (102, 'Interlake', 'red'); 
insert into Boats values (103, 'Clipper', 'green'); 
insert into Boats values (104, 'Marine', 'red'); 

insert into Reserves values (22, 101, '10-OCT-98'); 
insert into Reserves values (22, 102, '10-OCT-98');
insert into Reserves values (22, 103, '10-AUG-98'); 
insert into Reserves values (22, 104, '10-JUL-98'); 
insert into Reserves values (31, 102, '11-OCT-98'); 
insert into Reserves values (31, 103, '11-JUN-98'); 
insert into Reserves values (31, 104, '11-DEC-98'); 
insert into Reserves values (64, 101, '9-MAY-98'); 
insert into Reserves values (64, 102, '9-AUG-98'); 
insert into Reserves values (74, 103, '9-AUG-98'); 
"""

for row in insert_query.splitlines():
    try:
        cursor.execute(row)
    except:
        print(f"An error occurred")
        print(row)

# Step 5: Fetch data from tables
list_of_queries = []
list_of_queries.append("SELECT * FROM Sailors")
list_of_queries.append("SELECT * FROM Boats")
list_of_queries.append("SELECT * FROM Reserves")

# execute queries
for query in list_of_queries:
    cursor.execute(query)
    data = cursor.fetchall()

    print(f"--- Data from tables ({query}) ---")
    for row in data:
        print(row)

# Step 7: Close the cursor and connection
cursor.close()
conn.commit()
conn.close()

os.environ['OPENAI_API_KEY'] = api_key

## include the db

db = SQLDatabase.from_uri('sqlite:///sql_lite_database1.db')




llm = OpenAI(
            temperature=0,
            verbose=True,
            openai_api_key= api_key,
            )

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

st.title("SQL Agent")



user_input = st.text_input("Enter your query")

# Show the input text back to the user


question = user_input
ans = agent_executor.invoke(question)
st.write("The answer to your query is: ", ans)