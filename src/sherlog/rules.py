
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List

ERROR_MARKERS = [
    r"error:", r"fatal error:", r"undefined reference", r"collect2: error",
    r"FAILED:", r"Build failed", r"Traceback (most recent call last):",
    r"Exit status: 1", r"ninja: build stopped", r"gmake: \*\*\* \[", r"make: \*\*\* \[",
    r"command 'cc' failed", r"gcc: error", r"clang: error", r"ld: error", r"linker command failed",
    r"ModuleNotFoundError", r"ImportError", r"CalledProcessError", r"ResolutionImpossible",
    r"error: subprocess-exited-with-error", r"ERROR:",
]

RULES = [
    {
        "name": "Missing C compiler",
        "pattern": re.compile(r"(command 'cc' failed|gcc: command not found|clang: command not found|No such file or directory.*\bcc\b)", re.I),
        "explain": "Your environment lacks a C compiler, but this package builds a native extension.",
        "fix_by_os": {
            "debian": "sudo apt-get update && sudo apt-get install -y build-essential gcc g++ make",
            "ubuntu": "sudo apt-get update && sudo apt-get install -y build-essential gcc g++ make",
            "arch": "sudo pacman -S --needed base-devel",
            "fedora": "sudo dnf groupinstall -y \"Development Tools\" && sudo dnf install -y gcc gcc-c++ make",
            "rhel": "sudo yum groupinstall -y \"Development Tools\" && sudo yum install -y gcc gcc-c++ make",
            "alpine": "sudo apk add --no-cache build-base",
            "mac": "xcode-select --install  # then: brew install gcc",
            "windows": "Install Microsoft C++ Build Tools (vs_BuildTools) or mingw-w64.",
            "default": "Install a C/C++ toolchain (gcc/clang, make).",
        }
    },
    {
        "name": "Missing Python headers",
        "pattern": re.compile(r"fatal error: Python\.h: No such file or directory", re.I),
        "explain": "Python dev headers are required to build C-extensions.",
        "fix_by_os": {
            "debian": "sudo apt-get install -y python3-dev",
            "ubuntu": "sudo apt-get install -y python3-dev",
            "arch": "sudo pacman -S --needed python",
            "fedora": "sudo dnf install -y python3-devel",
            "rhel": "sudo yum install -y python3-devel",
            "alpine": "sudo apk add --no-cache python3-dev",
            "mac": "brew install python",
            "windows": "Install Python from python.org and ensure headers are included.",
            "default": "Install your distro's Python development headers.",
        }
    },
    {
        "name": "Unsupported Python version for wheel",
        "pattern": re.compile(r"(Unsupported.*python|Requires-Python|No matching distribution found.*cp3\d+|python 3\.1[3-9])", re.I),
        "explain": "Package may not publish wheels for your Python version; building from source may fail.",
        "fix_generic": "Try Python 3.10–3.12 in a fresh virtual environment, or check if the project publishes 3.13 wheels.",
    },
    {
        "name": "Missing system lib (e.g., libffi, openssl)",
        "pattern": re.compile(r"(fatal error: .*\.h: No such file or directory)|(cannot find -l[a-zA-Z0-9_]+)", re.I),
        "explain": "A required system library or header is missing during compilation/linking.",
        "fix_generic": "Install the corresponding *-dev package (e.g., libffi-dev, openssl-devel) for your distro.",
    },
    {
        "name": "pkg-config missing",
        "pattern": re.compile(r"(pkg-config: command not found|No package '.*' found)", re.I),
        "explain": "pkg-config is needed to discover system library flags.",
        "fix_by_os": {
            "debian": "sudo apt-get install -y pkg-config",
            "ubuntu": "sudo apt-get install -y pkg-config",
            "arch": "sudo pacman -S --needed pkgconf",
            "fedora": "sudo dnf install -y pkgconfig",
            "rhel": "sudo yum install -y pkgconfig",
            "alpine": "sudo apk add --no-cache pkgconf",
            "mac": "brew install pkg-config",
            "windows": "Install pkg-config via MSYS2 or vcpkg as appropriate.",
            "default": "Install pkg-config for your OS.",
        }
    },
    {
        "name": "CMake not found",
        "pattern": re.compile(r"(CMake Error:|cmake: command not found)", re.I),
        "explain": "Project uses CMake but it's not installed or failed to configure.",
        "fix_by_os": {
            "debian": "sudo apt-get install -y cmake",
            "ubuntu": "sudo apt-get install -y cmake",
            "arch": "sudo pacman -S --needed cmake",
            "fedora": "sudo dnf install -y cmake",
            "rhel": "sudo yum install -y cmake",
            "alpine": "sudo apk add --no-cache cmake",
            "mac": "brew install cmake",
            "windows": "Install CMake for Windows (or via choco: choco install cmake)",
            "default": "Install CMake for your OS.",
        }
    },
    {
        "name": "Network / TLS issues fetching wheels",
        "pattern": re.compile(r"(Read timed out|Connection reset by peer|SSLError|TLSV1_ALERT_PROTOCOL_VERSION|Temporary failure in name resolution)", re.I),
        "explain": "Network or TLS handshake error while fetching distribution files.",
        "fix_generic": "Retry on a stable connection; set a mirror; ensure up-to-date OpenSSL; consider offline wheels.",
    },
]

@dataclass
class Finding:
    rule: str
    reason: str
    fix: str

def extract_failure_window(text: str, window: int = 60) -> str:
    lines = text.splitlines()
    last_idx = -1
    pattern = re.compile("|".join(ERROR_MARKERS), re.I)
    for i, ln in enumerate(lines):
        if pattern.search(ln):
            last_idx = i
    if last_idx == -1:
        return "\n".join(lines[-window:])
    start = max(0, last_idx - window // 2)
    end = min(len(lines), last_idx + window // 2)
    return "\n".join(lines[start:end])

def apply_rules(snippet: str, os_hint: str) -> list[Finding]:
    out: list[Finding] = []
    for rule in RULES:
        if rule["pattern"].search(snippet):
            if "fix_by_os" in rule:
                fix = rule["fix_by_os"].get(os_hint, rule["fix_by_os"]["default"])
            else:
                fix = rule.get("fix_generic", "Check project docs or install missing dependencies.")
            out.append(Finding(rule=rule["name"], reason=rule["explain"], fix=fix))
    return out
