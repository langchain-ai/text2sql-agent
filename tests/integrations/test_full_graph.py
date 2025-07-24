from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from agents.simple_text2sql import create_agent


@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.invoke.side_effect = [
        AIMessage(content="SELECT * FROM artists"),  # SQL generation
        AIMessage(content="We have 20 songs by James Brown."),  # Answer generation
    ]
    return mock


@pytest.fixture
def mock_db():
    mock = MagicMock()
    mock.run.return_value = [{"Artist": "James Brown", "Songs": 20}]
    return mock


@pytest.mark.integration
def test_graph_run(mock_llm, mock_db):
    agent = create_agent(mock_llm, mock_db)
    input_state = {"messages": [HumanMessage(content="How many songs by James Brown?")]}
    result = agent.invoke(input_state)
    assert "James Brown" in result["messages"][-1].content
