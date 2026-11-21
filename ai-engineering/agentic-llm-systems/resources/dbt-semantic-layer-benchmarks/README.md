# Semantic Layer vs Text-to-SQL: the dbt Labs Benchmarks

Two articles from dbt Labs, three years apart, testing the same idea: are LLM answers to business questions more accurate when the model queries a semantic layer than when it writes SQL itself?

| | 2023 article | 2026 article |
| --- | --- | --- |
| Title | *Semantic Layer as the Data Interface for LLMs* | *Semantic Layer vs. Text-to-SQL: 2026 Benchmark Update* |
| Authors | Jason Ganz | Jason Ganz and Benoit Perigaud |
| Published | 30 November 2023 | 7 April 2026 |
| Link | <https://www.getdbt.com/blog/semantic-layer-as-the-data-interface-for-llms> | <https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026> |

Benchmark site: <https://dbt-labs.github.io/dbt-llm-sl-bench>. Read for these notes on 2026-11-20 (charts in the articles are images and were not read).

## Why it matters for agentic BI

This is the evidence behind the guide's Section 1.4: business definitions belong in a semantic layer, and the agent should query metrics rather than write their formulas. It also shows exactly where that advice stops working.

## Background: the two approaches

- **Text-to-SQL**: the model reads the schema and writes SQL from scratch. Flexible, but it has to guess what tables and columns mean, and a query that runs can still return the wrong number.
- **Semantic layer** (dbt's MetricFlow): metrics and dimensions are defined in the dbt project. The model only picks *which* metrics, dimensions and filters; MetricFlow writes the SQL, deterministically. Reliable, but it can only answer what has been modelled.

## The 2023 article

**The starting point** was a paper from data.world (Sequeda et al., arXiv:2311.07509): GPT-4, with no examples, answering insurance-company business questions either by writing SQL from the database schema or by querying a knowledge graph. An answer counted as correct if it returned all the required rows and columns of a reference query. SQL reached 16.7% accuracy and the knowledge graph 54.2%; on the questions over the most complex parts of the schema, plain SQL could not answer at all.

**dbt's replication.** They rebuilt the dataset as a dbt project with semantic models and tested only the questions closest to what a semantic layer is for (complex questions over a simple part of the schema). Three questions needed more chains of joins than MetricFlow supported and were left out, leaving eight. Result: **83% accuracy** on those eight; some questions were right every time, and the ones needing too many joins always failed. Adding one natural-language description to the project moved several questions from 0% to 100% correct.

**Its own caveats**: a small proof of concept, on data that was not modelled as a star schema; the 16.7% SQL baseline is the paper's, not a dbt measurement.

## The 2026 article

**Setup.**
- The same ACME Insurance dataset: 15 heavily normalized tables.
- 11 questions, each run 20 times. 3 of them need more joins than the semantic layer can express ("too many hops").
- Four configurations: text-to-SQL on the original schema (whole schema in the prompt); a minimal semantic layer on the original tables; a semantic layer on a properly modelled project; text-to-SQL on that modelled project.
- Models: Claude Sonnet 4.6 and GPT-5.3 Codex at default reasoning effort, chosen after a pilot that also tried Claude Opus 4.6 and GPT-5.2. In the pilot, reasoning effort barely changed accuracy but made the GPT models much slower at the highest setting.
- How correctness was graded is not described in the article; the repository is the place to check.

**Results on the original schema** (accuracy):

| Approach | 2023 (GPT-4) | 2026, Sonnet 4.6 | 2026, GPT-5.3 Codex |
| --- | --- | --- | --- |
| Text-to-SQL, all 11 questions | 32.7% | 64.5% | 64.5% |
| Semantic layer, 8 answerable questions | 83.1% | 100% | 100% |
| Semantic layer, 3 "too many hops" questions | 0% | 0% | 0% |
| Semantic layer, all 11 | 60.5% | 72.7% | 72.7% |

Text-to-SQL nearly doubled in three years. The semantic layer became perfect on what it can express and still cannot answer the rest.

**With minimal modelling.** A model was asked to add as few dbt models as possible so that all 11 questions became answerable; it added three. Text-to-SQL was given the new tables too.

| Approach | Sonnet 4.6 | GPT-5.3 Codex |
| --- | --- | --- |
| Text-to-SQL on the modelled project | 90.0% | 84.1% |
| Semantic layer on the modelled project | 98.2% | 100% |

Modelling improved *both* approaches.

**How each fails.** Text-to-SQL picks wrong joins and misreads columns, and gives a plausible wrong number with nothing to flag it. The semantic layer fails by saying it cannot answer: it does not return wrong data (earlier runs had a few wrong-dimension picks, which the authors say stopped).

**Recommendation: "It's both."**
- Where accuracy matters (board reporting, audits, KPIs, weekly reports): use the semantic layer.
- For ad hoc exploration: try the semantic layer first; if it cannot answer, see whether a small modelling change closes the gap; otherwise fall back to text-to-SQL with as much schema context as possible.

**Caveats.** Putting the whole schema in the prompt does not scale to large warehouses; questions outside the model's scope still need modelling work; the absolute numbers will keep rising. Cost and latency results are in the repository, not the article. Eleven questions is a small set, and dbt Labs sells the semantic layer.

## Connection to the guide

| dbt articles | Guide |
| --- | --- |
| Text-to-SQL fails silently with a plausible number | Section 4.1: EU 260 instead of 231 |
| The semantic layer fails loudly, by refusing | Section 5.5: "an agent told nothing found can react" |
| Descriptions moved questions from 0% to 100% | Section 5.5: aliases in the metric documents |
| "Both": semantic layer first, SQL as fallback | Section 1.4 and Exercise 5 |
| Modelling helps both approaches | Your dbt project is the agent's knowledge base |

## Takeaways for a BI agent

1. Give the agent two tools in order of preference: `query_metric` (semantic layer) first, `run_sql` second, and have answers say which one was used.
2. Clean dbt modelling and descriptions are agent work, not only analytics work: they raised both approaches.
3. Mark answers from raw SQL as exploratory; reserve "official" numbers for semantic-layer answers.
