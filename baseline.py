import os
import random
from openai import OpenAI

# Email dataset (same as environment)
EMAIL_DATASET = [
    {
        "subject": "URGENT: Server down in production",
        "sender": "alerts@company.com",
        "body": "Production server is down. Customers cannot access the app. Immediate action required.",
        "correct_priority": "urgent",
        "correct_category": "work",
        "correct_reply": True,
    },
    {
        "subject": "Congratulations! You won $1,000,000",
        "sender": "winner@lottery-scam.com",
        "body": "Click here to claim your prize. Send us your bank details.",
        "correct_priority": "low",
        "correct_category": "spam",
        "correct_reply": False,
    },
    {
        "subject": "Team meeting tomorrow at 10am",
        "sender": "manager@company.com",
        "body": "Hi team, reminder about our weekly sync tomorrow. Please come prepared.",
        "correct_priority": "normal",
        "correct_category": "work",
        "correct_reply": True,
    },
    {
        "subject": "Your order has been shipped",
        "sender": "noreply@amazon.com",
        "body": "Your order #12345 has been shipped and will arrive in 2-3 days.",
        "correct_priority": "low",
        "correct_category": "newsletter",
        "correct_reply": False,
    },
    {
        "subject": "CRITICAL: Security breach detected",
        "sender": "security@company.com",
        "body": "We detected unauthorized access to our systems. All hands on deck immediately.",
        "correct_priority": "urgent",
        "correct_category": "work",
        "correct_reply": True,
    },
    {
        "subject": "Happy Birthday!",
        "sender": "mom@gmail.com",
        "body": "Happy birthday sweetie! Hope you have a wonderful day. Love you!",
        "correct_priority": "normal",
        "correct_category": "personal",
        "correct_reply": True,
    },
    {
        "subject": "Monthly newsletter - April 2026",
        "sender": "news@techdigest.com",
        "body": "This month in tech: AI breakthroughs, new product launches and more.",
        "correct_priority": "low",
        "correct_category": "newsletter",
        "correct_reply": False,
    },
    {
        "subject": "Invoice overdue - immediate payment required",
        "sender": "billing@vendor.com",
        "body": "Your invoice #789 is 30 days overdue. Please make payment immediately.",
        "correct_priority": "urgent",
        "correct_category": "work",
        "correct_reply": True,
    },
    {
        "subject": "Weekend BBQ at my place",
        "sender": "friend@gmail.com",
        "body": "Hey! Having a BBQ this Saturday. You coming? Bring some drinks!",
        "correct_priority": "normal",
        "correct_category": "personal",
        "correct_reply": True,
    },
    {
        "subject": "Buy cheap meds online",
        "sender": "pharma@spamsite.net",
        "body": "Get cheap medications without prescription. Best prices guaranteed!",
        "correct_priority": "low",
        "correct_category": "spam",
        "correct_reply": False,
    },
]

TASKS = [
    {"task_id": "easy_triage", "num_emails": 3},
    {"task_id": "medium_triage", "num_emails": 5},
    {"task_id": "hard_triage", "num_emails": 10},
]


def score_action(action, email):
    score = 0.0
    if action["priority"] == email["correct_priority"]:
        score += 0.4
    if action["category"] == email["correct_category"]:
        score += 0.4
    if action["should_reply"] == email["correct_reply"]:
        score += 0.2
    return score


def run_llm_agent(email):
    """Use OpenAI API to triage an email."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key:
        # Fallback to random if no API key
        return {
            "priority": random.choice(["urgent", "normal", "low"]),
            "category": random.choice(["work", "spam", "personal", "newsletter"]),
            "should_reply": random.choice([True, False])
        }

    client = OpenAI(api_key=api_key)
    prompt = f"""You are an email triage assistant. Classify this email:

Subject: {email['subject']}
From: {email['sender']}
Body: {email['body']}

Respond in this exact format:
priority: urgent|normal|low
category: work|spam|personal|newsletter
should_reply: true|false"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=50,
    )

    text = response.choices[0].message.content.lower()
    lines = text.strip().split("\n")
    result = {}
    for line in lines:
        if "priority:" in line:
            val = line.split(":")[1].strip()
            result["priority"] = val if val in ["urgent", "normal", "low"] else "normal"
        elif "category:" in line:
            val = line.split(":")[1].strip()
            result["category"] = val if val in ["work", "spam", "personal", "newsletter"] else "work"
        elif "should_reply:" in line:
            result["should_reply"] = "true" in line

    return result


def main():
    print("Running baseline inference on all 3 tasks...\n")
    results = {}

    for task in TASKS:
        task_id = task["task_id"]
        num_emails = task["num_emails"]
        emails = random.sample(EMAIL_DATASET, min(num_emails, len(EMAIL_DATASET)))
        scores = []

        for email in emails:
            action = run_llm_agent(email)
            score = score_action(action, email)
            scores.append(score)

        final_score = round(sum(scores) / len(scores), 4)
        results[task_id] = final_score
        print(f"Task: {task_id} → Score: {final_score}")

    print(f"\nFinal baseline scores: {results}")
    return results


if __name__ == "__main__":
    main()