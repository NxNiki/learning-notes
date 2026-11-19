"""Embeddings, a vector index (exact and IVF), BM25 and rank fusion, from scratch.

Real systems use a learned embedding model (a neural network that maps text
with similar meaning to nearby vectors) and a vector database. Here the
embedding is feature hashing, which needs no model and is deterministic, so
every number in the guide can be checked by a test. The index code is the
same whatever produced the vectors.
"""

import hashlib
import math
import re
from collections import Counter

import numpy as np

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "is",
    "it", "of", "on", "or", "the", "to", "was", "what", "with", "we", "our",
    "how", "much", "did", "do", "does", "per", "each", "me", "show",
}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9_]+", text.lower()) if t not in STOPWORDS]


def _hash(feature: str) -> int:
    # md5 rather than hash(): Python salts hash() per process, and an index
    # built in one process must be searchable from another.
    return int.from_bytes(hashlib.md5(feature.encode()).digest()[:8], "little")


class HashingEmbedder:
    """Maps text to a unit vector by hashing its words and word pairs.

    Each feature (a word, or two adjacent words) is hashed to one of `dim`
    positions and adds +1 or -1 there (the sign comes from another bit of the
    hash, so collisions tend to cancel instead of pile up). The vector is then
    scaled to length 1, so the dot product of two vectors is their cosine
    similarity.

    Texts that share words get similar vectors; texts that mean the same thing
    in different words do not. That is the gap a learned embedding model closes.
    """

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, text: str) -> np.ndarray:
        tokens = tokenize(text)
        features = tokens + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
        v = np.zeros(self.dim)
        for f in features:
            h = _hash(f)
            v[h % self.dim] += 1.0 if (h >> 32) & 1 else -1.0
        norm = np.linalg.norm(v)
        return v / norm if norm else v

    def embed_many(self, texts: list[str]) -> np.ndarray:
        return np.vstack([self.embed(t) for t in texts])


class FlatIndex:
    """Exact nearest-neighbour search: compare the query with every vector.

    Cost is O(n * dim) per query. That is fine up to about a million vectors
    on one machine, and it is the ground truth that approximate indexes are
    measured against.
    """

    def __init__(self, dim: int):
        self.vectors = np.empty((0, dim))
        self.ids: list[str] = []
        self.meta: list[dict] = []

    def add(self, ids: list[str], vectors: np.ndarray, meta: list[dict] | None = None):
        if len(ids) != len(vectors):
            raise ValueError(f"{len(ids)} ids but {len(vectors)} vectors")
        self.vectors = np.vstack([self.vectors, vectors])
        self.ids += ids
        self.meta += meta if meta is not None else [{} for _ in ids]

    def search(self, query: np.ndarray, k: int, where: dict | None = None) -> list[tuple[str, float]]:
        """Top-k (id, cosine score). `where` filters on metadata before ranking."""
        scores = self.vectors @ query
        candidates = [
            i for i in range(len(self.ids))
            if not where or all(self.meta[i].get(key) == val for key, val in where.items())
        ]
        best = sorted(candidates, key=lambda i: -scores[i])[:k]
        return [(self.ids[i], float(scores[i])) for i in best]


def kmeans(x: np.ndarray, k: int, iters: int = 20, seed: int = 0) -> np.ndarray:
    """Plain k-means on unit vectors (spherical: centroids are re-normalized)."""
    rng = np.random.default_rng(seed)
    centroids = x[rng.choice(len(x), size=k, replace=False)].copy()
    for _ in range(iters):
        assign = np.argmax(x @ centroids.T, axis=1)
        for c in range(k):
            members = x[assign == c]
            if len(members):
                centroid = members.mean(axis=0)
                centroids[c] = centroid / np.linalg.norm(centroid)
    return centroids


class IVFIndex:
    """Inverted-file index, the simplest approximate nearest-neighbour index.

    Build: cluster the vectors with k-means into `n_lists` cells and keep, for
    each cell, the list of vectors assigned to it.
    Search: find the `nprobe` cells whose centroids are closest to the query
    and compare the query only with the vectors in those cells.

    With nprobe = n_lists it is exact; with nprobe = 1 it scans about
    1/n_lists of the data but can miss a neighbour that sits just across a
    cell boundary. nprobe is the recall-versus-speed dial that every vector
    database exposes under some name (nprobe in IVF, ef_search in HNSW).
    """

    def __init__(self, vectors: np.ndarray, ids: list[str], n_lists: int, seed: int = 0):
        self.vectors = vectors
        self.ids = ids
        self.centroids = kmeans(vectors, n_lists, seed=seed)
        assign = np.argmax(vectors @ self.centroids.T, axis=1)
        self.lists = [np.flatnonzero(assign == c) for c in range(n_lists)]

    def search(self, query: np.ndarray, k: int, nprobe: int) -> list[tuple[str, float]]:
        cells = np.argsort(-(self.centroids @ query))[:nprobe]
        candidates = np.concatenate([self.lists[c] for c in cells])
        scores = self.vectors[candidates] @ query
        order = np.argsort(-scores)[:k]
        return [(self.ids[candidates[i]], float(scores[i])) for i in order]

    def scanned_fraction(self, query: np.ndarray, nprobe: int) -> float:
        cells = np.argsort(-(self.centroids @ query))[:nprobe]
        return sum(len(self.lists[c]) for c in cells) / len(self.ids)


def recall_at_k(approx: list[tuple[str, float]], exact: list[tuple[str, float]]) -> float:
    """Fraction of the true top-k that the approximate search found."""
    truth = {i for i, _ in exact}
    return len(truth & {i for i, _ in approx}) / len(truth)


class BM25:
    """Keyword ranking (Okapi BM25), the classic search-engine score.

    A document scores high when it contains the query's rare words (high IDF)
    several times (TF, with diminishing returns set by k1) and is not unusually
    long (length normalization, set by b). It finds exact identifiers such as
    column names and error codes, which embeddings tend to blur.
    """

    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.tf = {doc_id: Counter(tokenize(text)) for doc_id, text in docs.items()}
        self.length = {doc_id: sum(tf.values()) for doc_id, tf in self.tf.items()}
        self.avg_length = sum(self.length.values()) / len(docs)
        n = len(docs)
        df = Counter(term for tf in self.tf.values() for term in tf)
        self.idf = {t: math.log(1 + (n - d + 0.5) / (d + 0.5)) for t, d in df.items()}

    def score(self, query: str, doc_id: str) -> float:
        tf, length = self.tf[doc_id], self.length[doc_id]
        total = 0.0
        for term in tokenize(query):
            if term not in tf:
                continue
            f = tf[term]
            norm = f + self.k1 * (1 - self.b + self.b * length / self.avg_length)
            total += self.idf[term] * f * (self.k1 + 1) / norm
        return total

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        scored = [(doc_id, self.score(query, doc_id)) for doc_id in self.tf]
        scored = [s for s in scored if s[1] > 0]
        return sorted(scored, key=lambda s: -s[1])[:k]


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Merge several ranked lists: score(d) = sum over lists of 1 / (k + rank).

    Only ranks are used, never raw scores, so a cosine similarity and a BM25
    score (which live on different scales) can be combined without tuning.
    k = 60 is the constant from the original paper (Cormack et al., 2009).
    """
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda s: (-s[1], s[0]))
