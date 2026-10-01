import json
import time
import pytest
from koml_experiment_engine.cli import main

@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path

def test_run_completes_on_fixture(workspace, capsys):
    start = time.perf_counter()
    assert main(['fixtures','--out','demo']) == 0
    assert main(['run','--input','demo']) == 0
    assert main(['report','--format','md']) == 0
    assert time.perf_counter()-start < 5
    assert 'Data provenance:' in capsys.readouterr().out

def test_empty_input_renders_without_traceback(workspace, capsys):
    (workspace/'empty').mkdir()
    assert main(['run','--input','empty']) == 0
    assert main(['report']) == 0
    assert 'records: 0' in capsys.readouterr().out

def test_malformed_input_named_error(workspace, capsys):
    (workspace/'bad').mkdir(); (workspace/'bad'/'broken.json').write_text('{\n bad')
    assert main(['run','--input','bad']) == 2
    output = capsys.readouterr().err
    assert 'ParseError' in output and 'broken.json' in output and 'line 2' in output

def test_cli_smoke_all_subcommands(workspace, capsys):
    assert main(['fixtures','--out','demo']) == 0
    assert main(['run','--input','demo']) == 0
    assert main(['report','--format','json']) == 0
    assert main(['belief']) == 0
    assert main(['hypothesis','--id','test','--claim','Recorded criterion']) == 0
    assert 'hypothetical' in capsys.readouterr().out
    for command in ['fixtures','run','report','belief','hypothesis']:
        with pytest.raises(SystemExit) as e: main([command,'--help'])
        assert e.value.code == 0

def test_cli_determinism(workspace):
    main(['fixtures','--out','demo']); main(['run','--input','demo'])
    first = (workspace/'.kee2-results.json').read_bytes()
    main(['run','--input','demo'])
    assert first == (workspace/'.kee2-results.json').read_bytes()
    main(['report','--out','a.md']); main(['report','--out','b.md'])
    assert (workspace/'a.md').read_bytes() == (workspace/'b.md').read_bytes()

def test_missing_input(workspace, capsys):
    assert main(['run','--input','absent']) == 2
    assert 'MissingInput' in capsys.readouterr().err

def test_write_failure_no_partial_files(workspace, capsys):
    main(['fixtures','--out','demo']); main(['run','--input','demo'])
    before = set(workspace.iterdir())
    assert main(['report','--out','absent/report.md']) == 2
    assert 'WriteError' in capsys.readouterr().err
    assert set(workspace.iterdir()) == before

def test_schema_drift_names_field(workspace, capsys):
    main(['fixtures','--out','demo'])
    p = workspace/'demo'/'trials.json'; d = json.loads(p.read_text()); d['surprise'] = 1; p.write_text(json.dumps(d))
    assert main(['run','--input','demo']) == 2
    error = capsys.readouterr().err
    assert 'SchemaError' in error and 'surprise' in error and 'trials.json' in error


def test_malformed_results_named_error(workspace, capsys):
    main(['fixtures','--out','demo']); main(['run','--input','demo'])
    p = workspace/'.kee2-results.json'; d = json.loads(p.read_text()); d['hypotheses'] = [None]; p.write_text(json.dumps(d))
    assert main(['report']) == 2
    assert 'SchemaError' in capsys.readouterr().err
