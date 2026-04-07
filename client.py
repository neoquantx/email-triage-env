from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import EmailTriageAction, EmailTriageObservation


class EmailTriageEnv(
    EnvClient[EmailTriageAction, EmailTriageObservation, State]
):
    """
    Client for the Email Triage environment.
    Connects via WebSocket to the running server.
    """

    def _step_payload(self, action: EmailTriageAction) -> Dict:
        return {
            "priority": action.priority,
            "category": action.category,
            "should_reply": action.should_reply,
        }

    def _parse_result(self, payload: Dict) -> StepResult[EmailTriageObservation]:
        obs_data = payload.get("observation", {})
        observation = EmailTriageObservation(
            email_id=obs_data.get("email_id", 0),
            subject=obs_data.get("subject", ""),
            sender=obs_data.get("sender", ""),
            body=obs_data.get("body", ""),
            emails_remaining=obs_data.get("emails_remaining", 0),
            last_reward=obs_data.get("last_reward", 0.0),
            done=payload.get("done", False),
            reward=payload.get("reward"),
            metadata=obs_data.get("metadata", {}),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )