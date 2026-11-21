# Building Effective Agents (Anthropic)

| | |
| --- | --- |
| Authors | Erik S. and Barry Zhang (Anthropic) |
| Published | 19 December 2024 |
| Link | <https://www.anthropic.com/engineering/building-effective-agents> |
| Read for these notes | 2026-11-20, full text |

The page now carries a note that much of the tooling it mentions has changed since 2024. The patterns and principles have not; read it for those.

## Why it matters for agentic BI

It gives the vocabulary for deciding *how much* agent a BI assistant needs. Most of a BI system can be a workflow (fixed steps); only the parts whose steps cannot be predicted need an agent. The guide's Sections 1.1, 1.2 and 4.5 follow this article.

## Main ideas

**Definitions.**
- *Agentic systems* is the umbrella term.
- *Workflows*: the model and its tools follow code paths you wrote.
- *Agents*: the model directs its own process and tool use.
- The building block of both is the *augmented LLM*: a model with retrieval, tools and memory, which can write its own search queries, choose tools and decide what to keep. Expose these through a clean, documented interface (the article mentions the Model Context Protocol as one way).

**Five workflow patterns.**

| Pattern | How it works | Use when | BI example (ours, not the article's) |
| --- | --- | --- | --- |
| Prompt chaining | Each call takes the previous output; code can check ("gate") between steps | The task splits into fixed sub-steps; trade latency for accuracy | Draft SQL → lint against metric rules → run → summarize |
| Routing | A classifier sends each input to a specialized prompt, tool or model | Inputs fall into distinct categories that are classified reliably | "Explain a metric" vs "compute a number" vs "out of scope"; easy questions to a cheap model |
| Parallelization | *Sectioning*: independent sub-tasks at once. *Voting*: the same task several times | Speed, or more confidence through several attempts | Revenue for 12 regions at once; generate SQL 3 times and compare results |
| Orchestrator–workers | A lead model decides sub-tasks at run time and delegates them | The sub-tasks cannot be predicted in advance | The guide's three-agent system |
| Evaluator–optimizer | One model produces, another critiques, in a loop | Clear evaluation criteria, and feedback measurably helps | SQL agent + metric checker |

**Agents.** Start from a person's request, then plan and act on their own, checking "ground truth" from the environment (tool results, executed code) at each step, and pausing for human input at checkpoints or when blocked. Bound them with stopping conditions such as a maximum number of iterations. They are usually simple to implement: a model using tools in a loop. So the design of the tools and their documentation carries most of the weight. Use them for open-ended problems where the number of steps cannot be fixed in advance, in environments you trust, and test them in sandboxes: they cost more, and errors compound.

**When not to build one.** Find the simplest solution first; often a single well-prompted call with retrieval and examples is enough. Agentic systems trade latency and cost for task performance, so check that the trade is worth it. Workflows give predictability for well-defined tasks; agents give flexibility.

**Frameworks.** They make calling models, defining tools and chaining calls easy, but they add layers that hide the actual prompts and responses, make debugging harder, and tempt you into unneeded complexity. Start with the model API directly (most patterns are a few lines). If you use a framework, understand the code underneath, and remove abstraction when moving to production.

**Tool design: the agent–computer interface (ACI).** Put as much effort into tool definitions as into the main prompt, and as much care into the ACI as into a human–computer interface.
- Read each tool from the model's point of view: is its use obvious from the name, description and parameters? Include example usage, edge cases, input formats, and how it differs from similar tools.
- Write descriptions like docstrings for a junior developer; rename parameters if that makes them clearer.
- Test with many example inputs and fix the mistakes you see.
- *Poka-yoke* the tools: change the arguments so that mistakes are hard to make. Their example: the model made errors with relative file paths, so the tool was changed to require absolute paths, and the errors stopped.
- Prefer formats the model has seen a lot of (plain text, markdown) over formats that need counting or escaping.
- On their SWE-bench agent they spent more time on the tools than on the overall prompt.

**Where agents work well (appendix).** Tasks that mix conversation and action, have clear success criteria, allow feedback loops and keep humans in oversight: customer support (resolution is measurable) and coding (tests verify the work, though human review remains essential).

**Principles.** Keep the design simple; make the agent's planning visible; build the ACI carefully. Add complexity only when it measurably improves results.

## Connection to the guide

| Article | Guide |
| --- | --- |
| Workflows vs agents, start simple | Sections 1.1–1.2 |
| The five patterns | Section 4.5 |
| ACI and tool design, poka-yoke | Section 2.2: strict schemas, `enum` for `kind` and `metric_id`, errors written for the model |
| Ground truth from the environment | Section 4.4: the database error and the metric check corrected the SQL agent |
| Start with the API, not a framework | `agents.py`: the loop is written out in eight lines |

## Takeaways for a BI agent

1. Build the predictable parts (permission checks, query execution, formatting) as code, and keep the agent for planning and SQL writing.
2. Spend your effort on the tools: `run_sql`, `search_docs`, and above all a metric tool that makes wrong definitions hard to express (the poka-yoke idea applied to metrics is a semantic layer).
3. Use the executed result as ground truth, not the model's opinion of its own SQL.
