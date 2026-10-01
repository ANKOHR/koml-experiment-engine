import copy
import pytest
from koml_experiment_engine.core import InputError, run_experiments
from koml_experiment_engine.fixtures import fixture

def run(doc):
    return run_experiments([('trials.json', doc)])

def test_fixture_ground_truth_matches_hand_computed():
    r = run(fixture())
    assert (r['records'], r['successes'], r['failures'], r['accepted'], r['rejected']) == (200,130,70,5,5)
    assert [h['posterior_mean'] for h in r['hypotheses']] == ['19/22']*5 + ['9/22']*5
    assert [h['success_rate'] for h in r['hypotheses']] == ['9/10']*5 + ['2/5']*5

@pytest.mark.parametrize('mutation', ['negative','future','long','duplicate','unknown','boolean','prior','field','dash'])
def test_rejects_adversarial_values(mutation):
    d = fixture()
    if mutation == 'negative': d['hypotheses'][0]['minimum_trials'] = -1
    if mutation == 'future': d['records'][0]['date'] = '2027-01-01'
    if mutation == 'long': d['records'][0]['note'] = 'a'*10001
    if mutation == 'duplicate': d['records'][1]['id'] = d['records'][0]['id']
    if mutation == 'unknown': d['records'][0]['hypothesis_id'] = 'missing'
    if mutation == 'boolean': d['records'][0]['success'] = 1
    if mutation == 'prior': d['hypotheses'][0]['prior_alpha'] = 0
    if mutation == 'field': d['records'][0]['amount'] = -1
    if mutation == 'dash': d['hypotheses'][0]['claim'] = chr(0x2014)
    with pytest.raises(InputError, match='SchemaError'): run(d)

def test_corrupted_ground_truth_changes_output():
    d = fixture()
    for r in d['records'][:20]: r['success'] = False
    r = run(d)
    assert r['successes'] == 112 and r['accepted'] == 4
    assert r['hypotheses'][0]['posterior_mean'] == '1/22'

def test_handles_unicode_and_long_inputs():
    d = fixture(); d['records'][0]['note'] = '日本語 café C:\\Users\\Henry ' + 'x'*9000
    d['hypotheses'][0]['claim'] = '日本語 café'
    assert run(d)['hypotheses'][0]['claim'] == '日本語 café'

def test_empty_and_insufficient():
    assert run_experiments([])['records'] == 0
    d = fixture(); d['records'] = d['records'][:5]
    assert run(d)['insufficient'] == 10

def test_real_provenance():
    d = fixture(); d['synthetic'] = False; d['entered_by'] = 'Henry'
    for r in d['records']: r['synthetic'] = False
    assert run(d)['provenance'][0]['synthetic'] is False
