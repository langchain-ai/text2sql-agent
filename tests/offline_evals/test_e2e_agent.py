import pytest
from langsmith import Client
from openevals.llm import create_llm_as_judge
from agents.simple_text2sql import agent
from langchain_core.messages import HumanMessage

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
        evaluators=[correctness_evaluator, response_quality_evaluator],  # The evaluators to score the results
        max_concurrency=10,
        experiment_prefix="text2sql-agent-e2e",  # A prefix for your experiment names
    )
    
    assert experiment_results is not None
    print(f"Evaluation completed. Results: {experiment_results}")
    
    # Fetch feedback scores and assert minimum thresholds
    feedback = client.list_feedback(
        run_ids=[r.id for r in client.list_runs(project_name=experiment_results.experiment_name)],
    )
    
    # Test correctness scores (boolean - should be at least 80% correct)
    correctness_feedback = [f for f in feedback if f.key == 'correctness']
    correctness_scores = [f.score for f in correctness_feedback if f.score is not None]
    if correctness_scores:
        correctness_percentage = sum(correctness_scores) / len(correctness_scores)
        print(f"Correctness Score: {correctness_percentage:.2%} ({sum(correctness_scores)}/{len(correctness_scores)})")
        assert correctness_percentage >= 0.8, f"Correctness score {correctness_percentage:.2%} is below 80% threshold"
    
    # Test response quality scores (1-5 scale - should be at least 3.5 average)
    quality_feedback = [f for f in feedback if f.key == 'response_quality']
    quality_scores = [f.score for f in quality_feedback if f.score is not None]
    if quality_scores:
        quality_average = sum(quality_scores) / len(quality_scores)
        print(f"Response Quality Score: {quality_average:.2f}/5 (min: {min(quality_scores)}, max: {max(quality_scores)})")
        assert quality_average >= 3.5, f"Response quality score {quality_average:.2f} is below 3.5 threshold"
    
    print(f"✅ All evaluation thresholds met! Processed {len(correctness_scores)} correctness and {len(quality_scores)} quality scores.")
    
    # Write evaluation results to file for GitHub Actions parsing
    import json
    import os
    
    eval_results = {
        "e2e_correctness": correctness_percentage if correctness_scores else 0.0,
        "e2e_quality": quality_average if quality_scores else 0.0,
        "e2e_correctness_passed": correctness_percentage >= 0.8 if correctness_scores else False,
        "e2e_quality_passed": quality_average >= 3.5 if quality_scores else False
    }
    
    # Write to file that GitHub Actions can read
    with open("e2e_evaluation_results.json", "w") as f:
        json.dump(eval_results, f) 