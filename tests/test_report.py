import json
from koml_experiment_engine.core import run_experiments
from koml_experiment_engine.fixtures import fixture, expectations
from koml_experiment_engine.report import render

def result(): return run_experiments([('trials.json', fixture())])

def test_report_matches_ground_truth_exact():
    r = json.loads(render(result(), 'json')); e = expectations()
    for field in ['records','successes','failures','accepted','rejected','insufficient']: assert r[field] == e[field]
    assert [h['success_rate'] for h in r['hypotheses']] == e['rates']
    assert [h['posterior_mean'] for h in r['hypotheses']] == e['posterior_means']
    assert sum(h['trials'] for h in r['hypotheses']) == r['records']

def test_report_zero_false_positives():
    accepted = {h['id'] for h in result()['hypotheses'] if h['status'] == 'accepted'}
    assert accepted == set(expectations()['accepted_ids'])

def test_report_carries_provenance_banner():
    for fmt in ['md','json']:
        output = render(result(), fmt)
        assert 'Data provenance:' in output and 'synthetic' in output and 'trials.json' in output

def test_hypothetical_figures_labelled():
    for fmt in ['md','json']:
        output = render(result(), fmt)
        assert 'illustrative' in output and 'unmeasured' in output and 'model-derived' in output

def test_no_em_dashes_in_outputs():
    for fmt in ['md','json']: assert chr(0x2014) not in render(result(), fmt)

def test_determinism_byte_identical():
    for fmt in ['md','json']: assert render(result(), fmt).encode() == render(result(), fmt).encode()
