---
title: Notes from building the agent behind "Four steps for startups to build multi-agent systems"
date: 2025-11-14
summary: My colleague Oluwamayowa Awojuyigbe wrote up a multi-agent build I helped architect. These are the four lessons from that project I now repeat to almost every startup I work with.
canonical_url: https://cloud.google.com/blog/topics/startups/four-steps-for-startups-to-build-multi-agent-systems
source: the Google Cloud Blog
kind: Companion
---

The technical guide on the Google Cloud Blog was written by Oluwamayowa Awojuyigbe, a fellow Customer Engineer. I was one of the collaborators who helped architect and build the agent it describes. The article is his and you should read it for the full walkthrough and code. What follows is my own short list of what the project taught me.

## 1. Decide what kind of build this is before writing any code

There are three honest options: use an agent someone already built, adopt a partner's, or write your own. We wrote our own, code-first, because the workflow encoded logic specific to the team and we needed control over orchestration.

Most startups skip this decision and discover it later, halfway through fighting a tool that was never meant for their case. Ten minutes on it up front is cheap.

## 2. Let the model talk and let code do the work

The design that held up was a hybrid. A language model handles the conversational part, such as onboarding the user and collecting what it needs. Then it hands off to deterministic workflow steps that loop over the real work, with each step wrapped as a tool.

The instinct to make everything an agent is strong and usually wrong. If a step has one correct way to run, it should be code. Save the model for the parts that need judgment.

## 3. Isolate state, or your agent gets worse as it goes

Our agent processed a list of companies in a loop. Left alone, context from the first company bled into the fifth, and quality dropped the longer it ran. The fix was to wrap the research pipeline as its own agent, called as a tool, so every item started with a clean context.

If your agent is good on the first task and strange by the tenth, look here first.

## 4. Treat the path to production as part of the build

A demo on localhost proves the idea. It does not prove you can ship it. We started from a production-grade project template, set up CI/CD with a manual approval before production, and deployed to a managed runtime that scales to zero when idle.

None of that is exciting. All of it is the difference between an agent your team shows in a meeting and one your customers use.

## Why I keep coming back to this project

Every one of these lessons is about structure, not model quality. The model was never the hard part. Knowing where to put the boundaries was.
