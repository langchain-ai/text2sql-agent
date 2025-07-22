import pytest
from langchain_core.messages import HumanMessage, AIMessage
from agents.simple_text2sql import create_agent
from langchain_openai import ChatOpenAI
from agents.utils import get_engine_for_chinook_db
from langchain_community.utilities.sql_database import SQLDatabase

@pytest.mark.e2e
def test_real_graph_run_with_openai():
    # Instantiate real dependencies
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    engine = get_engine_for_chinook_db()
    db = SQLDatabase(engine)
    
    agent = create_agent(llm, db)

    input_state = {
        "messages": [HumanMessage(content="How many albums do we have by AC/DC?")]
    }

    result = agent.invoke(input_state)
    messages = result["messages"]
    
    assert isinstance(messages[-1], AIMessage)
    print(f"LLM response: {messages[-1].content}")

    assert "AC/DC" in messages[-1].content
    assert any(char.isdigit() for char in messages[-1].content)  # crude check for numeric result
