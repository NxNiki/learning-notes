# BIRD: a Text-to-SQL Benchmark with Business Knowledge

| | |
| --- | --- |
| Paper | Jinyang Li, Binyuan Hui, Ge Qu, and 15 co-authors (University of Hong Kong, Alibaba DAMO Academy, and others), *Can LLM Already Serve as A Database Interface? A BIg Bench for Large-Scale Database Grounded Text-to-SQLs* |
| Venue | NeurIPS 2023 (spotlight, per the benchmark site) |
| Link | <https://arxiv.org/abs/2305.03111> (v3, November 2023) |
| Leaderboard | <https://bird-bench.github.io/> |
| Read for these notes | 2026-11-20: the abstract, the first part of the HTML paper, and the leaderboard. Details marked † were read only in summarized form; check them against the paper before quoting |

## Why it matters for agentic BI

Most text-to-SQL benchmarks test whether a model can turn a question into SQL over a clean schema. BIRD tests the parts that make BI hard: large, messy databases, and questions that need **external knowledge** (a business rule or a value mapping) that is not in the schema. Its headline finding is the quantitative case for the guide's Section 1.4.

## What BIRD adds over Spider

Earlier benchmarks such as Spider use databases with few rows and clean values. BIRD targets three gaps with real applications:
1. **Dirty values**: stored values are noisy and inconsistent.
2. **External knowledge**: mapping the question's wording to database values often needs information that is not in the data.
3. **Efficiency**: on large databases, a correct but slow query is a real problem.

## The dataset

- 12,751 question–SQL pairs over 95 databases (33.4 GB in total) from 37 professional domains.
- Split: 9,428 training, 1,534 development, 1,789 hidden test†.
- Each question can come with **evidence**: a short, expert-written note mapping the question's terms to the database (for example, that "eligible for a loan" means the account type is `OWNER`). Formally, the task is SQL = f(question, database, evidence). Evidence types include numeric reasoning, domain knowledge, synonyms, and explanations of what values mean†.

## Metrics

- **Execution accuracy (EX)**: a prediction counts as correct if its result equals the result of the reference query. EX is the share of correct predictions. This is what `same_result()` in the guide implements.
- **Valid efficiency score (VES)**: each correct prediction is weighted by the square root of (reference query time / predicted query time), averaged over repeated runs; wrong predictions count 0. A correct but slow query scores below 1. Since August 2024 the leaderboard uses a reward-based variant (R-VES).

## Results in the paper (test set, EX)

| System | Without evidence | With evidence |
| --- | --- | --- |
| Humans (data engineers and database students) | 72.37† | 92.96 |
| GPT-4 | 34.88 | 54.89 |
| GPT-4 + DIN-SQL | | 55.90 |
| Claude-2 | 34.60 | 49.02 |
| ChatGPT | 26.77 | 39.30 |

Two findings:
1. **Evidence adds about 20 points for every model, and for humans too.** Business knowledge, not SQL skill, was the largest single factor.
2. The best model in 2023 was about 38 points below humans.

**Error analysis** of 500 failed ChatGPT queries†: wrong schema linking (choosing the wrong tables or columns, about 42%), misunderstanding the database content (invented columns, wrong values, especially on large databases, about 41%), and misusing the evidence (for example copying a formula without adapting it to SQL, about 18%).

## The leaderboard today

As read on 2026-11-20 (values change; check the live page): the best single systems score in the low 80s on the test set, against 92.96 for humans with the evidence. Models have closed most of the 2023 gap, but not all of it, and that is with expert-written evidence supplied for every question. The site also announces newer variants (BIRD Mini-Dev, and LiveSQLBench as "BIRD 2.0").

## Connection to the guide

| BIRD | Guide |
| --- | --- |
| Evidence: knowledge not in the schema | Section 1.4, and the metric documents in `DOCS` |
| +20 points from evidence | Section 4.1: the definition, not the SQL, decides the number |
| Execution accuracy | `same_result()`, Chapter 7 |
| Schema-linking errors | Retrieval of the right tables (Chapter 5); the `amount_usd` mistake in Section 4.4 |
| Value errors on large databases | Section 4.3: row caps, and giving the model sample values |

## Takeaways for a BI agent

1. Your evaluation set should look like BIRD, not like Spider: real questions, your messy tables, and the business rule each question depends on written next to it.
2. In BIRD the evidence is handed to the model. In production the agent has to *find* it, which is the retrieval problem of Chapter 5; evaluate retrieval separately.
3. Grade by execution accuracy, and watch query cost on Redshift: VES is a reminder that a correct query that scans a whole table is a problem too.
