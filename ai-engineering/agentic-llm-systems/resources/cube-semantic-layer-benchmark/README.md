# Semantic Layers for Reliable LLM Analytics: the Cube Paired Benchmark

| | |
| --- | --- |
| Paper | Michael Rumiantsau and Ivan Fokeev (Cube), *Semantic Layers for Reliable LLM-Powered Data Analytics: A Paired Benchmark of Accuracy and Hallucination Across Three Frontier Models*, arXiv:2604.25149, 28 April 2026, 25 pages — <https://arxiv.org/abs/2604.25149> |
| Blog post | *Why semantic layers make LLM analytics reliable*, Michael Rumiantsau (VP of Product, Cube), 28 April 2026 — <https://cube.dev/blog/why-semantic-layers-make-llm-analytics-reliable-a-paired-benchmark-across-three-frontier-models> |
| Code and data | <https://github.com/cubedevinc/semantic-layer-benchmark> (questions, the semantic-layer document, all generated SQL, rows and verdicts; not read for these notes) |
| Read for these notes | 2026-11-20: the full paper and the blog post |

## Why it matters for agentic BI

It isolates one variable: the same three models, questions, harness and judge, with and without a short document describing what the data *means*. The document is plain markdown in the prompt, not a query engine, so the study measures what written-down business knowledge alone is worth. It complements the [dbt benchmark](../dbt-semantic-layer-benchmarks/), which tests a semantic-layer engine.

## Two forms of semantic layer

The paper's useful distinction:
- **Runtime form**: a code-defined model (Cube, dbt Semantic Layer, Snowflake Semantic Views, AtScale) and an engine that compiles requests into SQL. Rules are *enforced*: an unknown measure is an error.
- **Context form**: a document describing the same concepts, put in the model's prompt. Rules are *advisory*: the model is told the right answer but not forced to use it.

This paper tests the context form, and argues its gains are a lower bound on what the runtime form can give (not tested).

What such a document contains (Section 3.1): which fact table answers which kind of question; metric formulas; hierarchies and join paths; data quirks (string booleans, sentinel values, snapshot tables, the dataset's "current date"); and rules for ambiguous words ("sales" means online or all channels? "region" means customer or store?).

## The study

| | |
| --- | --- |
| Data | Cleaned Contoso Retail Dataset (a Kaggle export of Microsoft's ContosoRetailDW sample): 25 tables, sales 2007–2009, loaded into ClickHouse |
| Questions | 100, 20 in each of five tiers: simple, medium (2–3 joins), complex (window functions, snapshots), advanced (several CTEs, cohorts), expert (ambiguous business terms, recursive CTEs). Many deliberately hinge on data quirks. Each has a reference SQL query. One (q33) was excluded because its reference query ran out of memory, so **n = 99** |
| Models | Claude Opus 4.7 and Claude Sonnet 4.6 (via `claude -p`), GPT-5.4 (via `codex exec`), all at medium reasoning effort |
| Raw condition | One attempt: the question plus the `CREATE TABLE` statements of all 25 tables. No tools, no execution feedback, no retries |
| Semantic-layer condition | The same, plus one markdown document of about 9,000 characters (~2,200 tokens), hand-written by an analyst who knew the dataset but had not seen the final questions |
| Grading | The generated SQL is executed; a model judge (Claude Sonnet 4.6) compares its rows with the reference rows, given the question, schema, reference SQL and both results, and returns pass, fail or excluded under a fixed rubric. It does not know which condition produced the answer and never sees the document |
| Two verdicts | *Strict*: rows match (ignoring column order and under-1% numeric differences). *Analytical* (the primary metric): also accepts, for example, a breakdown whose values add up to the requested total, or a fraction shown as a percentage |
| Statistics | Wilson 95% intervals; pairwise exact McNemar tests on the paired pass/fail outcomes |

## Results

| Configuration | Pass rate | 95% interval | Gain | Latency | Input tokens |
| --- | --- | --- | --- | --- | --- |
| Claude Opus 4.7, raw | 50.5% | 40.8–60.1 | | 8.1 s | 19,123 |
| Claude Opus 4.7, + document | 67.7% | 58.0–76.1 | +17.2 | 8.7 s | 23,322 |
| Claude Sonnet 4.6, raw | 46.5% | 37.0–56.2 | | 9.6 s | 14,364 |
| Claude Sonnet 4.6, + document | 68.7% | 59.0–77.0 | +22.2 | 11.4 s | 17,303 |
| GPT-5.4, raw | 45.5% | 36.0–55.2 | | 15.6 s | 16,595 |
| GPT-5.4, + document | 68.7% | 59.0–77.0 | +23.2 | 14.7 s | 18,956 |

- **Every gain is significant** (p ≤ 0.0015).
- **Two clusters.** With the document, the three models are statistically indistinguishable (all p ≥ 0.79); without it, also indistinguishable (all p ≥ 0.42). All nine comparisons across the clusters are significant (p < 0.01). The spread between models is about 5 points; the effect of the document is four to five times larger.
- **The practical reading:** with the document, choose the model on cost and latency; without it, a stronger model does not recover the gap. A smaller model with the document beat a larger one without it.
- **Cost**: the document adds a few thousand input tokens per question; with prompt caching of the schema-plus-document prefix, its marginal cost is close to zero. Output was only 271–439 tokens per query.

## Why the raw condition fails (Section 5.4)

The questions the document fixed fall into five categories. All of them produce SQL that is valid, uses real tables and columns, runs, and returns rows: nothing signals the mistake.

| Category | Example from the paper | Toy-warehouse equivalent |
| --- | --- | --- |
| Which fact table | Unqualified "sales" means online sales in this dataset; the schema gives no hint | Which of several revenue tables is official |
| Snapshot vs flow | Summing daily inventory snapshots over time gives numbers about 1,000× too large | Summing a balance or headcount table over days |
| Metric formulas | Gross margin, return rate, inventory turnover, recency segments cannot be inferred from column types | Net revenue: completed orders, converted with `fx_rates` |
| Hidden conventions | A promotion key of 1 means "no discount"; booleans stored as strings; single-letter codes | `status` values; amounts in local currency |
| Time anchoring | The data ends in 2009, so "last quarter" relative to today returns nothing | "Last month" with late-arriving data |

**The remaining ~30% of failures with the document**: statistics the models rarely compose correctly inline (percentiles, correlation, standard deviation, ABC classification, threshold rankings), which the authors suggest defining as named measures; complex queries where small differences change the shape of the result; and a few genuinely ambiguous questions.

## Limitations (the authors' own)

- One dataset, one warehouse, 99 questions: enough to detect ±10-point effects, borderline for ±5. "The models are equal" is a claim about this study only.
- The judge (Claude Sonnet 4.6) is from the same family as two of the tested models. The paired design applies the same judge to both conditions, so it should not inflate the *gain*, but a cross-family judge and human checks would be better.
- Single attempt at fixed medium effort. Agentic loops, retries or higher effort may change the picture. An internal experiment found that an **agentic tool-use system with the same knowledge did not beat the schema-only baseline**, suggesting that for one-shot accuracy, putting all the context in the prompt beat having the model search for it (not reported in detail).
- The document's value depends on its quality; its author had seen the dataset, and a document written blind might be weaker.

**Read critically, too:**
- The authors work for Cube, which sells a semantic layer. The paper argues the effect is general, not product-specific, and cites other studies with similar findings, several of which are themselves vendor-published.
- Despite "hallucination" in the title, the paper reports **no separate hallucination rate**. It defines a "silent hallucination" (valid SQL, confident wrong answer) and describes such failures qualitatively, but leaves measuring it to future work.

## Connection to the guide

| Cube paper | Guide |
| --- | --- |
| Context form vs runtime form | Section 1.4: a document *informs*; a semantic layer or `check_metric_sql` *constrains* |
| "Silent hallucination": valid SQL, wrong number | Section 4.1: EU 260 instead of 231 |
| The five failure categories | `DOCS` and the metric checks; the categories are a checklist for what your documents must cover |
| Context mattered more than the model | Section 1.4: the business-specific layer is your work, not the vendor's |
| All-in-prompt beat search-based discovery here | Section 1.4: "with a handful of metrics, put them directly in the system prompt"; retrieval pays off when the knowledge no longer fits |
| Prompt caching makes the document nearly free | Chapter 7, cost control |
| Paired design, same judge | Chapter 7, evaluation; Exercise 4 |

## Takeaways for a BI agent

1. Write the document before comparing models: fact-table rules, metric formulas, data quirks, time anchoring, and rules for ambiguous words. In this study it was worth about 20 points; the choice of model was worth almost nothing.
2. Use the five failure categories as a checklist when writing it, and add named measures for anything statistical.
3. While the document fits in the prompt, put it all in (and cache it) rather than retrieving pieces of it.
4. A document alone left ~30% wrong in a single attempt. Add constraints (a semantic-layer engine, metric checks) and feedback (running the query, as the guide's agent does) on top.
5. Evaluate your own changes the same way: every question under both conditions, with the same judge.
