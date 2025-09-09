# Sherlog — your build‑log whisperer

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python >=3.9](https://img.shields.io/badge/python-%3E%3D3.9-blue)](#)
[![Packaging: uv tools](https://img.shields.io/badge/packaging-uv%20tools-8A2BE2)](https://docs.astral.sh/uv/concepts/tools/)
[![Tests: pytest](https://img.shields.io/badge/tests-pytest-green)](#)
[![Status: experimental](https://img.shields.io/badge/status-experimental-orange)](#)

Sherlog is a tiny, local‑first CLI that reads noisy build or install logs and tells you exactly what to do.

- Sniffs the real error from long logs.
- Explains it with a local Small Language Model (Hugging Face) — or falls back to rule‑based hints.
- Prints copy‑paste fixes per OS.

## Install (global via `uv`)

Sherlog installs as a global “tool” using [uv](https://docs.astral.sh/uv/), keeping its dependencies isolated while placing a `sherlog` executable on your `PATH`.

### Install uv globally [First Time Only]
```
curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/usr/local/bin" UV_NO_MODIFY_PATH=1 sh
```


### Install Sherlog
Sherlog is packaged with a `pyproject.toml`, so you can install it system‑wide using `uv tool install`.

```bash
# Install Sherlog globally (rules + pretty output):
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool install --from . sherlog

# Verify:
sherlog --help
````

#### Install with ML support (local SLMs)
To enable the ML step (Transformers, Accelerate, PyTorch), install the optional `ml` extra:

```bash
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool install './.[ml]'

# Example (uses a local small model):
echo "error: command 'cc' failed: No such file or directory" | \
  sherlog --os ubuntu --model microsoft/phi-3-mini-4k-instruct
```

To upgrade later:

```bash
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool upgrade sherlog
```

For ML installs, upgrade with one of:

```bash
# If installed from this repo (local path)
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool upgrade './.[ml]'

# If installed from PyPI with extras
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool upgrade sherlog  # preserves original extras
```

To uninstall:

```bash
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool uninstall sherlog
```

> `UV_TOOL_DIR` sets where Sherlog’s isolated environment lives; `UV_TOOL_BIN_DIR` (like `/usr/local/bin`) is where the CLI link is placed. ([Astral uv docs](https://docs.astral.sh/uv/concepts/tools))
> If `UV_TOOL_BIN_DIR` isn’t in your `PATH`, `uv tool update-shell` can help add it.

## Usage

Pipe or pass a file as usual:

```bash
uv pip install pyeda==0.29.0 2>&1 | sherlog --source pip --os debian
# or
sherlog examples/sample.log --model microsoft/phi-3-mini-4k-instruct --os ubuntu
```

## Contributing

Contributions welcome! If you’d like to add rules, improve the CLI, or enhance docs:

- Fork and create a feature branch.
- Add or update tests for behavior changes (`pytest`).
- Keep changes minimal and focused.
- Open a PR with a clear description and example logs if possible.

Local dev setup and tests:

```bash
uv pip install -e '.[test]'
uv run -m pytest -q
```

## Tests (pytest)

Run tests locally with pytest. The simplest route is to install the project in editable mode with the `test` extra and then run pytest via `uv`:

```bash
uv pip install -e '.[test]'
uv run -m pytest -q
```

## Models (local SLMs)

Pick any small instruct model — examples in 2025:

* Microsoft Phi‑3/3.5 Mini (3.8 B params)
* Qwen2.5‑1.5 B / 3 B Instruct
* TinyLlama‑1.1 B‑Chat
* Google Gemma‑2 / 3 small

See Hugging Face’s [SLM overview](https://huggingface.co/blog/jjokah/small-language-model) for an updated list.

## Roadmap

* VS Code panel that tails terminal logs and renders Sherlog diagnosis.
* Add detectors for `rustc/maturin`, CUDA/ROCm, Fortran (`gfortran`), `pkg-config`.
* Add a `--format json` option for CI integration.

## Author

- Maxence Bouvier — maxence.bouvier.pro@gmail.com

## Thanks

Inspired by countless hours debugging build logs and by the excellent local SLM ecosystem.

## License

MIT
