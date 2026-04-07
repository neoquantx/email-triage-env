try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv is required. Install dependencies with 'uv sync'"
    ) from e

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from models import EmailTriageAction, EmailTriageObservation
    from server.email_triage_env_environment import EmailTriageEnvironment, TASKS, EMAIL_DATASET
except ModuleNotFoundError:
    from email_triage_env.models import EmailTriageAction, EmailTriageObservation
    from email_triage_env.server.email_triage_env_environment import EmailTriageEnvironment, TASKS, EMAIL_DATASET

import random
from fastapi.responses import JSONResponse

app = create_app(
    EmailTriageEnvironment,
    EmailTriageAction,
    EmailTriageObservation,
    env_name="email_triage_env",
    max_concurrent_envs=10,
)


@app.get("/tasks")
def get_tasks():
    """Returns list of tasks and the action schema."""
    return JSONResponse({
        "tasks": TASKS,
        "action_schema": {
            "priority": "string: 'urgent', 'normal', or 'low'",
            "category": "string: 'work', 'spam', 'personal', 'newsletter'",
            "should_reply": "boolean: whether the email needs a reply"
        }
    })


@app.get("/grader")
def get_grader():
    """Returns grader info and scoring criteria."""
    return JSONResponse({
        "grader": {
            "description": "Scores agent performance on email triage",
            "scoring": {
                "priority_correct": 0.4,
                "category_correct": 0.4,
                "reply_correct": 0.2,
            },
            "score_range": "0.0 to 1.0",
            "tasks": [t["task_id"] for t in TASKS]
        }
    })


@app.get("/baseline")
def get_baseline():
    """Runs a simple baseline agent and returns scores for all 3 tasks."""
    results = {}
    for task in TASKS:
        task_id = task["task_id"]
        num_emails = task["num_emails"]
        emails = random.sample(EMAIL_DATASET, min(num_emails, len(EMAIL_DATASET)))
        scores = []
        for email in emails:
            action = EmailTriageAction(
                priority=random.choice(["urgent", "normal", "low"]),
                category=random.choice(["work", "spam", "personal", "newsletter"]),
                should_reply=random.choice([True, False])
            )
            score = 0.0
            if action.priority == email["correct_priority"]:
                score += 0.4
            if action.category == email["correct_category"]:
                score += 0.4
            if action.should_reply == email["correct_reply"]:
                score += 0.2
            scores.append(score)
        results[task_id] = round(sum(scores) / len(scores), 4)
    return JSONResponse({"baseline_scores": results})


def main(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    main(port=args.port)