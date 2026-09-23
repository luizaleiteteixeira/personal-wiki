"""Paths, model identifiers and tunable settings for the wiki harness.

Everything the harness reads or writes is resolved from the repository root,
so the CLI works no matter which directory it is launched from.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Knowledge base (the Obsidian vault). Only human-readable Markdown lives here.
VAULT = ROOT / "vault"
RAW_DIR = VAULT / "raw"          # original sources, never modified by the harness
WIKI_DIR = VAULT / "wiki"        # generated + reviewed notes
INDEX_MD = VAULT / "index.md"    # human landing page

# Machine files live outside the vault.
INDEX_DIR = ROOT / "index"       # chunks, embeddings, manifest
RUNS_DIR = ROOT / "runs"         # saved evidence from ask / chat / search / ingest
PROMPTS_DIR = ROOT / "prompts"   # persona and research rules loaded per mode

# Local models (downloaded once while online, then read from the Hugging Face cache).
LLM_MODEL = os.environ.get("WIKI_LLM", "mlx-community/gemma-4-e4b-it-4bit")
EMBED_MODEL = os.environ.get("WIKI_EMBED", "mlx-community/all-MiniLM-L6-v2-4bit")

# Chunking: passages returned by search and passed to Gemma as evidence.
CHUNK_CHARS = 900          # target passage size
CHUNK_MIN_CHARS = 120      # smaller trailing pieces are merged into the previous chunk

# Retrieval.
TOP_K_ASK = 6              # passages passed to Gemma in ask mode
TOP_K_CHAT = 4             # passages passed to Gemma when chat decides to retrieve
TOP_K_SEARCH = 5           # passages shown by search
RRF_K = 60                 # reciprocal-rank-fusion constant for BM25 + embeddings
CHAT_RETRIEVE_MIN_SIM = 0.40   # chat looks up notes only if the best passage is at least this similar

# Generation.
MAX_TOKENS_ASK = 450
MAX_TOKENS_CHAT = 600
MAX_TOKENS_INGEST = 600
CHAT_HISTORY_TURNS = 6     # user+assistant pairs kept as conversation context

# Wiki note generation.
NOTE_SECTION_MAX_CHARS = 6000   # longer sections are truncated before being sent to Gemma
NOTE_MERGE_SIM = 0.86           # new notes whose title is this similar to an existing one are merged directly
MERGE_CANDIDATE_SIM = 0.70      # same-course note pairs above this (title + summary) are checked by Gemma
RELATED_NOTES = 3               # related-note links per page
RELATED_MIN_SIM = 0.38
