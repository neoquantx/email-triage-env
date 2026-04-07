---
title: Email Triage Env Environment Server
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
---

# Email Triage Environment

An OpenEnv RL environment where an AI agent learns to triage emails by assigning priority, category, and reply decisions.

## Environment Description

In the real world, professionals receive hundreds of emails daily. This environment simulates that challenge — the agent must correctly classify each email across three dimensions:
- **Priority**: `urgent`, `normal`, or `low`
- **Category**: `work`, `spam`, `personal`, `newsletter`
- **Reply**: whether the email needs a response

## Action Space

| Field | Type | Values |
|-------|------|--------|
| priority | string | `urgent`, `normal`, `low` |
| category | string | `work`, `spam`, `personal`, `newsletter` |
| should_reply | boolean | `true`, `false` |

## Observation Space

| Field | Type | Description |
|-------|------|-------------|
| email_id | int | Current email index |
| subject | string | Email subject line |
| sender | string | Email sender address |
| body | string | Email body text |
| emails_remaining | int | Emails left in episode |
| last_reward | float | Reward from last action |
| done | boolean | Whether episode is complete |

## Tasks

| Task | Difficulty | Emails | Description |
|------|-----------|--------|-------------|
| easy_triage | Easy | 3 | Obvious priority and category |
| medium_triage | Medium | 5 | Mixed types including spam |
| hard_triage | Hard | 10 | All categories, full accuracy required |

## Reward Function

Each email is scored out of 1.0:
- Correct priority → +0.4
- Correct category → +0.4
- Correct reply decision → +0.2

Final episode reward = average score across all emails.

## Setup & Usage

```bash
# Install dependencies
uv sync

# Run server locally
uv run server

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/tasks
curl http://localhost:8000/baseline
curl http://localhost:8000/grader
```

## Baseline Scores

| Task | Score |
|------|-------|
| easy_triage | ~0.33 (random baseline) |
| medium_triage | ~0.40 (random baseline) |
| hard_triage | ~0.32 (random baseline) |

## Docker

```bash
docker build -t email_triage_env:latest -f server/Dockerfile .
docker run -p 8000:8000 email_triage_env:latest
```

## API Endpoints

- `GET /health` — Health check
- `GET /tasks` — List tasks and action schema
- `GET /baseline` — Run baseline agent and return scores
- `GET /grader` — Return grader scoring criteria
- `POST /reset` — Reset environment
- `POST /step` — Execute action
- `GET /state` — Get current state
- `WS /ws` — WebSocket persistent session