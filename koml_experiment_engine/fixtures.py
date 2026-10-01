"""Synthetic labelled data. No randomness; seed is not applicable."""
from .core import formulate

def fixture():
    hypotheses = [formulate(f'h{i}', f'Illustrative intervention {i} meets its recorded success criterion') for i in range(10)]
    records = [{'id': f'r{i:03}', 'hypothesis_id': f'h{i//20}', 'date': '2026-09-30',
                'success': i % 20 < (18 if i//20 < 5 else 8),
                'note': 'Synthetic planted observation', 'synthetic': True} for i in range(200)]
    return {'synthetic': True, 'entered_by': 'fixture generator', 'as_of': '2026-09-30',
            'hypotheses': hypotheses, 'records': records}

def expectations():
    # Hand arithmetic: 5*18 + 5*8 = 130; 200-130 = 70.
    # First five: 18/20 = 9/10, posterior 19/22. Others: 8/20 = 2/5, posterior 9/22.
    return {'synthetic': True, 'label': 'Synthetic hand-computed expectations, not engine output',
            'records': 200, 'successes': 130, 'failures': 70, 'accepted': 5, 'rejected': 5,
            'insufficient': 0, 'accepted_ids': ['h0', 'h1', 'h2', 'h3', 'h4'],
            'rates': ['9/10']*5 + ['2/5']*5, 'posterior_means': ['19/22']*5 + ['9/22']*5}
