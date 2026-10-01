from koml_experiment_engine.fixtures import fixture, expectations

def test_fixtures_labelled_synthetic():
    d = fixture()
    assert len(d['records']) == 200 and d['synthetic'] is True
    assert all(r['synthetic'] is True for r in d['records'])
    assert expectations()['synthetic'] is True

def test_generator_deterministic():
    assert fixture() == fixture()
