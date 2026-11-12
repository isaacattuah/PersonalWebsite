---
title: Building a practice customer: persona agents, hidden objectives, and a judge you can trust
date: 2026-11-11
summary: How Customer Scenario Simulator II works: one agent plays a customer who is holding something back, a second grades the conversation against a rubric, and a small eval harness checks that the grader deserves to be believed.
kind: Deep dive
---

Discovery is the skill that separates a good Customer Engineer from a product catalog with a calendar. It is also the hardest one to practice. You cannot rehearse on a real customer, and a colleague playing the customer already knows what you are fishing for.

In 2023 I built a small Colab notebook that used PaLM's `chat-bison` to role-play a customer. It was fun and not much more. The customer was a random adjective attached to a product area, and the feedback was one freeform prompt that mostly said "good job."

Customer Scenario Simulator II is the rebuild. This piece walks through the three decisions that made it useful: giving the customer something to hide, grading with a rubric instead of a vibe, and testing the grader before trusting it. The [code is on GitHub](https://github.com/isaacattuah/Customer-Scenario-Simulator-v2).

## The shape of the system

There are two agents, one web service, and one warehouse.

| Part | What it does | Runs on |
| --- | --- | --- |
| Persona agent | Plays the customer, in character, turn by turn | Claude on Vertex AI |
| Coach agent | Reads the finished transcript and scores it | Claude on Vertex AI |
| API and UI | Sessions, chat, grading | FastAPI on Cloud Run |
| Skill history | Sessions, turns, scores, a leaderboard view | BigQuery |

A session has three calls. `/session/new` creates a persona. `/chat` sends your message and returns the customer's reply. `/grade` hands the whole conversation to the coach and returns a scorecard.

The two agents never talk to each other. They have separate system prompts and separate jobs, and the only thing that passes between them is the transcript. That separation is the whole design. The persona must not know how it will be graded, or it starts performing for the rubric. The coach must not be in the conversation, or it stops being a judge.

## Give the customer something to hide

The first version failed because the customer had no interior. Ask it what it needed and it told you. Real customers do not do that. The stated problem ("we want to cut our inference bill") is rarely the real one ("our CTO promised the board a launch date and we do not have the capacity").

So each session starts by generating a structured persona card. Here is a simplified illustration of the idea, not the exact schema in the repository:

```json
{
  "company": "Series B logistics startup, 60 engineers",
  "role": "VP of Engineering",
  "personality": "skeptical, short on time",
  "product_area": "data analytics",
  "stated_goal": "Cut warehouse spend before the next board meeting",
  "hidden_objectives": [
    "A migration last year went badly and the team distrusts lift-and-shift",
    "The real deadline is a customer audit in six weeks"
  ],
  "reveal_rules": "Share a hidden objective only when asked a specific, open question about it"
}
```

The persona agent receives the card and the running conversation state as context on every turn. The person practicing never sees the hidden objectives. They have to earn them, the same way they would in a real meeting: by asking better questions.

Two things made this work in practice.

**Structure beats adjectives.** "Be a difficult customer" produces theater. A card with a stated goal, specific hidden objectives and explicit rules for when to reveal them produces a customer who is consistent across twenty turns.

**State is context, not memory.** The service keeps session state itself and injects it on each call. The model is never asked to remember what it already revealed. It is told.

## Grade with a rubric, and demand evidence

When you finish, the coach agent gets three things: the full transcript, the hidden objectives, and a rubric. The rubric lives in a YAML file and is the single source of truth for what "good" means. Changing how Customer Engineers are assessed is a change to that file, not to a prompt buried in code.

The coach returns structured JSON: a score for each rubric dimension, and for each score, the turns in the transcript that justify it. Then the scorecard reveals what the customer was hiding, so you can see which objective you found and which one walked out of the room with them.

The evidence requirement matters more than the score. A grader that says "discovery: 3 out of 5" teaches you nothing. A grader that says "3 out of 5, because in turn 4 you asked about timeline but accepted the first answer, and in turn 9 you pitched before confirming the constraint" gives you something to do differently tomorrow.

Structured output from a model fails occasionally, so the service validates the response against a schema and allows exactly one repair attempt if parsing fails. One retry catches almost everything. Unlimited retries hide a prompt problem you should fix instead.

## Grade the grader

This is the part most LLM-as-judge projects skip, and it is the part I would keep if I had to throw the rest away.

A judge is only useful if it is consistent and calibrated. So the repository includes a small harness with hand-labeled golden transcripts: one strong, one mixed, one weak. Each has an expected score range written down in advance. The harness runs every transcript through the judge several times and checks three things:

1. **Consistency.** Does the same transcript get roughly the same score on every run?
2. **Calibration.** Do the scores land inside the range a human said they should?
3. **Ranking.** Does strong beat mixed, and mixed beat weak, every time?

```bash
python -m evals.judge_consistency --runs 3
```

If you change the rubric, the coach prompt or the model, you rerun this before you believe a single scorecard. It is the same discipline as a unit test, pointed at the one component whose output everyone will take on faith.

## Keep the history, but never block on it

Every session, turn and score is written to BigQuery, with a leaderboard view on top. That turns a toy into a training tool. You can ask whether your discovery scores improved over a month, or which rubric dimension a whole team is weakest on.

Persistence is fail-soft. If BigQuery is unreachable, the conversation carries on and the app says nothing dramatic. Session state lives in memory and BigQuery is the durable record. For a practice tool that is the right trade: losing a row of analytics is cheap, and killing someone's session in the middle of a hard conversation is not. You can also switch BigQuery off entirely with one environment variable and run the full loop on a laptop.

## Deployment notes that cost me time

- **Scale to zero.** The service is a source-based Cloud Run deploy. A practice tool is idle most of the day and should cost nothing while it is.
- **No keys in code.** Authentication is Application Default Credentials end to end.
- **Use `/health`, not only `/healthz`.** On Cloud Run the Google Front End intercepts `/healthz` before it reaches your container. I registered both paths and point checks at `/health`.
- **One script.** A single deploy script enables the APIs, creates the dataset, tables and view, and ships the service.

## What I would tell a startup building something similar

The pattern here is not specific to sales training. Any product where one model plays a role and another evaluates the result has the same three risks.

Keep the actor and the judge apart. Shared context is how a judge ends up grading intentions instead of outcomes.

Put the rubric in data. The people who own the standard should be able to read it and change it without reading Python.

Test the judge first. If the grader cannot rank three hand-labeled examples in the right order, nothing built on top of it means anything.
