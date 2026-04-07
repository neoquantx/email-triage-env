from openenv.core.env_server.types import Action, Observation
from pydantic import Field
from typing import List, Optional


class EmailTriageAction(Action):
    """Action taken by the agent to triage an email."""
    
    priority: str = Field(..., description="Priority assigned: 'urgent', 'normal', or 'low'")
    category: str = Field(..., description="Category: 'work', 'spam', 'personal', 'newsletter'")
    should_reply: bool = Field(..., description="Whether the email needs a reply")


class EmailTriageObservation(Observation):
    """Observation of the current email to triage."""
    
    email_id: int = Field(default=0, description="ID of the current email")
    subject: str = Field(default="", description="Email subject line")
    sender: str = Field(default="", description="Email sender")
    body: str = Field(default="", description="Email body text")
    emails_remaining: int = Field(default=0, description="Number of emails left to triage")
    last_reward: float = Field(default=0.0, description="Reward from last action")
    done: bool = Field(default=False, description="Whether episode is complete")