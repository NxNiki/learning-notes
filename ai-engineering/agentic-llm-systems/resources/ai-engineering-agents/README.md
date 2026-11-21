# AI Engineering, Chapter 6: Agents (Chip Huyen)

| | |
| --- | --- |
| Book | Chip Huyen, *AI Engineering: Building Applications with Foundation Models*, O'Reilly, 2024 |
| Chapter | 6, "RAG and Agents" |
| Link | <https://www.oreilly.com/library/view/ai-engineering/9781098166298/> |
| Read for these notes | 2026-11-20: her blog post [*Agents*](https://huyenchip.com/2025/01/07/agents.html) (7 January 2025), which is adapted from the agents part of the chapter |

**Coverage.** These notes cover the agents material as published in the blog post. The book page could not be fetched, so the chapter's RAG half and its section on memory are not summarized here (the blog post says memory is left for a later post). The sections on tool selection, ReAct and Reflexion, and the failure-mode metrics come from the last part of the post, which was read only in summarized form; treat those details as less certain.

## Why it matters for agentic BI

Her running example is a BI agent: an agent with three actions (generate a response, generate SQL, execute SQL) answering a sales-projection question. Her catalogue of agent failure modes and metrics is the most practical evaluation checklist for a BI agent.

## Main ideas

**Definition.** An agent is anything that perceives its environment and acts on it. It is defined by its *environment* (set by the use case: a database, the web, a game) and its *actions*, which tools extend. The two constrain each other: the environment limits which actions make sense, and the tool inventory limits which environments the agent can work in.

**Why agents need strong models.** Errors compound. With 95% accuracy per step, a 10-step task succeeds about 60% of the time (0.95¹⁰ ≈ 0.60), and a 100-step task about 0.6% of the time. And tool use raises the stakes of each mistake.

**Three kinds of tools.**

| Kind | Examples | BI version |
| --- | --- | --- |
| Knowledge augmentation (read) | Retrievers, internal APIs, Slack or email readers, web search | `search_docs`, `run_sql`, the data catalog |
| Capability extension | Calculators, unit and time-zone converters, code interpreters, OCR | A Python sandbox for forecasting or charts |
| Write actions | SQL writes, sending email, bank transfers | Writing to a table, sending a report, creating a dashboard |

More tools mean more capability, but each tool is harder to use well. Write actions need the most care: do not give an unreliable system irreversible powers, any more than you would let an intern delete production data. Code execution opens injection risks.

**Planning.**
- A task has a goal and constraints; a plan is the sequence of steps. Planning is a search problem.
- *Separate planning from execution*: generate a plan, validate it, then run it. Running a bad plan wastes time and money. Validation can be simple rules (reject plans with unknown tools or too many steps) or a model as judge.
- Several plans can be generated in parallel and the best chosen. An intent classifier helps choose tools and reject out-of-scope requests.
- Humans can supply or approve plans, and must approve risky actions such as database updates. Decide the level of automation per action.
- Her four steps: (1) generate a plan, (2) reflect on it and correct errors, (3) execute it (usually through function calls), (4) reflect on the outcome and re-plan if the goal is not met.
- Whether language models can really plan is debated; her view is that it is unclear whether the limit is the models or how they are used.
- Function calling: declare a tool inventory with names, parameters and documentation. Models often guess parameter values, so log the values they actually use and inspect them.
- Plan granularity: detailed plans are harder to generate but easier to execute; plans written in natural language survive tool renames but need a translation step.
- Control flow: sequential, parallel, if (routing) and loops. When the model decides the control flow, non-sequential plans are harder; check which control flows a framework supports.

**Reflection and error correction.** Optional, but in her framing usually what makes an agent succeed. It can happen after the request arrives, after planning, after each step and at the end, either as a self-critique prompt or a separate scorer. She discusses ReAct (alternating thought, action and observation) and Reflexion (separate evaluator and self-reflection).

**Tool selection** (summarized source). The right set depends on the environment, the task and the model. Compare tool sets, run ablations (remove a tool and measure), find frequently misused tools, and look at how often each tool is called; tools that are always used together can be merged.

**Failure modes and how to measure them.** "Evaluation is about detecting failures": list the ways the agent fails, then measure how often each happens.

| Failure | Examples | Metrics |
| --- | --- | --- |
| Planning | Unknown tool; right tool, wrong parameters; right tool, wrong values; plan ignores a constraint (the budget); agent wrongly believes it is done | On a set of tasks, generate K plans each: share of valid plans, plans needed per valid plan, share of valid tool calls, frequency of each error type |
| Tool | The right tool returns a wrong output (bad SQL, bad caption); translation errors | Test each tool on its own; log every call and output. Repeated failures in one area may mean a tool is missing |
| Efficiency | Too many steps, too slow, too expensive | Steps per task, cost per task, time per action; compare with a baseline (another agent, or a person) |

## Connection to the guide

| Book | Guide |
| --- | --- |
| Environment and tools | Chapter 2 |
| Compound errors need strong models | Chapter 3: tune effort per agent rather than lowering it everywhere |
| Write actions are dangerous | Section 4.3: the BI agent has no write tools at all, enforced by the database |
| Separate plan from execution, validate the plan | The orchestrator plans; `check_metric_sql` validates SQL before it runs |
| Failure modes and metrics | Chapter 7 and Exercise 4 |

## Takeaways for a BI agent

1. Keep the BI agent read-only. Any write action (scheduling a report, creating a table) should go through a separate, approved path.
2. Turn her failure table into your evaluation: for each test question, record whether the agent picked the right tables (planning), whether the SQL was right (tool), and how many steps and how much it cost (efficiency).
3. Log the parameters of every tool call; in BI the most common wrong parameter is the date range.
