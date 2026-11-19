"""Checks the retrieval chapters (5 and 6) of README.md: chunking, embeddings, BM25, RRF, IVF, hybrid search."""

import re

import numpy as np
import pytest

from bi_warehouse import DOCS
from rag import Retriever, chunk_words, format_context
from vector_search import (BM25, FlatIndex, HashingEmbedder, IVFIndex, recall_at_k,
                           reciprocal_rank_fusion)


def ids(chunks):
    return [c.doc_id for c in chunks]


@pytest.fixture(scope="module")
def retriever():
    r = Retriever()
    r.ingest(DOCS)
    return r


def test_chunk_overlap():                      # Section 5.2
    assert chunk_words("a b c d e f g", size=3, overlap=1) == ["a b c", "c d e", "e f g"]
    assert chunk_words("a b", size=3, overlap=1) == ["a b"]
    with pytest.raises(ValueError):
        chunk_words("a b c", size=3, overlap=3)


def test_embedding_is_unit_and_deterministic():  # Section 5.3
    e = HashingEmbedder()
    v = e.embed("net revenue by region")
    assert np.linalg.norm(v) == pytest.approx(1.0)
    assert np.array_equal(v, HashingEmbedder().embed("net revenue by region"))


def test_cosine_sees_words_not_meaning():      # Section 5.3
    e = HashingEmbedder()
    a, b, c = e.embed("net revenue by region"), e.embed("revenue by region"), e.embed("sales by region")
    assert float(a @ b) == pytest.approx(0.775, abs=1e-3)
    assert float(a @ c) == pytest.approx(0.258, abs=1e-3)


def test_bm25_finds_alias():                   # Section 5.4
    bm25 = BM25({d["id"]: d["text"] for d in DOCS})
    hits = bm25.search("refund rate", 3)
    assert [h[0] for h in hits] == ["metric_refund_rate"]
    assert hits[0][1] == pytest.approx(4.767, abs=1e-3)


def test_rrf_worked_example():                 # Section 5.4
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "c", "d"]])
    assert [d for d, _ in fused] == ["b", "c", "a", "d"]
    assert fused[0][1] == pytest.approx(1 / 62 + 1 / 61)


@pytest.mark.parametrize("query, mode, expected", [   # Section 5.5 table
    ("net revenue by region", "dense", ["metric_revenue", "golden_revenue_by_region", "metric_aov"]),
    ("net revenue by region", "sparse", ["golden_revenue_by_region", "metric_revenue", "metric_aov"]),
    ("net revenue by region", "hybrid", ["golden_revenue_by_region", "metric_revenue", "metric_aov"]),
    ("basket size", "sparse", ["metric_aov"]),
    ("basket size", "hybrid", ["metric_aov", "table_fx_rates", "metric_revenue"]),
    ("which customers are active", "hybrid", ["metric_active_customers", "table_customers", "table_orders"]),
    ("amount_usd column", "hybrid", []),
])
def test_retrieval_table(retriever, query, mode, expected):
    assert ids(retriever.search(query, k=3, mode=mode)) == expected


def test_aliases_matter():                     # Section 5.5
    no_alias = [dict(d, text=re.sub(r"Aliases:[^.]*\.\s*", "", d["text"])) for d in DOCS]
    r = Retriever()
    r.ingest(no_alias)
    assert ids(r.search("basket size", k=2)) == ["table_fx_rates", "metric_revenue"]


def test_metadata_filter(retriever):           # Section 5.5
    hits = retriever.search("net revenue definition", k=3, kind="metric")
    assert ids(hits) == ["metric_revenue", "metric_aov"]   # nothing else scores above 0
    assert '<doc id="metric_revenue" kind="metric">' in format_context(hits)


def test_ivf_recall_vs_work():                 # Section 6.2
    rng = np.random.default_rng(42)
    centers = rng.normal(size=(20, 32))
    x = np.vstack([c + 0.35 * rng.normal(size=(100, 32)) for c in centers])
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    doc_ids = [str(i) for i in range(len(x))]
    flat = FlatIndex(32)
    flat.add(doc_ids, x)
    ivf = IVFIndex(x, doc_ids, n_lists=16, seed=0)
    queries = centers[rng.integers(0, 20, 50)] + 0.35 * rng.normal(size=(50, 32))
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)

    def measure(nprobe):
        recall = np.mean([recall_at_k(ivf.search(q, 10, nprobe), flat.search(q, 10)) for q in queries])
        scanned = np.mean([ivf.scanned_fraction(q, nprobe) for q in queries])
        return round(float(recall), 2), round(float(scanned), 3)

    assert measure(1) == (0.98, 0.074)
    assert measure(2) == (1.0, 0.131)
    assert measure(16) == (1.0, 1.0)
