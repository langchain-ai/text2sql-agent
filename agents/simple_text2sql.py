
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END
from agents.utils import get_engine_for_chinook_db, get_detailed_table_info
from langchain_community.utilities.sql_database import SQLDatabase

from dotenv import load_dotenv

load_dotenv(override=True)

engine = get_engine_for_chinook_db()
db = SQLDatabase(engine)

class OverallState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    schema: str
    sql: str
    records: List[dict]
    answer: str

class InputState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

class OutputState(TypedDict):
    answer: str
    sql: str

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

qa_system_prompt = """
You are an assistant that helps to form nice and human understandable answers.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
Here is an example:

Question: How many songs do you have by James Brown?
Context:[20]
Helpful Answer: We have 20 songs by James Brown.

Follow this example when generating answers.
If the provided information is empty, say that you don't know the answer.
You will have the full message history to help you answer the question, if you need more information, ask the user for it.
"""

sql_system_prompt = """
Task: Generate SQL statement to query a database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a SQL statement.
Do not include any text except the generated SQL statement.
You will have the full message history to help you answer the question, if you dont need to generate a sql query, just generate a sql query that will return an empty result.
"""

def generate_sql(state: OverallState) -> dict:

    last_message = state["messages"][-1]

    prompt = """Generate a SQL query for the following question:
    Question: {question}
    Schema: {schema}
    SQL:
    """.format(question=last_message.content, schema=str(get_detailed_table_info()))

    sql_query = llm.invoke([SystemMessage(sql_system_prompt)] + state["messages"] + [HumanMessage(prompt)])
    # strip the sql query of triple backticks
    try:
        sql_query = sql_query.content.replace("```sql", "").replace("```", "")
    except Exception as e:
        print(f"Error stripping sql query: {e}")
        sql_query = sql_query.content
    return {"sql": sql_query}

def execute_sql(state: OverallState) -> dict:
    records = db.run(state["sql"])
    return {"records": records}

def generate_answer(state: OverallState) -> dict:
    last_message = state["messages"][-1]
    prompt = """Given the question: {question} and the database results: {records}, provide a concise answer.
    """.format(question=last_message.content, records=state["records"])

    answer = llm.invoke([SystemMessage(qa_system_prompt)] + state["messages"] + [HumanMessage(prompt)])
    return {"answer": answer.content}


graph_builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)

graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("execute_sql", execute_sql)
graph_builder.add_node("generate_answer", generate_answer)

graph_builder.add_edge(START, "generate_sql")
graph_builder.add_edge("generate_sql", "execute_sql")
graph_builder.add_edge("execute_sql", "generate_answer")
graph_builder.add_edge("generate_answer", END)

agent = graph_builder.compile()
