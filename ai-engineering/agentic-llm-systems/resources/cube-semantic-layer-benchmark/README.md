# Semantic Layers for Reliable LLM Analytics: the Cube Paired Benchmark

| | |
| --- | --- |
| Blog post | *Why semantic layers make LLM analytics reliable: a paired benchmark across three frontier models*, Michael Rumiantsau (VP of Product, Cube), 28 April 2026 — <https://cube.dev/blog/why-semantic-layers-make-llm-analytics-reliable-a-paired-benchmark-across-three-frontier-models> |
| Paper | Michael Rumiantsau and Ivan Fokeev, *Semantic Layers for Reliable LLM-Powered Data Analytics: A Paired Benchmark of Accuracy and Hallucination Across Three Frontier Models*, arXiv:2604.25149, 28 April 2026 — <https://arxiv.org/abs/2604.25149> |
| Benchmark code | github.com/cubedevinc/semantic-layer-benchmark (linked from the blog; not read) |
| Read for these notes | 2026-11-20: the full blog post and the paper's abstract. The paper's full text could not be read, so its grading method, hallucination measurements, error analysis and limitations are **not** covered here |

The blog post and the paper describe the same study (the post links the paper, and the numbers match).

## Why it matters for agentic BI

It isolates one variable: the same models, questions and harness, with and without a short document describing the business meaning of the data. It complements the dbt benchmark, because here the "semantic layer" is only a document in the prompt, not a query engine. So it measures what *business context alone* is worth.

## The study

- **Data**: 100 natural-language questions over the Contoso retail dataset (a cleaned Kaggle export of Microsoft's ContosoRetailDW sample), loaded into ClickHouse.
- **Models**: Claude Opus 4.7, Claude Sonnet 4.6, GPT-5.4.
- **Two conditions** for each model:
  - *Schema only*: the warehouse table definitions and the question.
  - *Schema + semantic layer*: the same, plus a hand-written 4 KB markdown document describing measures, conventions and how to resolve ambiguous terms. No query engine, no tools: the document is simply pasted into the prompt.
- Same questions, same single-attempt protocol, same reasoning effort and the same judge for all six runs. Paired design: every question is answered under both conditions, so each question is its own control.

## Results

Accuracy, with 95% intervals as reported:

| Model | Schema only | + semantic layer document | Gain |
| --- | --- | --- | --- |
| Claude Opus 4.7 | 50.5% [40.8, 60.1] | 67.7% [58.0, 76.1] | +17.2 points |
| Claude Sonnet 4.6 | 46.5% [37.0, 56.2] | 68.7% [59.0, 77.0] | +22.2 points |
| GPT-5.4 | 45.5% [36.0, 55.2] | 68.7% [59.0, 77.0] | +23.2 points |

- Every gain is significant (paired exact McNemar test, p ≤ 0.0015).
- The differences *between models* are not significant, with or without the document (p ≥ 0.42 without, p ≥ 0.79 with).
- The blog's point: **the business context mattered more than the choice of model.** The three models were indistinguishable; the document lifted all of them by about 20 points.
- The blog presents the document as about an afternoon of an analyst's work.

## Reading it critically

- **Conflict of interest.** Cube sells a semantic layer, and the blog author is its VP of Product. The result favours their product category. No funding or conflict statement was visible in the blog post.
- **Statistical tests use n = 99**, not 100; the blog does not say why.
- **The title says "hallucination"**, but neither the blog nor the abstract gives a definition or a hallucination rate; that is in the paper's full text, which these notes do not cover.
- **How answers were judged** is not described in the blog ("the judge" is not specified).
- Even with the document, about a third of the answers were wrong. Business context is necessary, not sufficient; the dbt benchmark's query-engine approach did better on questions it could express.

## Connection to the guide

| Cube benchmark | Guide |
| --- | --- |
| A short document of measures and conventions, pasted into the prompt | The metric documents in `DOCS`; Section 1.4: "with a handful of metrics, put them directly in the system prompt" |
| Context mattered more than the model | Section 1.4: the business-specific layer is the onboarding, and it is your work, not the vendor's |
| About a third still wrong | Section 4.3: why the guide adds `check_metric_sql`, and why a semantic layer engine beats a document |

## Takeaways for a BI agent

1. Before comparing models, write the 4 KB document: definitions, conventions, ambiguous terms. It is the cheapest large gain on record here.
2. Do not stop there: a document only informs the model; a semantic-layer engine or checks like `check_metric_sql` *constrain* it.
3. Use a paired design for your own evaluation: every question with and without a change, so that small question sets still give clear answers.
