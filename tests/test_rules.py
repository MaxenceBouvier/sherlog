from sherlog.rules import apply_rules, extract_failure_window, Finding
from sherlog.cli import make_user_prompt, rules_only_text



def test_compiler_rule():
    snippet = "building ext\nerror: command 'cc' failed: No such file or directory\n"
    findings = apply_rules(snippet, "debian")
    assert any(f.rule == "Missing C compiler" for f in findings)


def test_window_extract():
    text = "\n".join([f"line {i}" for i in range(100)]) + "\nerror: something bad\n"
    snippet = extract_failure_window(text, window=20)
    assert "error:" in snippet


def test_python_headers_rule():
    snippet = "fatal error: Python.h: No such file or directory"
    findings = apply_rules(snippet, "ubuntu")
    assert any(f.rule == "Missing Python headers" for f in findings)


def test_unsupported_python_rule():
    snippet = "Requires-Python: >=3.14"
    findings = apply_rules(snippet, "debian")
    assert any(f.rule == "Unsupported Python version for wheel" for f in findings)


def test_system_lib_rule():
    snippet = "fatal error: openssl/ssl.h: No such file or directory"
    findings = apply_rules(snippet, "debian")
    assert any(
        f.rule == "Missing system lib (e.g., libffi, openssl)" for f in findings
    )


def test_pkg_config_rule():
    snippet = "pkg-config: command not found"
    findings = apply_rules(snippet, "debian")
    assert any(f.rule == "pkg-config missing" for f in findings)


def test_cmake_rule():
    snippet = "cmake: command not found"
    findings = apply_rules(snippet, "debian")
    assert any(f.rule == "CMake not found" for f in findings)


def test_network_tls_rule():
    snippet = "SSLError: TLSV1_ALERT_PROTOCOL_VERSION"
    findings = apply_rules(snippet, "debian")
    assert any(
        f.rule == "Network / TLS issues fetching wheels" for f in findings
    )


def test_make_user_prompt_includes_findings():
    finding = Finding(
        rule="Missing C compiler", reason="No compiler", fix="install build-essential"
    )
    prompt = make_user_prompt("error", "ubuntu", "pip", [finding])
    assert "Detected patterns" in prompt and "Missing C compiler" in prompt


def test_rules_only_text_outputs_findings():
    findings = [Finding(rule="Foo", reason="Bar", fix="Baz")]
    text = rules_only_text(findings)
    assert "Foo" in text and "Baz" in text


def test_rules_only_text_no_findings():
    text = rules_only_text([])
    assert "No known patterns" in text
