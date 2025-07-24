from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agents.simple_text2sql import execute_sql, generate_answer, generate_sql


@pytest.mark.single_node
def test_generate_sql_node():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="SELECT * FROM artists")
    node = generate_sql(mock_llm)
    state = {
        "messages": [HumanMessage(content="List all artists")],
        "schema": "",
        "sql": "",
        "records": [],
    }
    result = node(state)
    assert "SELECT *" in result["sql"]


@pytest.mark.single_node
def test_execute_sql_node():
    mock_db = MagicMock()
    mock_db.run.return_value = [{"Artist": "Test"}]
    node = execute_sql(mock_db)
    state = {
        "sql": "SELECT * FROM artists",
        "messages": [],
        "schema": "",
        "records": [],
    }
    result = node(state)
    assert result["records"] == [{"Artist": "Test"}]


@pytest.mark.single_node
def test_generate_answer_node():
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="We have 20 songs by James Brown.")
    node = generate_answer(mock_llm)
    state = {
        "messages": [HumanMessage(content="How many songs by James Brown?")],
        "records": [{"Artist": "James Brown", "Songs": 20}],
        "sql": "",
        "schema": "",
    }
    result = node(state)
    assert "James Brown" in result["messages"][0].content
