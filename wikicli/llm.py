"""The model: local Gemma through MLX (mlx-vlm), loaded once per CLI process.

Gemma only sees what the harness puts in `messages`: it does not read files,
remember past runs, or call tools on its own.
"""

import os
import resource
import sys
import time
import warnings
from dataclasses import dataclass

from . import config


class ModelUnavailable(RuntimeError):
    pass


@dataclass
class Generation:
    text: str
    seconds: float
    prompt_tokens: int
    output_tokens: int
    tokens_per_sec: float
    peak_memory_gb: float      # MLX peak (model weights + activations + KV cache)


_model = None


def _load():
    global _model
    if _model is not None:
        return _model
    warnings.filterwarnings("ignore")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    try:
        from mlx_vlm import load
        _model = load(config.LLM_MODEL)
    except Exception as e:  # missing weights offline, wrong id, unsupported chip...
        raise ModelUnavailable(
            f"Could not load local model '{config.LLM_MODEL}': {e}\n"
            "Download it once while online:  .venv/bin/python -m mlx_vlm.generate "
            f"--model {config.LLM_MODEL} --prompt hi --max-tokens 1"
        ) from e
    return _model


def generate(messages: list[dict], max_tokens: int, temperature: float = 0.0) -> Generation:
    """messages: [{"role": "system"|"user"|"assistant", "content": str}, ...]"""
    import mlx.core as mx
    from mlx_vlm import generate as mlx_generate
    from mlx_vlm.prompt_utils import apply_chat_template

    model, processor = _load()
    prompt = apply_chat_template(processor, model.config, messages)
    t0 = time.perf_counter()
    result = mlx_generate(model, processor, prompt, max_tokens=max_tokens,
                          temperature=temperature, verbose=False)
    seconds = time.perf_counter() - t0
    return Generation(
        text=result.text.strip(),
        seconds=round(seconds, 2),
        prompt_tokens=result.prompt_tokens,
        output_tokens=result.generation_tokens,
        tokens_per_sec=round(result.generation_tps, 1),
        peak_memory_gb=round(mx.get_peak_memory() / 1e9, 2),
    )


def process_rss_gb() -> float:
    """Peak resident memory of this whole process (Python + model + index)."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / (1e9 if sys.platform == "darwin" else 1e6), 2)


def model_identity() -> dict:
    import importlib.metadata as md
    return {
        "model": config.LLM_MODEL,
        "quantization": "4-bit (MLX)",
        "runtime": f"mlx-vlm {md.version('mlx-vlm')}, mlx {md.version('mlx')}",
        "embedding_model": config.EMBED_MODEL,
        "execution": "local",
    }
