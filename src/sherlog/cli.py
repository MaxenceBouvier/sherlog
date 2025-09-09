
from __future__ import annotations

import argparse, os, sys
from typing import Optional, List

from .rules import apply_rules, extract_failure_window, Finding

# Optional rich pretty print
try:
    from rich.console import Console
    from rich.panel import Panel
except Exception:
    Console = None
    Panel = None

HF_AVAILABLE = True
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
except Exception:
    HF_AVAILABLE = False

SYSTEM_PROMPT = "You are a senior build & packaging engineer.\n" \
"Given a noisy build log snippet, diagnose the most likely root cause\n" \
"and propose concrete shell commands to fix it.\n\n" \
"Format your answer in four short sections:\n" \
"1) Root cause — one sentence.\n" \
"2) One-line fix — the most likely single command for the user's OS.\n" \
"3) Why this happens — 2–4 bullet points.\n" \
"4) If it persists — short next steps.\n\n" \
"Be precise, avoid guessy filler, and prioritize actionable steps.\n"

def make_user_prompt(snippet: str, os_hint: str, source: Optional[str], findings: List[Finding]) -> str:
    rule_hints = ""
    if findings:
        rule_hints = "Detected patterns:\n" + "\n".join(
            [f"- {f.rule}: {f.reason} (suggested fix: {f.fix})" for f in findings]
        )
    src = source or "unknown"
    return (
        f"OS: {os_hint}\n"
        f"Tool/source: {src}\n"
        "Log snippet:\n---\n"
        f"{snippet}\n---\n"
        f"{rule_hints}\n"
        "Now produce the 4-section answer.\n"
    )

def run_llm(snippet: str, os_hint: str, source: Optional[str], model_id: str, findings: List[Finding]) -> str:
    if not HF_AVAILABLE:
        return "(Transformers not installed) Using rule-based hints only.\n" + rules_only_text(findings)
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    mdl = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True, device_map="auto")
    pipe = pipeline("text-generation", model=mdl, tokenizer=tok)
    prompt = f"<|system|>\n{SYSTEM_PROMPT}\n<|user|>\n{make_user_prompt(snippet, os_hint, source, findings)}\n<|assistant|>\n"
    out = pipe(prompt, max_new_tokens=450, do_sample=False, temperature=0.0)[0]["generated_text"]
    if "<|assistant|>" in out:
        out = out.split("<|assistant|>")[-1].strip()
    return out.strip()

def rules_only_text(findings: List[Finding]) -> str:
    if not findings:
        return "No known patterns matched. Consider installing a compiler and Python headers, or use a supported Python version."
    lines = []
    for f in findings:
        lines.append(f"- {f.rule}\n  Reason: {f.reason}\n  Fix: {f.fix}")
    return "Rule-based suggestions:\n" + "\n".join(lines)

def print_result(header: str, body: str):
    if Console and Panel:
        Console().print(Panel.fit(body, title=header))
    else:
        print(f"== {header} ==")
        print(body)

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="sherlog", description="Sherlog — your build-log whisperer")
    ap.add_argument("logfile", nargs="?", help="Path to a log file (or omit to read stdin)")
    ap.add_argument("--model", default=os.environ.get("SHERLOG_MODEL", "microsoft/phi-3-mini-4k-instruct"), help="HF model id to use locally")
    ap.add_argument("--no-ml", action="store_true", help="Disable ML step and only use rules")
    ap.add_argument("--os", default=os.environ.get("SHERLOG_OS", "debian"),
                    choices=["debian","ubuntu","arch","fedora","rhel","alpine","mac","windows","other"],
                    help="OS hint for actionable commands")
    ap.add_argument("--source", default=None, help="Tool generating logs (pip/uv/poetry/conda/cmake/make/ninja)")
    ap.add_argument("--window", type=int, default=60, help="Context lines window")
    args = ap.parse_args(argv)

    if args.logfile and args.logfile != "-":
        with open(args.logfile, "r", errors="ignore") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("No input detected. Pipe logs or pass a file.", file=sys.stderr)
        return 2

    snippet = extract_failure_window(text, window=args.window)
    findings = apply_rules(snippet, args.os)

    if args.no-ml:
        out = rules_only_text(findings)
    else:
        try:
            out = run_llm(snippet, args.os, args.source, args.model, findings)
        except Exception as e:
            out = f"(ML step failed: {e})\n" + rules_only_text(findings)

    print_result("Sherlog Diagnosis", out)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
