# Sherlog — your build‑log whisperer

Sherlog is a tiny, local‑first CLI that reads noisy build or install logs and tells you exactly what to do.

- Sniffs the real error from long logs.
- Explains it with a local Small Language Model (Hugging Face) — or falls back to rule‑based hints.
- Prints copy‑paste fixes per OS.

## Install (with `uv`)

Sherlog uses a `pyproject.toml`, so you can install it cleanly with [uv](https://docs.astral.sh/uv/), which handles both dependency resolution and environment creation.

Minimal (rules only):
```bash
uv venv .venv
source .venv/bin/activate
uv pip install .
```

With local SLM support (CPU OK, GPU faster):
```bash
uv pip install ".[ml]"
```

## Usage

Pipe or pass a file:
```bash
uv pip install pyeda==0.29.0 2>&1 | sherlog --source pip --os debian
# or
sherlog examples/sample.log --model microsoft/phi-3-mini-4k-instruct --os ubuntu
```

## Models (local SLMs)

Pick any small instruct model. Solid options in 2025:
- Microsoft Phi‑3/3.5 Mini (3.8B)
- Qwen2.5‑1.5B/3B Instruct
- TinyLlama‑1.1B‑Chat
- Google Gemma‑2/3 small

For an overview and examples (e.g., Llama3.2‑1B, Qwen2.5‑1.5B, Phi‑3.5‑Mini, Gemma‑3/4B), see:
- Hugging Face SLM overview (Feb 22, 2025)【HF†L96-L109】
- DataCamp small‑model roundup (Nov 14, 2024)【DC†L103-L121】【DC†L196-L206】

## Roadmap
- VS Code panel that tails terminal output and renders Sherlog diagnosis.
- More detectors: rustc/maturin, CUDA/ROCm, Fortran (gfortran), pkg-config.
- `--format json` for CI annotations.

## License
MIT
