from sherlog.rules import apply_rules, extract_failure_window

def test_compiler_rule():
    snippet = "building ext\nerror: command 'cc' failed: No such file or directory\n"
    findings = apply_rules(snippet, "debian")
    assert any(f.rule == "Missing C compiler" for f in findings)

def test_window_extract():
    text = "\n".join([f"line {i}" for i in range(100)]) + "\nerror: something bad\n"
    snippet = extract_failure_window(text, window=20)
    assert "error:" in snippet
