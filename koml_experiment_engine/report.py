"""Deterministic reports with explicit provenance and model limits."""
import json

BANNER = 'Data provenance: synthetic fixtures are illustrative; real inputs are declared Henry-entered observations, not independently verified.'
HONESTY = 'Success rates are computed from recorded inputs. Posterior means are model-derived beliefs under declared Beta-Bernoulli priors, not measured probabilities or predictions. Time and money saved are unmeasured and are not reported. No ground-truth accuracy claim is made for real data.'

def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n'

def render(result, format='md'):
    if format == 'json':
        return json_text({'provenance_banner': BANNER, 'honesty': HONESTY, **result})
    lines = ['# KOML Experiment Engine', '', BANNER, '', HONESTY, '', '## Inputs', '']
    lines += [f"- {p['file']}: {'SYNTHETIC' if p['synthetic'] else 'REAL (declared Henry-entered)'}; as_of={p['as_of']}" for p in result['provenance']] or ['No inputs; all counts are zero.']
    lines += ['', '## Computed counts', '']
    lines += [f"- {key}: {result[key]}" for key in ['records', 'successes', 'failures', 'accepted', 'rejected', 'insufficient']]
    for h in result['hypotheses']:
        lines += ['', f"## {h['id']}", '', h['claim'], '', f"Status: {h['status']}; successes={h['successes']}; failures={h['failures']}; trials={h['trials']}",
                  f"Recorded success rate: {h['success_rate']}; threshold: {h['threshold']}; minimum trials: {h['minimum_trials']}",
                  f"Model-derived posterior mean: {h['posterior_mean']}; prior alpha={h['prior_alpha']}, beta={h['prior_beta']}",
                  'Evidence record IDs: ' + ', '.join(h['record_ids'])]
    return '\n'.join(lines) + '\n'
