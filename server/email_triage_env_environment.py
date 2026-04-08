from uuid import uuid4
import os
import random

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from ..models import EmailTriageAction, EmailTriageObservation
except ImportError:
    from models import EmailTriageAction, EmailTriageObservation


# Dataset of emails with correct labels
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
        "body": "Your invoice #789 is 30 days overdue. Please make payment immediately to avoid service interruption.",
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
    {
        "subject": "Re: Project deadline extension request",
        "sender": "client@bigcorp.com",
        "body": "We need to discuss the project timeline. The current deadline is not feasible given the scope changes. Can we schedule a call today?",
        "correct_priority": "urgent",
        "correct_category": "work",
        "correct_reply": True,
    },
    {
        "subject": "You have been pre-approved for a loan!",
        "sender": "loans@quickcash-offers.net",
        "body": "Dear customer, you have been pre-approved for a $50,000 loan. No credit check needed. Apply now!",
        "correct_priority": "low",
        "correct_category": "spam",
        "correct_reply": False,
    },
    {
        "subject": "Doctor appointment reminder",
        "sender": "noreply@cityhealth.com",
        "body": "This is a reminder that you have an appointment scheduled for tomorrow at 2:00 PM with Dr. Smith.",
        "correct_priority": "normal",
        "correct_category": "personal",
        "correct_reply": False,
    },
    {
        "subject": "URGENT: Legal notice - response required within 24 hours",
        "sender": "legal@lawfirm.com",
        "body": "Our client has filed a complaint against your company. You are required to respond within 24 hours to avoid further legal action.",
        "correct_priority": "urgent",
        "correct_category": "work",
        "correct_reply": True,
    },
    {
        "subject": "Weekly digest - top stories",
        "sender": "digest@medium.com",
        "body": "Your weekly reading list is ready. Top stories in technology, science and business curated just for you.",
        "correct_priority": "low",
        "correct_category": "newsletter",
        "correct_reply": False,
    },
]

# Task definitions
TASKS = [
    {
        "task_id": "easy_triage",
        "name": "Easy Email Triage",
        "description": "Triage 3 emails with obvious priority and category",
        "num_emails": 3,
        "difficulty": "easy",
        "grader": {
            "type": "rule_based",
            "metrics": ["priority_correct", "category_correct", "reply_correct"],
            "weights": {
                "priority_correct": 0.4,
                "category_correct": 0.4,
                "reply_correct": 0.2,
            },
        },
    },
    {
        "task_id": "medium_triage",
        "name": "Medium Email Triage",
        "description": "Triage 7 emails with mixed types including spam detection",
        "num_emails": 7,
        "difficulty": "medium",
        "grader": {
            "type": "rule_based",
            "metrics": ["priority_correct", "category_correct", "reply_correct"],
            "weights": {
                "priority_correct": 0.4,
                "category_correct": 0.4,
                "reply_correct": 0.2,
            },
        },
    },
    {
        "task_id": "hard_triage",
        "name": "Hard Email Triage",
        "description": "Triage all 15 emails accurately across all categories",
        "num_emails": 15,
        "difficulty": "hard",
        "grader": {
            "type": "rule_based",
            "metrics": ["priority_correct", "category_correct", "reply_correct"],
            "weights": {
                "priority_correct": 0.4,
                "category_correct": 0.4,
                "reply_correct": 0.2,
            },
        },
    },
]


class EmailTriageEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._emails = []
        self._current_index = 0
        self._scores = []
        self._task_id = os.getenv("TASK_ID", "medium_triage")

    def reset(self) -> EmailTriageObservation:
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._scores = []
        self._current_index = 0

        # Pick task
        task = next((t for t in TASKS if t["task_id"] == self._task_id), TASKS[1])
        num_emails = task["num_emails"]

        # Sample emails
        self._emails = random.sample(EMAIL_DATASET, min(num_emails, len(EMAIL_DATASET)))

        email = self._emails[0]
        return EmailTriageObservation(
            email_id=0,
            subject=email["subject"],
            sender=email["sender"],
            body=email["body"],
            emails_remaining=len(self._emails) - 1,
            last_reward=0.0,
            done=False,
            reward=0.0,
        )

    def step(self, action: EmailTriageAction) -> EmailTriageObservation:
        self._state.step_count += 1

        email = self._emails[self._current_index]

        # Score the action
        score = 0.0
        if action.priority == email["correct_priority"]:
            score += 0.4
        if action.category == email["correct_category"]:
            score += 0.4
        if action.should_reply == email["correct_reply"]:
            score += 0.2

        self._scores.append(score)
        self._current_index += 1

        done = self._current_index >= len(self._emails)

        if done:
            return EmailTriageObservation(
                email_id=self._current_index,
                subject="",
                sender="",
                body="Episode complete.",
                emails_remaining=0,
                last_reward=score,
                done=True,
                reward=sum(self._scores) / len(self._scores),
            )

        next_email = self._emails[self._current_index]
        return EmailTriageObservation(
            email_id=self._current_index,
            subject=next_email["subject"],
            sender=next_email["sender"],
            body=next_email["body"],
            emails_remaining=len(self._emails) - self._current_index - 1,
            last_reward=score,
            done=False,
            reward=score,
        )

    @property
    def state(self) -> State:
        return self._state