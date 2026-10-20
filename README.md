# Learning notes

Personal study notes on math models, programming, data/ML engineering, algorithm practice and papers. Each topic lives in its own folder. New topics follow the template: notes written from first principles, a from-scratch implementation, and tests that check the code against the worked examples in the notes. Older course notes were copied in from their original repos as they were.

## Layout

```
.
├── math-models/                 statistical and mathematical models
│   └── hidden-markov-models/    HMM derivations + NumPy implementation
├── programming/                 languages and tools: sql, git, python, cpp, javascript, docker
├── data-engineering/            data engineering, PySpark, AWS / SageMaker ML
├── algorithms/                  leetcode notebooks (python) and SQL problems
├── papers/                      journal-club notes
├── _templates/                  template for new topics
└── requirements.txt
```

## Topics

| Area | Topic | Source | Status |
| --- | --- | --- | --- |
| Math models | [Hidden Markov Models](math-models/hidden-markov-models/) | own derivations | Complete |
| Programming | [SQL](programming/sql/) | Mosh course | Course notes |
| Programming | [Git](programming/git/) | DataCamp course | Course notes |
| Programming | [Python](programming/python/) | Mosh course | Course notes |
| Programming | [C++](programming/cpp/) | C++ Primer, Mosh course | Course notes |
| Programming | [JavaScript](programming/javascript/) | Udemy, Galvanize prep | Course notes |
| Programming | [Docker](programming/docker/) | Mosh course | Course notes |
| Data engineering | [Intro to data engineering](data-engineering/intro/) | Coursera | Course notes |
| Data engineering | [PySpark](data-engineering/pyspark/) | Udemy, Databricks | Course notes |
| Data engineering | [AWS and SageMaker ML](data-engineering/aws-ml/) | Udemy, Udacity | Course notes |
| Algorithms | [LeetCode](algorithms/leetcode/) | own solutions | Ongoing |
| Papers | [Journal club](papers/) | own notes | Ongoing |

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest                                   # run every topic's tests
python math-models/hidden-markov-models/hmm.py   # HMM demo
```

## Conventions

- One folder per topic, starting from [`_templates/topic-template.md`](_templates/topic-template.md).
- Math is written in GitHub-flavored Markdown: display formulas in ` ```math ` blocks; diagrams in ` ```mermaid ` blocks, or fixed-width text when the layout needs a grid mermaid cannot produce.
- Every worked example in the notes has a matching test, so the notes and the code cannot drift apart.
- Course slides, textbooks and paper PDFs are not committed. The original per-course repos keep them.
