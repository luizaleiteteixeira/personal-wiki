"""The retrieval tool: a local index of original passages, searched two ways.

* BM25 keyword scoring (pure Python, no model needed)
* cosine similarity of MiniLM embeddings (small local embedding model)

The two rankings are combined with reciprocal rank fusion (RRF), so a passage
that matches the words *or* the meaning of the query can surface. Every hit
keeps its source path, section and PDF page so answers can be cited.
"""

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass

import numpy as np

from . import config
from .sources import Section, page_at


@dataclass
class Chunk:
    chunk_id: str
    source_id: str
    path: str
    course: str
    section: str
    page: int | None
    text: str

    def location(self) -> str:
        loc = f"{self.path} › {self.section}"
        return loc + (f" › p.{self.page}" if self.page else "")


@dataclass
class Hit:
    chunk: Chunk
    score: float        # fused RRF score (for ranking)
    cosine: float       # semantic similarity, 0-1 (used for "is this relevant at all?")
    bm25: float


# ---------------------------------------------------------------- chunking

def chunk_section(section: Section) -> list[Chunk]:
    """Pack whole lines into ~CHUNK_CHARS passages so bullets and formulas are not cut."""
    chunks, buf, start, pos = [], [], 0, 0
    for line in section.text.splitlines(keepends=True):
        if buf and sum(map(len, buf)) + len(line) > config.CHUNK_CHARS:
            chunks.append(("".join(buf), start))
            buf, start = [], pos
        buf.append(line)
        pos += len(line)
    if buf:
        text = "".join(buf)
        if chunks and len(text) < config.CHUNK_MIN_CHARS:
            prev, s = chunks.pop()
            chunks.append((prev + text, s))
        else:
            chunks.append((text, start))
    out = []
    for i, (text, offset) in enumerate(chunks):
        if not text.strip():
            continue
        out.append(Chunk(
            chunk_id=f"{section.section_id}:{i}",
            source_id=section.source_id,
            path=section.path,
            course=section.course,
            section=section.title,
            page=page_at(section, offset),
            text=text.strip(),
        ))
    return out


# ---------------------------------------------------------------- BM25

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set("""a an and are as at be but by can did do does for from had has have how i if in into is it
its me my of on or our so that the their them then there these they this to was we were what when where
which who why will with you your about""".split())


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 1]


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1, self.b = k1, b
        self.docs = [Counter(d) for d in docs]
        self.lens = [len(d) for d in docs]
        self.avg = sum(self.lens) / max(1, len(self.lens))
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: list[str]) -> np.ndarray:
        out = np.zeros(len(self.docs))
        for i, (tf, ln) in enumerate(zip(self.docs, self.lens)):
            s = 0.0
            for t in query:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * ln / self.avg))
            out[i] = s
        return out


# ---------------------------------------------------------------- embeddings

class Embedder:
    """Lazy wrapper around the local MiniLM model (mlx-embeddings)."""

    _model = None

    @classmethod
    def encode(cls, texts: list[str], batch: int = 32) -> np.ndarray:
        import mlx_embeddings
        from mlx_embeddings.utils import load

        if cls._model is None:
            cls._model = load(config.EMBED_MODEL)
        model, tok = cls._model
        vecs = []
        for i in range(0, len(texts), batch):
            out = mlx_embeddings.generate(model, tok, texts=texts[i:i + batch], max_length=256)
            vecs.append(np.array(out.text_embeds, dtype=np.float32))
        v = np.concatenate(vecs) if vecs else np.zeros((0, 384), dtype=np.float32)
        return v / np.clip(np.linalg.norm(v, axis=1, keepdims=True), 1e-9, None)


def embed_text(chunk: Chunk) -> str:
    # Section context helps short bullet passages match questions about their topic.
    return f"{chunk.course} — {chunk.section}: {chunk.text}"


# ---------------------------------------------------------------- index on disk

CHUNKS_FILE = config.INDEX_DIR / "chunks.jsonl"
VECTORS_FILE = config.INDEX_DIR / "embeddings.npy"


class Index:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray | None):
        self.chunks = chunks
        self.vectors = vectors
        self.bm25 = BM25([tokenize(f"{c.section} {c.text}") for c in chunks])

    # -- persistence
    @staticmethod
    def exists() -> bool:
        return CHUNKS_FILE.exists()

    @classmethod
    def load(cls, with_vectors: bool = True) -> "Index":
        if not CHUNKS_FILE.exists():
            raise FileNotFoundError("No index found. Run `wiki ingest` first.")
        chunks = [Chunk(**json.loads(l)) for l in CHUNKS_FILE.read_text().splitlines() if l.strip()]
        vectors = np.load(VECTORS_FILE) if with_vectors and VECTORS_FILE.exists() else None
        return cls(chunks, vectors)

    def save(self):
        config.INDEX_DIR.mkdir(exist_ok=True)
        CHUNKS_FILE.write_text("".join(json.dumps(asdict(c), ensure_ascii=False) + "\n" for c in self.chunks))
        if self.vectors is not None:
            np.save(VECTORS_FILE, self.vectors)

    @classmethod
    def build(cls, chunks: list[Chunk]) -> "Index":
        vectors = Embedder.encode([embed_text(c) for c in chunks])
        return cls(chunks, vectors)

    def replace_sources(self, source_ids: set[str], new_chunks: list[Chunk]) -> "Index":
        """Re-ingesting a source swaps its chunks instead of appending duplicates."""
        keep = [i for i, c in enumerate(self.chunks) if c.source_id not in source_ids]
        kept_chunks = [self.chunks[i] for i in keep]
        new_vecs = Embedder.encode([embed_text(c) for c in new_chunks])
        old_vecs = self.vectors[keep] if self.vectors is not None else Embedder.encode(
            [embed_text(c) for c in kept_chunks])
        return Index(kept_chunks + new_chunks, np.concatenate([old_vecs, new_vecs]))

    # -- search
    def search(self, query: str, k: int, keyword_only: bool = False) -> list[Hit]:
        bm = self.bm25.scores(tokenize(query))
        if keyword_only or self.vectors is None:
            order = [i for i in np.argsort(-bm) if bm[i] > 0][:k]
            return [Hit(self.chunks[i], float(bm[i]), 0.0, float(bm[i])) for i in order]

        q = Embedder.encode([query])[0]
        cos = self.vectors @ q
        rank_bm = {i: r for r, i in enumerate(np.argsort(-bm)) if bm[i] > 0}
        rank_cos = {i: r for r, i in enumerate(np.argsort(-cos))}
        fused = {}
        for i in range(len(self.chunks)):
            s = 1.0 / (config.RRF_K + rank_cos[i])
            if i in rank_bm:
                s += 1.0 / (config.RRF_K + rank_bm[i])
            fused[i] = s
        order = sorted(fused, key=fused.get, reverse=True)[:k]
        return [Hit(self.chunks[i], fused[i], float(cos[i]), float(bm[i])) for i in order]
