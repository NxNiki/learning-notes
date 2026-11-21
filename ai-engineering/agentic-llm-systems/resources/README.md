# Resource notes

Summaries of the readings most relevant to agentic BI, one folder each, chosen from the guide's [Chapter 10](../README.md#chapter-10-further-reading). Each note gives the source details, the main ideas and numbers, how they connect to the guide, and takeaways for building a BI agent.

| Folder | Resource | What it gives you |
| --- | --- | --- |
| [building-effective-agents](building-effective-agents/) | Anthropic, *Building effective agents* (2024) | Workflows vs agents, five patterns, tool design (the agent–computer interface) |
| [multi-agent-research-system](multi-agent-research-system/) | Anthropic, *How we built our multi-agent research system* (2025) | Orchestrator–workers in production: token costs, delegation, evaluation, operations |
| [ai-engineering-agents](ai-engineering-agents/) | Chip Huyen, *AI Engineering*, chapter 6 (agents part) | Tools, planning, reflection, and a failure-mode checklist with metrics |
| [dbt-semantic-layer-benchmarks](dbt-semantic-layer-benchmarks/) | dbt Labs, semantic layer vs text-to-SQL (2023 and 2026) | When the agent should query metrics and when it should write SQL |
| [cube-semantic-layer-benchmark](cube-semantic-layer-benchmark/) | Cube, paired benchmark across three models (2026) | Business context mattered more than the choice of model |
| [bird-text-to-sql](bird-text-to-sql/) | BIRD benchmark (NeurIPS 2023) and leaderboard | Text-to-SQL on messy data with business knowledge; execution accuracy |

**Suggested order**: Building effective agents → AI Engineering → the multi-agent post → BIRD → the dbt and Cube benchmarks.

**How these notes were written.** Each source was read on 2026-11-20 and summarized in my own words, with only short quotations. Where a source could not be read in full, the note says which parts it does not cover; numbers that came only from a partial read are marked. Benchmark and leaderboard figures are snapshots: check the source before quoting them.
