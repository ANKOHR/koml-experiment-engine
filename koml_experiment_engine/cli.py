"""Local CLI; no network, model calls, or time-dependent output."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import InputError, formulate, run_experiments
from .fixtures import fixture, expectations
from .report import json_text, render

def atomic_write(path, content):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n', dir=path.parent, delete=False) as f:
            temporary = Path(f.name)
            f.write(content)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f'WriteError: {path}: {exc.strerror}') from None
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        raise InputError(f'ParseError: {path}: line {exc.lineno}: {exc.msg}') from None
    except (OSError, UnicodeError) as exc:
        raise InputError(f'ReadError: {path}: line 1: {exc}') from None

def load_inputs(directory):
    path = Path(directory)
    if not path.is_dir():
        raise InputError(f'MissingInput: {path}; use kee2 fixtures --out demo or supply an input directory')
    docs = []
    for f in sorted(path.iterdir()):
        if f.name == 'expectations.json' or f.suffix.lower() == '.md' or not f.is_file():
            continue
        if f.suffix.lower() != '.json':
            raise InputError(f'SchemaError: {f}: line 1: unsupported format; use JSON document files')
        docs.append((f.name, read_json(f)))
    return docs

def parser():
    p = argparse.ArgumentParser(description='Compute explicit experiment outcomes and model-derived beliefs from local JSON.')
    sub = p.add_subparsers(dest='command', required=True)
    f = sub.add_parser('fixtures', help='Generate 200 labelled synthetic trials', epilog='Example: kee2 fixtures --out demo')
    f.add_argument('--out', required=True)
    r = sub.add_parser('run', help='Validate and run recorded experiments', epilog='Example: kee2 run --input demo')
    r.add_argument('--input', required=True); r.add_argument('--results', default='.kee2-results.json')
    r = sub.add_parser('report', help='Render computed results and provenance', epilog='Example: kee2 report --format md')
    r.add_argument('--format', choices=['md', 'json'], default='md'); r.add_argument('--results', default='.kee2-results.json'); r.add_argument('--out')
    h = sub.add_parser('hypothesis', help='Formulate a hypothesis with explicit acceptance criteria', epilog='Example: kee2 hypothesis --id h1 --claim "Success rate reaches 75 percent"')
    h.add_argument('--id', required=True); h.add_argument('--claim', required=True); h.add_argument('--threshold', default='3/4'); h.add_argument('--minimum-trials', type=int, default=10)
    b = sub.add_parser('belief', help='Show model-derived belief updates from stored results', epilog='Example: kee2 belief --results .kee2-results.json')
    b.add_argument('--results', default='.kee2-results.json')
    return p

def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == 'fixtures':
            path = Path(args.out); path.mkdir(parents=True, exist_ok=True)
            atomic_write(path / 'trials.json', json_text(fixture()))
            atomic_write(path / 'expectations.json', json_text(expectations()))
            atomic_write(path / 'LABEL.md', '# SYNTHETIC FIXTURES\nAll observations are illustrative planted ground truth. No real trials.\n')
            print('Generated 200 SYNTHETIC illustrative records.')
        elif args.command == 'run':
            result = run_experiments(load_inputs(args.input))
            atomic_write(args.results, json_text(result))
            print(f"Computed {result['records']} recorded trials. Use kee2 report for provenance and model limits.")
        elif args.command == 'hypothesis':
            h = formulate(args.id, args.claim, args.threshold, args.minimum_trials)
            run_experiments([('hypothesis', {'synthetic': False, 'entered_by': 'Henry', 'as_of': '2000-01-01', 'hypotheses': [h], 'records': []})])
            print(json_text({'label': 'Proposed hypothesis; hypothetical, unmeasured until trials are recorded', **h}), end='')
        else:
            result = read_json(Path(args.results))
            if not isinstance(result, dict) or not all(k in result for k in ['provenance', 'records', 'successes', 'failures', 'accepted', 'rejected', 'insufficient', 'hypotheses']):
                raise InputError('SchemaError: results missing required fields; use kee2 run')
            output = render(result, args.format if args.command == 'report' else 'json')
            if args.command == 'report' and args.out:
                atomic_write(args.out, output)
            else:
                print(output, end='')
        return 0
    except (InputError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        print(f'SchemaError: invalid results or input fields: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
