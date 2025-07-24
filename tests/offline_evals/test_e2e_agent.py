import json

import pytest
from langchain_core.messages import HumanMessage
from langsmith import Client
from openevals.llm import create_llm_as_judge

from agents.simple_text2sql import agent

# Setup LangSmith client
client = Client()

# Define evaluators using OpenEvals
CORRECTNESS_PROMPT = """
You are an expert professor specialized in grading text2sql agent responses.

You are grading the following question:
{inputs}

Here is the expected answer:
{reference_outputs}

You are grading the following predicted answer:
{outputs}

Respond with CORRECT or INCORRECT.
CORRECT means the response is accurate and matches the expected answer.
INCORRECT means the response is wrong or doesn't match the expected answer.

Grade:
"""

RESPONSE_QUALITY_PROMPT = """
Rate the quality of this text2sql agent response on a scale of 1-5:

Question: {inputs}
Expected Response: {reference_outputs}
Actual Response: {outputs}

Rate the response quality (1-5):
1. Completely incorrect or irrelevant
2. Partially correct but missing key information
3. Mostly correct with minor issues
4. Correct and helpful
5. Excellent, comprehensive and accurate

Rating:
"""

correctness_evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    feedback_key="correctness",
    model="openai:gpt-4o-mini",
)

response_quality_evaluator = create_llm_as_judge(
    prompt=RESPONSE_QUALITY_PROMPT,
    feedback_key="response_quality",
    model="openai:gpt-4o-mini",
)


def ls_target(inputs: dict) -> dict:
    """LangSmith target function that runs the text2sql agent"""
    try:
        result = agent.invoke({"messages": [HumanMessage(content=inputs["question"])]})
        if result and "messages" in result and len(result["messages"]) > 0:
            response = result["messages"][-1].content
            if response is None or response == "":
                return {"response": "No response generated"}
            return {"response": response}
        else:
            return {"response": "No response generated"}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}


@pytest.mark.evaluator
def test_e2e_evaluation():
    """Run end-to-end evaluation using LangSmith"""

    # Create dataset if it doesn't exist
    dataset_name = "text2sql-agent"

    # Run evaluation
    experiment_results = client.evaluate(
        ls_target,  # Your AI system
        data=dataset_name,  # The data to predict and grade over
        evaluators=[
            correctness_evaluator,
            response_quality_evaluator,
        ],  # The evaluators to score the results
        max_concurrency=10,
        experiment_prefix="text2sql-agent-e2e",  # A prefix for your experiment names
    )

    assert experiment_results is not None
    print(f"✅ Evaluation completed: {experiment_results.experiment_name}")

    # Define scoring rules for post-processing
    criteria = {"correctness": ">=0.8", "response_quality": ">=3.5"}

    output_metadata = {
        "experiment_name": experiment_results.experiment_name,
        "criteria": criteria,
    }

    safe_name = experiment_results.experiment_name.replace(":", "-").replace("/", "-")
    config_filename = f"evaluation_config__{safe_name}.json"
    with open(config_filename, "w") as f:
        json.dump(output_metadata, f)

    print(f"::set-output name=config_filename::{config_filename}")
