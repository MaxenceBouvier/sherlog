<h1 align="center">Sherlog 🕵️‍♂️</h1>
<p align="center"><em>“It’s Sedimentary, My Dear Watson” of Logs</em></p>

<p align="center">
  <a href="LICENSE">
    <img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-blue.svg">
  </a>
  <a href="#">
    <img alt="Python >=3.13" src="https://img.shields.io/badge/python-%3E%3D3.13-blue">
  </a>
  <a href="https://docs.astral.sh/uv/concepts/tools/">
    <img alt="Packaging: uv tools" src="https://img.shields.io/badge/packaging-uv%20tools-8A2BE2">
  </a>
  <a href="#">
    <img alt="Tests: pytest" src="https://img.shields.io/badge/tests-pytest-green">
  </a>
  <a href="#">
    <img alt="Status: experimental" src="https://img.shields.io/badge/status-experimental-orange">
  </a>
</p>

---

**Sherlog** is a tiny, local‑first CLI that reads the many layers of noisy build and install logs and tells you exactly what to do 😄.  
Requires Python 3.13+ 🐍

- 🧐 Sniffs the real error from long logs  
- 🤖 Explains it with a local Small Language Model (Hugging Face) — or falls back to rule‑based hints  
- 🛠️ Prints copy‑paste fixes per OS  


## Install

Sherlog installs as a [uv tool](https://docs.astral.sh/uv/concepts/tools/): its own isolated env plus a small `sherlog` shim on your `PATH`.


### [Optional for SLM-based hints] Setup Hugging Face 

You'll probably need to instal the huggingface-cli to configure your Hugging Face token.

```bash 
uv tool install huggingface-cli
git config --global credential.helper store
hf auth login
# --> Follow the steps
```

### Option A — User‑local (recommended)

This avoids permission pitfalls and works across your shells/venvs.

#### Install uv locally [First Time Only]
```
# Linux/macOS (user-local)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Ensure ~/.local/bin is on PATH for this shell
export PATH="$HOME/.local/bin:$PATH"

# Verify
uv --version
```

#### Install sherlog

```bash
# Install to ~/.local (default uv tool dirs)
uv tool install --from . sherlog

# With ML extras (Transformers/Accelerate/Torch):
uv tool install './.[ml]'

# Ensure ~/.local/bin is in PATH (bash example):
export PATH="$HOME/.local/bin:$PATH"

# Verify
sherlog --help
```

### Option B — System‑wide (via `sudo`)

If you need a system‑wide install, set explicit locations and ensure the
installed env is world‑readable/executable.

#### Install uv globally [First Time Only]
```
curl -LsSf https://astral.sh/uv/install.sh | sudo env UV_INSTALL_DIR="/usr/local/bin" UV_NO_MODIFY_PATH=1 sh
```

#### Install Sherlog (system‑wide)
Sherlog is packaged with a `pyproject.toml`, so you can install it system‑wide using `uv tool install`.

```bash
# Install Sherlog globally (rules + pretty output):
sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
    uv tool install --from . sherlog

# Verify:
sherlog --help
```

#### Install with ML support (local SLMs)
1. To enable the ML step (Transformers, Accelerate, PyTorch), install the optional `ml` extra:

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

## Troubleshooting

- "bad interpreter: Permission denied" when running `sherlog`:
  - Cause: the system‑wide tool env (e.g. `/usr/local/share/uv/tools/sherlog`) was created by `sudo` and isn’t world‑executable (or lives on a `noexec` mount). The `sherlog` shim points to that Python via its shebang.
  - Quick checks:
    - `head -1 /usr/local/bin/sherlog` (see the shebang path)
    - `ls -ld /usr/local/share/uv /usr/local/share/uv/tools /usr/local/share/uv/tools/sherlog{,/bin}`
    - `ls -l /usr/local/share/uv/tools/sherlog/bin/python`
  - Fix (recommended): uninstall the root install and reinstall user‑local:
    ```bash
    sudo env UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
      uv tool uninstall sherlog
    uv tool install --from . sherlog   # or './.[ml]'
    export PATH="$HOME/.local/bin:$PATH"
    ```
  - Fix (keep global): ensure world read/execute on the tool env and parents:
    ```bash
    sudo chmod a+rx /usr/local/share/uv /usr/local/share/uv/tools
    sudo chmod -R a+rx /usr/local/share/uv/tools/sherlog
    ```
    If re‑installing globally, set a permissive umask: `sudo sh -c 'umask 022; \
      UV_TOOL_DIR=/usr/local/share/uv/tools UV_TOOL_BIN_DIR=/usr/local/bin \
      uv tool install --from . sherlog'`.


## Configuration

To specify where Hugging Face 🤗 stores the models weights on your machine, put that in your shell `rc` file, e.g. `~/.bashrc` or `~/.zshrc`:
```bash
HF_HOME=/path/to/models
```

## Contributing

Contributions welcome! If you’d like to add rules, improve the CLI, or enhance docs, we'd love your help 😊:

- Fork and create a feature branch.
- Add or update tests for behavior changes (`pytest`).
- Keep changes minimal and focused.
- Open a PR with a clear description and example logs if possible.

Local dev setup and tests:

```bash
uv python install 3.13  # one-time
uv run -p 3.13 --extra test -m pytest -q
```

## Tests (pytest)

Run tests locally with pytest. The simplest route is to ensure Python 3.13 is available and run:

```bash
uv run -p 3.13 --extra test -m pytest -q
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

Inspired by countless hours debugging build logs and by the excellent Huggging Face 🤗 based local SLM ecosystem 🙏

Happy debugging! 😄
