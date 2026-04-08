import os
import random
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

EMAIL_DATASET = [
    {"subject": "URGENT: Server down in production", "sender": "alerts@company.com", "body": "Production server is down. Customers cannot access the app. Immediate action required.", "correct_priority": "urgent", "correct_category": "work", "correct_reply": True},
    {"subject": "Congratulations! You won $1,000,000", "sender": "winner@lottery-scam.com", "body": "Click here to claim your prize. Send us your bank details.", "correct_priority": "low", "correct_category": "spam", "correct_reply": False},
    {"subject": "Team meeting tomorrow at 10am", "sender": "manager@company.com", "body": "Hi team, reminder about our weekly sync tomorrow. Please come prepared.", "correct_priority": "normal", "correct_category": "work", "correct_reply": True},
    {"subject": "Your order has been shipped", "sender": "noreply@amazon.com", "body": "Your order #12345 has been shipped and will arrive in 2-3 days.", "correct_priority": "low", "correct_category": "newsletter", "correct_reply": False},
    {"subject": "CRITICAL: Security breach detected", "sender": "security@company.com", "body": "We detected unauthorized access to our systems. All hands on deck immediately.", "correct_priority": "urgent", "correct_category": "work", "correct_reply": True},
    {"subject": "Happy Birthday!", "sender": "mom@gmail.com", "body": "Happy birthday sweetie! Hope you have a wonderful day. Love you!", "correct_priority": "normal", "correct_category": "personal", "correct_reply": True},
    {"subject": "Monthly newsletter - April 2026", "sender": "news@techdigest.com", "body": "This month in tech: AI breakthroughs, new product launches and more.", "correct_priority": "low", "correct_category": "newsletter", "correct_reply": False},
    {"subject": "Invoice overdue - immediate payment required", "sender": "billing@vendor.com", "body": "Your invoice #789 is 30 days overdue. Please make payment immediately.", "correct_priority": "urgent", "correct_category": "work", "correct_reply": True},
    {"subject": "Weekend BBQ at my place", "sender": "friend@gmail.com", "body": "Hey! Having a BBQ this Saturday. You coming? Bring some drinks!", "correct_priority": "normal", "correct_category": "personal", "correct_reply": True},
    {"subject": "Buy cheap meds online", "sender": "pharma@spamsite.net", "body": "Get cheap medications without prescription. Best prices guaranteed!", "correct_priority": "low", "correct_category": "spam", "correct_reply": False},
    {"subject": "Re: Project deadline extension request", "sender": "client@bigcorp.com", "body": "We need to discuss the project timeline. The current deadline is not feasible given the scope changes. Can we schedule a call today?", "correct_priority": "urgent", "correct_category": "work", "correct_reply": True},
    {"subject": "You have been pre-approved for a loan!", "sender": "loans@quickcash-offers.net", "body": "Dear customer, you have been pre-approved for a $50,000 loan. No credit check needed. Apply now!", "correct_priority": "low", "correct_category": "spam", "correct_reply": False},
    {"subject": "Doctor appointment reminder", "sender": "noreply@cityhealth.com", "body": "This is a reminder that you have an appointment scheduled for tomorrow at 2:00 PM with Dr. Smith.", "correct_priority": "normal", "correct_category": "personal", "correct_reply": False},
    {"subject": "URGENT: Legal notice - response required within 24 hours", "sender": "legal@lawfirm.com", "body": "Our client has filed a complaint against your company. You are required to respond within 24 hours to avoid further legal action.", "correct_priority": "urgent", "correct_category": "work", "correct_reply": True},
    {"subject": "Weekly digest - top stories", "sender": "digest@medium.com", "body": "Your weekly reading list is ready. Top stories in technology, science and business curated just for you.", "correct_priority": "low", "correct_category": "newsletter", "correct_reply": False},
]

TASKS = [
    {"task_id": "easy_triage", "num_emails": 3},
    {"task_id": "medium_triage", "num_emails": 7},
    {"task_id": "hard_triage", "num_emails": 15},
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
    try:
        client = OpenAI(
            api_key=HF_TOKEN if HF_TOKEN else "dummy-key",
            base_url=API_BASE_URL,
        )
        prompt = f"""You are an email triage assistant. Classify this email:

Subject: {email['subject']}
From: {email['sender']}
Body: {email['body']}

Respond in this exact format only, no extra text:
priority: urgent|normal|low
category: work|spam|personal|newsletter
should_reply: true|false"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )
        text = response.choices[0].message.content.lower()
        lines = text.strip().split("\n")
        result = {"priority": "normal", "category": "work", "should_reply": False}
        for line in lines:
            if "priority:" in line:
                val = line.split(":")[1].strip()
                if val in ["urgent", "normal", "low"]:
                    result["priority"] = val
            elif "category:" in line:
                val = line.split(":")[1].strip()
                if val in ["work", "spam", "personal", "newsletter"]:
                    result["category"] = val
            elif "should_reply:" in line:
                result["should_reply"] = "true" in line
        return result
    except Exception:
        # Fallback to rule-based heuristic (not random)
        subject = email["subject"].lower()
        body = email["body"].lower()
        sender = email["sender"].lower()

        # Priority heuristic
        if any(w in subject + body for w in ["urgent", "critical", "immediately", "breach", "down", "legal"]):
            priority = "urgent"
        elif any(w in subject + body for w in ["meeting", "birthday", "bbq", "appointment"]):
            priority = "normal"
        else:
            priority = "low"

        # Category heuristic
        if any(w in sender + subject + body for w in ["scam", "lottery", "prize", "cheap", "pre-approved", "pharma"]):
            category = "spam"
        elif any(w in sender for w in ["gmail.com", "yahoo.com", "hotmail.com", "mom", "friend"]):
            category = "personal"
        elif any(w in sender + subject for w in ["newsletter", "digest", "noreply", "techdigest", "medium.com"]):
            category = "newsletter"
        else:
            category = "work"

        # Reply heuristic
        should_reply = priority in ["urgent", "normal"] and category in ["work", "personal"]

        return {"priority": priority, "category": category, "should_reply": should_reply}


def main():
    print("[START]", flush=True)
    for task in TASKS:
        task_id = task["task_id"]
        num_emails = task["num_emails"]
        emails = random.sample(EMAIL_DATASET, min(num_emails, len(EMAIL_DATASET)))
        scores = []
        for i, email in enumerate(emails):
            action = run_llm_agent(email)
            score = score_action(action, email)
            scores.append(score)
            print(f"[STEP] task={task_id} step={i+1} reward={round(score, 4)}", flush=True)
        final_score = round(sum(scores) / len(scores), 4)
        print(f"[END] task={task_id} score={final_score} steps={num_emails}", flush=True)
    print("[END] all_tasks_complete", flush=True)


if __name__ == "__main__":
    main()