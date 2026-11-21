# How We Built Our Multi-Agent Research System (Anthropic)

| | |
| --- | --- |
| Authors | Jeremy Hadfield, Barry Zhang, Kenneth Lien, Florian Scholz, Jeremy Fox, Daniel Ford (Anthropic) |
| Published | 13 June 2025 |
| Link | <https://www.anthropic.com/engineering/multi-agent-research-system> |
| Read for these notes | 2026-11-20, full text (diagrams read from their captions only) |

## Why it matters for agentic BI

It is a detailed account of an orchestrator–workers system in production, the same architecture as the guide's BI system, with measured costs, the prompting lessons, the evaluation method, and the operational problems. Almost every lesson transfers to a BI assistant.

## Main ideas

**Why several agents.** Research is open-ended: what to look at next depends on what was just found, so the steps cannot be fixed in advance. Sub-agents each work in their own context window and return only the important findings, which compresses information for the lead; separate prompts, tools and paths also reduce the chance that one bad early choice derails everything. Multi-agent works best on *breadth-first* questions with many independent directions (their example: the board members of every IT company in the S&P 500, which a single agent searched slowly, one at a time, and failed).

**Architecture.**
1. A lead agent analyses the query, plans, and saves the plan to memory (long contexts get truncated, so the plan must persist outside the context).
2. It starts sub-agents with specific research tasks; the number varies with the question.
3. Each sub-agent searches, evaluates results by thinking between tool calls, and reports back.
4. The lead combines the results and decides whether more research is needed; if so, it starts more sub-agents or changes strategy.
5. A separate citation agent then attaches each claim to its source.

They contrast this with fixed RAG, which retrieves once: here the search adapts to what it finds.

**Numbers.**

| Finding | Value |
| --- | --- |
| Lead Claude Opus 4 with Claude Sonnet 4 sub-agents vs a single Opus 4 agent, internal research eval | +90.2% |
| Share of performance variance on BrowseComp explained by token usage, number of tool calls and model choice | 95% (token usage alone: 80%) |
| Upgrading the model vs doubling the token budget | Moving to Sonnet 4 gained more than doubling the budget on Sonnet 3.7 |
| Tokens used, relative to a chat | Agents ~4×, multi-agent systems ~15× |
| Parallelism | 3–5 sub-agents at once, each making 3+ tool calls at once: up to 90% less time on complex queries |
| Rewriting a flawed tool's description | 40% less task completion time |

The economics only work when the task is worth the tokens. Tasks with heavy shared context or many dependencies between agents are poor fits; coding has fewer parallel sub-tasks than research.

**Prompting lessons.**
1. *Think like your agents*: run them step by step with the exact prompts and tools, and watch for failures (continuing after enough results, overly long queries, wrong tools).
2. *Teach the lead to delegate*: every sub-task needs an objective, an output format, guidance on tools and sources, and clear boundaries. Vague tasks made sub-agents duplicate each other's work.
3. *Scale effort to the question*: rules of thumb in the prompt, from 1 agent with 3–10 tool calls for a simple fact to more than 10 sub-agents for complex research. Early versions started 50 sub-agents for simple questions.
4. *Tool design matters*: a bad tool description sends agents down the wrong path; prefer specialized tools to generic ones.
5. *Let agents improve themselves*: a model given a flawed tool ran it many times and rewrote its description (the 40% result).
6. *Start wide, then narrow*: agents defaulted to long, specific search queries that found little.
7. *Guide the thinking*: extended thinking as the lead's planning scratchpad; sub-agents think after each tool result to judge quality.
8. *Parallelize tool calls*: the source of the speed-ups.

Prompts encode heuristics, not rigid rules; guardrails stop runaway behaviour.

**Evaluation.**
- Judge outcomes, not paths: two runs can take different valid routes.
- Start small: about 20 real queries were enough at first, because early changes have large effects (one prompt change moved success from 30% to 80%).
- A model as judge: one call with one rubric, scoring 0.0–1.0 plus pass/fail, on factual accuracy, citation accuracy, completeness, source quality and tool efficiency. It works best when there is a clear right answer.
- Humans still find what the evaluations miss: early agents preferred search-engine-optimized content farms over better sources, which was fixed with source-quality guidance in the prompt.
- For agents that change state, evaluate the end state, not every step.

**Production problems.**
- *State and compounding errors*: long runs need durable execution and resumption from the point of failure, not restarts; combine telling the model a tool is failing with deterministic retries and checkpoints.
- *Debugging*: agents are non-deterministic, so full tracing is essential; they monitor decision patterns without reading conversations, for privacy.
- *Deployment*: agents are always mid-task, so updates use gradual ("rainbow") deployments with old and new versions running side by side.
- *Synchronous execution*: the lead waits for each batch of sub-agents, so one slow sub-agent blocks everything; asynchronous execution is faster but harder to coordinate.

## Connection to the guide

| Article | Guide |
| --- | --- |
| Orchestrator, sub-agents with their own context | Sections 4.2 and 4.5, `Agent.as_tool` |
| Every sub-task needs objective, format, boundaries | The orchestrator prompt: "give the SQL agent a self-contained task" |
| ~15× tokens; worth it only when the task is | Section 4.5, "the costs are also real" |
| Thinking as a scratchpad; effort scaled to the task | Chapter 3 |
| Start with ~20 real queries; judge outcomes | Chapter 7, evaluation set |
| Full tracing | `Trace` in `agents.py` |

## Takeaways for a BI agent

1. A BI question is usually *not* breadth-first: "revenue by region" is one query, not ten independent searches. Expect a lead plus one or two specialists, not a swarm; parallel fan-out pays for questions like "compare these five metrics".
2. Most failures will be hand-off failures: the SQL agent did not get the date range or the definition. Make the task format explicit.
3. For BI, outcome evaluation is easy and strict: compare the result rows with a known answer (execution accuracy). Start with 20 real questions from your stakeholders.
4. Put the effort rules in the prompt: a lookup should not start three agents.
