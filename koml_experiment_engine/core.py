"""Pure validation and exact updates. Beliefs are model-derived, never predictions."""
from datetime import date
from fractions import Fraction

class InputError(ValueError):
    """Named input failure."""

def fraction(value, field):
    if not isinstance(value, str) or len(value) > 100:
        raise InputError(f"SchemaError: {field} must be a rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError):
        raise InputError(f"SchemaError: invalid {field}") from None
    return result

def formulate(identifier, claim, threshold="3/4", minimum_trials=10):
    return {"id": identifier, "claim": claim, "threshold": threshold,
            "minimum_trials": minimum_trials, "prior_alpha": 1, "prior_beta": 1}

def require_fields(obj, required, context):
    if not isinstance(obj, dict):
        raise InputError(f"SchemaError: {context} must be an object")
    missing = set(required) - obj.keys()
    extra = obj.keys() - set(required)
    if missing or extra:
        raise InputError(f"SchemaError: {context} fields missing={sorted(missing)} unknown={sorted(extra)}")

def text(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 10000:
        raise InputError(f"SchemaError: {field} must be nonempty text up to 10000 characters")
    if chr(0x2014) in value:
        raise InputError(f"SchemaError: {field} contains forbidden punctuation U+2014")

def integer(value, field, minimum):
    if type(value) is not int or not minimum <= value <= 1000000:
        raise InputError(f"SchemaError: {field} must be integer {minimum}..1000000")

def update_belief(alpha, beta, successes, failures):
    """Beta-Bernoulli posterior mean, an explicit model-derived belief."""
    return str(Fraction(alpha + successes, alpha + beta + successes + failures))

def run_experiments(documents):
    hypotheses, records, provenance = {}, [], []
    for source, doc in documents:
        try:
            require_fields(doc, ['synthetic', 'entered_by', 'as_of', 'hypotheses', 'records'], 'document')
            if type(doc['synthetic']) is not bool:
                raise InputError('SchemaError: synthetic must be boolean')
            if doc['entered_by'] != ('fixture generator' if doc['synthetic'] else 'Henry'):
                raise InputError('SchemaError: entered_by must be fixture generator for synthetic or Henry for real')
            as_of = date.fromisoformat(doc['as_of'])
            if not isinstance(doc['hypotheses'], list) or not isinstance(doc['records'], list):
                raise InputError('SchemaError: hypotheses and records must be arrays')
            local = set()
            for h in doc['hypotheses']:
                require_fields(h, ['id', 'claim', 'threshold', 'minimum_trials', 'prior_alpha', 'prior_beta'], 'hypothesis')
                text(h['id'], 'id'); text(h['claim'], 'claim')
                if h['id'] in hypotheses:
                    raise InputError('SchemaError: duplicate hypothesis id ' + h['id'])
                if not 0 <= fraction(h['threshold'], 'threshold') <= 1:
                    raise InputError('SchemaError: threshold outside 0..1')
                for field in ['minimum_trials', 'prior_alpha', 'prior_beta']:
                    integer(h[field], field, 1)
                hypotheses[h['id']] = h
                local.add(h['id'])
            for r in doc['records']:
                require_fields(r, ['id', 'hypothesis_id', 'date', 'success', 'note', 'synthetic'], 'record')
                text(r['id'], 'record id'); text(r['hypothesis_id'], 'hypothesis_id')
                if not isinstance(r['note'], str) or len(r['note']) > 10000 or chr(0x2014) in r['note']:
                    raise InputError('SchemaError: note must be text up to 10000 characters without U+2014')
                if r['hypothesis_id'] not in local:
                    raise InputError('SchemaError: unknown hypothesis_id')
                if type(r['success']) is not bool or type(r['synthetic']) is not bool or r['synthetic'] != doc['synthetic']:
                    raise InputError('SchemaError: success/synthetic must be consistent booleans')
                if date.fromisoformat(r['date']) > as_of:
                    raise InputError('SchemaError: future date beyond explicit as_of')
                records.append(r)
            provenance.append({'file': source, 'synthetic': doc['synthetic'], 'entered_by': doc['entered_by'], 'as_of': doc['as_of']})
        except (InputError, ValueError, TypeError) as exc:
            raise InputError(f'{source}: line 1: {exc}') from None
    ids = [r['id'] for r in records]
    if len(ids) != len(set(ids)):
        raise InputError('SchemaError: duplicate record ids across inputs: line 1')
    results = []
    for hid, h in sorted(hypotheses.items()):
        trials = sorted((r for r in records if r['hypothesis_id'] == hid), key=lambda r: r['id'])
        n = len(trials); s = sum(r['success'] for r in trials)
        rate = Fraction(s, n) if n else Fraction(0)
        status = 'insufficient' if n < h['minimum_trials'] else ('accepted' if rate >= fraction(h['threshold'], 'threshold') else 'rejected')
        results.append({**h, 'trials': n, 'successes': s, 'failures': n-s, 'success_rate': str(rate),
                        'posterior_mean': update_belief(h['prior_alpha'], h['prior_beta'], s, n-s),
                        'status': status, 'record_ids': [r['id'] for r in trials]})
    return {'provenance': sorted(provenance, key=lambda p: p['file']), 'records': len(records),
            'successes': sum(r['success'] for r in records), 'failures': sum(not r['success'] for r in records),
            'accepted': sum(h['status'] == 'accepted' for h in results),
            'rejected': sum(h['status'] == 'rejected' for h in results),
            'insufficient': sum(h['status'] == 'insufficient' for h in results), 'hypotheses': results}
