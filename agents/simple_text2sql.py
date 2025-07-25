from dotenv import load_dotenv
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, List, TypedDict

from agents.prompts import QA_SYSTEM_PROMPT, SQL_SYSTEM_PROMPT
from agents.utils import get_detailed_table_info, get_engine_for_chinook_db

load_dotenv(override=True)


class OverallState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    schema: str
    sql: str
    records: List[dict]


class InputState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class OutputState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def generate_sql(llm):
    def _generate(state: OverallState) -> dict:
        last_message = state["messages"][-1]
        prompt = f"""Generate a SQL query for the following question:
        Question: {last_message.content}
        Schema: {get_detailed_table_info()}
        SQL:
        """
        sql_query = llm.invoke(
            [SystemMessage(SQL_SYSTEM_PROMPT)]
            + state["messages"]
            + [HumanMessage(prompt)]
        )
        sql_query = sql_query.content.replace("```sql", "").replace("```", "")
        return {"sql": sql_query}

    return _generate


def execute_sql(db):
    def _execute(state: OverallState) -> dict:
        records = db.run(state["sql"])
        return {"records": records}

    return _execute


def generate_answer(llm):
    def _answer(state: OverallState) -> dict:
        last_message = state["messages"][-1]
        prompt = f"Given the question: {last_message.content} and the database results: {state['records']}, provide a concise answer."
        answer = llm.invoke(
            [SystemMessage(QA_SYSTEM_PROMPT)]
            + state["messages"]
            + [HumanMessage(prompt)]
        )
        return {"messages": [answer]}

    return _answer


def create_agent(llm, db):
    builder = StateGraph(
        OverallState, input_schema=InputState, output_schema=OutputState
    )
    builder.add_node("generate_sql", generate_sql(llm))
    builder.add_node("execute_sql", execute_sql(db))
    builder.add_node("generate_answer", generate_answer(llm))
    builder.add_edge(START, "generate_sql")
    builder.add_edge("generate_sql", "execute_sql")
    builder.add_edge("execute_sql", "generate_answer")
    builder.add_edge("generate_answer", END)
    return builder.compile()


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
db = SQLDatabase(get_engine_for_chinook_db())
agent = create_agent(llm, db)
