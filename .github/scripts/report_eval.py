import json
import operator
import os
from langsmith import Client
from collections import defaultdict

# Operator map for threshold comparisons
OP_MAP = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
}

def parse_threshold(threshold_str):
    """Parse a condition string like '>=0.75' into (operator, float value)."""
    for symbol in sorted(OP_MAP.keys(), key=len, reverse=True):
        if threshold_str.startswith(symbol):
            return OP_MAP[symbol], float(threshold_str[len(symbol):])
    raise ValueError(f"Invalid threshold format: {threshold_str}")

def format_percentage(value):
    return f"{value * 100:.1f}%" if isinstance(value, float) else "N/A"

# Step 1: Load evaluation config
with open("evaluation_config.json", "r") as f:
    config = json.load(f)

experiment_name = config["experiment_name"]
criteria = config.get("criteria", {})

client = Client()

# Step 2: Get all runs in experiment
runs = list(client.list_runs(project_name=experiment_name))
run_ids = [r.id for r in runs]

# Step 3: Fetch feedback
feedbacks = client.list_feedback(run_ids=run_ids)

# Step 4: Group feedback by key
feedback_by_key = defaultdict(list)
for fb in feedbacks:
    if fb.score is not None:
        feedback_by_key[fb.key].append(fb.score)

# Step 5: Evaluate and format results
table_rows = []
num_passed = 0
num_failed = 0

for key, scores in feedback_by_key.items():
    avg_score = sum(scores) / len(scores) if scores else None
    threshold_expr = criteria.get(key)
    passed = "N/A"
    check = ""

    if threshold_expr:
        op, value = parse_threshold(threshold_expr)
        result = op(avg_score, value)
        passed = "✅" if result else "❌"
        check = threshold_expr
        if result:
            num_passed += 1
        else:
            num_failed += 1

    display_score = f"{avg_score:.2f}" if avg_score is not None else "N/A"
    table_rows.append((key, display_score, check or "–", passed))

# Step 6: Write Markdown output
with open("eval_comment.md", "w") as f:
    f.write(f"### 🧪 LangSmith Evaluation Results for `{experiment_name}`\n\n")
    f.write("| Feedback Key | Avg Score | Criterion | Pass? |\n")
    f.write("|--------------|-----------|-----------|--------|\n")
    for row in table_rows:
        f.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
    
    f.write("\n")
    total = num_passed + num_failed
    summary_line = f"**✅ {num_passed} Passed, ❌ {num_failed} Failed**" if total else "No thresholds defined."
    f.write(summary_line + "\n")

print("✅ Evaluation summary written to eval_comment.md")
