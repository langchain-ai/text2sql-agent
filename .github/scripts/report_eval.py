import json
import operator
import os
import sys
import glob
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
    for symbol in sorted(OP_MAP.keys(), key=len, reverse=True):
        if threshold_str.startswith(symbol):
            return OP_MAP[symbol], float(threshold_str[len(symbol):])
    raise ValueError(f"Invalid threshold format: {threshold_str}")

def format_score(value):
    return f"{value:.2f}" if value is not None else "N/A"

def process_config(config_path, client):
    with open(config_path, "r") as f:
        config = json.load(f)

    experiment_name = config["experiment_name"]
    criteria = config.get("criteria", {})

    runs = list(client.list_runs(project_name=experiment_name))
    run_ids = [r.id for r in runs]
    feedbacks = client.list_feedback(run_ids=run_ids)

    feedback_by_key = defaultdict(list)
    for fb in feedbacks:
        if fb.score is not None:
            feedback_by_key[fb.key].append(fb.score)

    table_rows = []
    num_passed = 0
    num_failed = 0

    for key, scores in feedback_by_key.items():
        avg_score = sum(scores) / len(scores) if scores else None
        threshold_expr = criteria.get(key)
        passed = "N/A"
        check = "–"

        if threshold_expr:
            op, value = parse_threshold(threshold_expr)
            result = op(avg_score, value)
            passed = "✅" if result else "❌"
            check = threshold_expr
            if result:
                num_passed += 1
            else:
                num_failed += 1

        display_score = format_score(avg_score)
        table_rows.append((key, display_score, check, passed))

    # Write to markdown
    with open("eval_comment.md", "a") as f:
        f.write(f"\n\n### 🧪 LangSmith Evaluation Results for `{experiment_name}`\n\n")
        f.write("| Feedback Key | Avg Score | Criterion | Pass? |\n")
        f.write("|--------------|-----------|-----------|--------|\n")
        for row in table_rows:
            f.write(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n")
        
        total = num_passed + num_failed
        summary = f"**✅ {num_passed} Passed, ❌ {num_failed} Failed**" if total else "No thresholds defined."
        f.write(f"\n{summary}\n")

    print(f"✅ Processed {config_path}")

# ---- Entry point ----

client = Client()

# Accept config paths via CLI or glob all matching files
config_files = sys.argv[1:] if len(sys.argv) > 1 else glob.glob("evaluation_config__*.json")

if not config_files:
    print("❌ No evaluation config files found.")
    sys.exit(1)

# Remove old comment if re-running
if os.path.exists("eval_comment.md"):
    os.remove("eval_comment.md")

for config_path in config_files:
    process_config(config_path, client)

print("✅ All evaluations processed. PR comment is ready in eval_comment.md")
