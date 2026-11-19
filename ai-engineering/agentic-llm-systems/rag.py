"""Retrieval-augmented generation: chunk, index, retrieve, build the prompt context.

RAG answers "how does the model know our metric definitions?" without
training: at question time, search a knowledge base and paste the best
passages into the prompt, with their ids so the answer can cite them.
"""

from dataclasses import dataclass, field

from vector_search import BM25, FlatIndex, HashingEmbedder, reciprocal_rank_fusion


def chunk_words(text: str, size: int, overlap: int) -> list[str]:
    """Split text into windows of `size` words, each sharing `overlap` words with the previous.

    The overlap keeps a sentence that straddles a boundary whole in at least
    one chunk. Real pipelines split on structure first (headings, paragraphs,
    one chunk per metric or table) and fall back to windows for long sections.
    """
    if not 0 <= overlap < size:
        raise ValueError(f"need 0 <= overlap < size, got overlap={overlap}, size={size}")
    words = text.split()
    if len(words) <= size:
        return [" ".join(words)] if words else []
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + size]))
        if start + size >= len(words):
            break
    return chunks


@dataclass
class Chunk:
    id: str          # "<doc id>#<n>"
    doc_id: str
    kind: str
    text: str


@dataclass
class Retriever:
    """Hybrid retrieval: vector search and BM25, merged with reciprocal rank fusion."""

    embedder: HashingEmbedder = field(default_factory=HashingEmbedder)
    chunk_size: int = 60
    chunk_overlap: int = 10
    # Vector search always returns k results, even when nothing is related.
    # Dense hits scoring at or below this cosine are dropped (0.0 = no shared feature).
    min_score: float = 0.0

    def __post_init__(self):
        self.chunks: dict[str, Chunk] = {}
        self.index = FlatIndex(self.embedder.dim)
        self.bm25: BM25 | None = None

    def ingest(self, docs: list[dict]) -> None:
        """Chunk, embed and index documents of the form {"id", "kind", "text"}."""
        new = []
        for doc in docs:
            for n, text in enumerate(chunk_words(doc["text"], self.chunk_size, self.chunk_overlap)):
                new.append(Chunk(f"{doc['id']}#{n}", doc["id"], doc["kind"], text))
        for c in new:
            if c.id in self.chunks:
                raise ValueError(f"duplicate chunk id {c.id}")
            self.chunks[c.id] = c
        self.index.add(
            [c.id for c in new],
            self.embedder.embed_many([c.text for c in new]),
            [{"kind": c.kind} for c in new],
        )
        # BM25 statistics (IDF, average length) depend on the whole corpus, so rebuild.
        self.bm25 = BM25({c.id: c.text for c in self.chunks.values()})

    def search(self, query: str, k: int = 3, kind: str | None = None,
               mode: str = "hybrid") -> list[Chunk]:
        if self.bm25 is None:
            raise RuntimeError("search() before ingest(): the index is empty")
        where = {"kind": kind} if kind else None
        pool = 4 * k   # fetch more than k from each ranker, then fuse
        dense = [cid for cid, score in self.index.search(self.embedder.embed(query), pool, where)
                 if score > self.min_score]
        sparse = [cid for cid, _ in self.bm25.search(query, len(self.chunks))
                  if not kind or self.chunks[cid].kind == kind][:pool]
        if mode == "dense":
            ranked = dense
        elif mode == "sparse":
            ranked = sparse
        elif mode == "hybrid":
            ranked = [cid for cid, _ in reciprocal_rank_fusion([dense, sparse])]
        else:
            raise ValueError(f"mode must be dense, sparse or hybrid, got {mode!r}")
        return [self.chunks[cid] for cid in ranked[:k]]


def format_context(chunks: list[Chunk]) -> str:
    """Retrieved passages as prompt text, each tagged with its source id for citations."""
    return "\n\n".join(f'<doc id="{c.doc_id}" kind="{c.kind}">\n{c.text}\n</doc>' for c in chunks)
