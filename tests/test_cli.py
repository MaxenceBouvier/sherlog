from sherlog.cli import main


def test_cli_rules_only(capsys):
    # Use provided sample log and the rules-only path
    code = main(["examples/sample.log", "--no-ml", "--os", "ubuntu"])
    out = capsys.readouterr().out
    assert code == 0
    # Robust to rich/Plain output; just look for key text
    assert "Missing C compiler" in out

