#!/usr/bin/env python3
"""Source-backed wiki navigation and measurable structural/routing acceptance.

Python 3.10+, standard library only. Never executes recorded commands or project code.
Only the explicit build command writes generated route-index files.
"""
from __future__ import annotations

import argparse
import ast
from datetime import date
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys


class Invalid(ValueError):
    """An actionable manifest, path or source error."""


ROLES = {'declaration', 'implementation', 'caller', 'consumer', 'contract'}
KINDS = {'interface', 'behavior', 'architecture', 'plan'}
STATES = {'planned', 'implemented', 'mixed', 'unknown'}
LEVELS = {'source', 'offline-tested', 'installed', 'live-verified'}
STOP = {'a', 'an', 'the', 'to', 'of', 'for', 'and', 'or', 'is', 'it', 'in', 'on',
        'i', 'we', 'how', 'what', 'does', 'do', 'can', 'this', 'that', 'with', 'my'}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and all(text(item) for item in value)


def local(root, name):
    if not text(name) or Path(name).is_absolute() or PureWindowsPath(name).anchor:
        raise Invalid(f'Expected a repository-relative path: {name!r}')
    if '\\' in name:
        raise Invalid(f'Use forward slashes in manifest paths: {name!r}')
    result = (root / name).resolve()
    if not result.is_relative_to(root):
        raise Invalid(f'Path escapes project root: {name}')
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def load(root):
    manifest = read_json(local(root, 'docs/wiki/routes.json'))
    if not isinstance(manifest, dict) or type(manifest.get('schema_version')) is not int or manifest.get('schema_version') not in (1, 2):
        raise Invalid('Expected schema_version 1 (legacy) or 2')
    if not text(manifest.get('project')) or not isinstance(manifest.get('routes'), list):
        raise Invalid('Manifest needs project and routes')
    seen = set()
    for row in manifest['routes']:
        if not isinstance(row, dict) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', str(row.get('id', ''))):
            raise Invalid('Each route needs a stable lowercase-hyphen id')
        if row['id'] in seen:
            raise Invalid(f'Duplicate route id: {row["id"]}')
        seen.add(row['id'])
        if not text(row.get('title')):
            raise Invalid(f'{row["id"]}: missing title')
        if not strings(row.get('aliases', [])):
            raise Invalid(f'{row["id"]}: aliases must be strings')
    quality = manifest.get('quality', {})
    if not isinstance(quality, dict):
        raise Invalid('quality must be an object')
    for key, default, low, high in [('min_structural_score', 85, 0, 100), ('max_query_words', 450, 1, 10000)]:
        value = quality.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
            raise Invalid(f'Invalid quality.{key}')
    return manifest


def py_symbols(node, prefix=''):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            qualified = prefix + child.name
            yield qualified, child.lineno
            yield from py_symbols(child, qualified + '.')
        else:
            yield from py_symbols(child, prefix)


def resolve_source(root, entry):
    if not isinstance(entry, dict):
        raise Invalid('Source record must be an object')
    path = local(root, entry.get('path'))
    if not path.is_file():
        raise Invalid(f'Missing source: {entry.get("path")}')
    content = path.read_text(encoding='utf-8-sig')  # universal newlines
    if text(entry.get('symbol')) == text(entry.get('needle')):
        raise Invalid(f'Choose exactly one symbol or needle: {entry.get("path")}')
    if text(entry.get('symbol')):
        if path.suffix != '.py':
            raise Invalid(f'AST symbols support Python; use a unique needle for {entry["path"]}')
        matches = [line for name, line in py_symbols(ast.parse(content)) if name == entry['symbol']]
    else:
        matches = [n for n, line in enumerate(content.splitlines(), 1) if entry['needle'] in line]
    if len(matches) != 1:
        raise Invalid(f'Expected one source match, got {len(matches)}: {entry["path"]}::{entry.get("symbol") or entry.get("needle")}')
    return dict(entry, line=matches[0], sha256=hashlib.sha256(content.encode('utf-8')).hexdigest())


def anchors(content):
    result = set(re.findall(r'<a\s+[^>]*id=["\']([^"\']+)["\']', content, re.I))
    used = {}
    fence = None
    for line in content.splitlines():
        opening = re.match(r'^\s{0,3}(`{3,}|~{3,})', line)
        if opening:
            token = opening.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is not None:
            continue
        heading = re.match(r'^#{1,6}\s+(.+?)(?:\s+#+)?\s*$', line)
        if heading:
            value = re.sub(r'<[^>]*>', '', heading.group(1)).lower()
            slug = re.sub(r'[^\w\- ]', '', value).replace(' ', '-')
            count = used.get(slug, 0)
            used[slug] = count + 1
            result.add(slug if count == 0 else f'{slug}-{count}')
    return result


def verify_ref(root, reference):
    if not text(reference):
        raise Invalid('Reference must be a nonempty local path')
    name, _, fragment = reference.partition('#')
    path = local(root, name)
    if not path.is_file():
        raise Invalid(f'Missing reference: {reference}')
    if fragment and fragment not in anchors(path.read_text(encoding='utf-8-sig')):
        raise Invalid(f'Missing Markdown anchor: {reference}')


def valid_date(value):
    if not text(value) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def resolve_route(root, row, version):
    if not text(row.get('boundary')):
        raise Invalid('Route requires an evidence boundary')
    for field in ('sources', 'rules', 'checks'):
        if not isinstance(row.get(field, []), list):
            raise Invalid(f'{field} must be an array')
    for field in ('docs', 'tests', 'impact', 'unknowns'):
        if field in row and not strings(row[field]):
            raise Invalid(f'{field} must be an array of nonempty strings')
    locations = [resolve_source(root, item) for item in row.get('sources', [])]
    for reference in row.get('docs', []) + row.get('tests', []):
        verify_ref(root, reference)
    if version == 1:
        return dict(row, locations=locations)
    if row.get('kind') not in KINDS:
        raise Invalid('kind must be interface, behavior, architecture or plan')
    evidence = row.get('evidence', {})
    if not isinstance(evidence, dict) or evidence.get('implementation') not in STATES:
        raise Invalid('evidence.implementation must explicitly describe implementation state')
    planned = evidence['implementation'] == 'planned'
    if row['kind'] == 'plan' and not planned:
        raise Invalid('Plan routes must remain planned; use a separate implemented route')
    if row['kind'] == 'plan':
        plan = row.get('plan', {})
        if not isinstance(plan, dict) or not all(
            strings(plan.get(field)) for field in
            ('outcomes', 'dependencies', 'interfaces', 'deliverables', 'exit_evidence', 'unknowns')
        ) or not all(plan.get(field) for field in ('outcomes', 'interfaces', 'deliverables', 'exit_evidence')):
            raise Invalid('Plans require outcomes, dependencies, interfaces, deliverables, exit_evidence and unknowns; empty dependencies/unknowns must be explicit')
    if not planned and not locations:
        raise Invalid('A non-planned route must resolve existing source')
    ids = set()
    for source in locations:
        if not text(source.get('id')) or source['id'] in ids or source.get('role') not in ROLES:
            raise Invalid('Source IDs must be unique and roles valid')
        ids.add(source['id'])
        if not text(source.get('reason')):
            raise Invalid('Each source requires its reason in the edit surface')
        if planned and source['role'] == 'implementation':
            raise Invalid('Do not label a proposed implementation as existing source')
    rule_ids = set()
    for rule in row.get('rules', []):
        if not isinstance(rule, dict) or not text(rule.get('id')) or rule['id'] in rule_ids or not text(rule.get('statement')):
            raise Invalid('Rules need unique IDs and statements')
        rule_ids.add(rule['id'])
        refs = rule.get('source_ids', [])
        if not strings(refs) or any(ref not in ids for ref in refs):
            raise Invalid(f'Unknown rule source ID: {rule["id"]}')
        if not refs and not (planned and rule.get('proposed') is True):
            raise Invalid(f'Rule has no source provenance: {rule["id"]}')
        if not strings(rule.get('tests', [])):
            raise Invalid('Rule tests must be paths')
        for reference in rule.get('tests', []):
            verify_ref(root, reference)
    interface = row.get('interface', {})
    if not isinstance(interface, dict):
        raise Invalid('interface must be an object')
    for field in ('inputs', 'outputs', 'errors'):
        if field in interface and not strings(interface[field]):
            raise Invalid(f'interface.{field} must be strings')
    if 'compatibility' in interface and not text(interface['compatibility']):
        raise Invalid('interface.compatibility must be nonempty')
    if row['kind'] == 'interface' and not all(interface.get(field) for field in ('inputs', 'outputs', 'errors', 'compatibility')):
        raise Invalid('Interface routes require inputs, outputs, errors and compatibility')
    modes = interface.get('failure_modes', {})
    if not isinstance(modes, dict):
        raise Invalid('interface.failure_modes must be an object')
    if row['kind'] == 'interface' and not all(strings(modes.get(key)) and modes[key] for key in ('returned', 'thrown', 'unsupported')):
        raise Invalid('Interface routes must distinguish returned, thrown and unsupported failure modes')
    for check in row.get('checks', []):
        if not isinstance(check, dict) or not text(check.get('command')) or not text(check.get('scope')):
            raise Invalid('Checks require command and scope; commands are never executed')
    observations = evidence.get('observations', [])
    if not isinstance(observations, list):
        raise Invalid('evidence.observations must be an array')
    for observation in observations:
        if not isinstance(observation, dict) or observation.get('level') not in LEVELS:
            raise Invalid('Observation requires a supported evidence level')
        if not all(text(observation.get(key)) for key in ('claim', 'revision')) or not valid_date(observation.get('observed_at')):
            raise Invalid('Observations require claim, revision, and observed_at date')
        verify_ref(root, observation.get('reference'))
        if planned and observation['level'] != 'source':
            raise Invalid('A plan cannot claim completed testing, installation or live verification')
    if 'reviewed_at' in row and not valid_date(row['reviewed_at']):
        raise Invalid('reviewed_at must be an actual YYYY-MM-DD date')
    if not isinstance(row.get('diagrams', []), list):
        raise Invalid('diagrams must be an array')
    for diagram in row.get('diagrams', []):
        if not isinstance(diagram, dict) or diagram.get('kind') not in {'architecture', 'flow', 'sequence', 'data-model', 'deployment', 'state-machine'}:
            raise Invalid('Unsupported diagram kind')
        if not text(diagram.get('question')) or not text(diagram.get('scope')):
            raise Invalid('Diagrams must explain their question and scope')
        verify_ref(root, diagram.get('path'))
    return dict(row, locations=locations)


def score(row):
    """Observable structural subcriteria only; never infer semantic correctness."""
    locations = row.get('locations', [])
    roles = {source.get('role') for source in locations}
    planned = row.get('evidence', {}).get('implementation') == 'planned'
    contract = row.get('interface', {})
    parts = {
        'location': (20 if planned else 12 * ('implementation' in roles) + 8 *
                     (row.get('kind') != 'interface' or 'declaration' in roles)),
        'contract': sum(3 * bool(contract.get(key)) for key in ('inputs', 'outputs'))
                    + 2 * bool(contract.get('errors')) + 3 * bool(contract.get('compatibility'))
                    + 4 * all(contract.get('failure_modes', {}).get(key) for key in ('returned', 'thrown', 'unsupported')),
        'rules': 15 * bool(row.get('rules')),
        'impact': 8 * bool(row.get('impact')) + 7 * (planned or bool(roles & {'caller', 'consumer'})),
        'validation': 8 * bool(row.get('tests')) + 7 * bool(row.get('checks')),
        'boundary': 3 * bool(row.get('boundary')) + 3 * ('unknowns' in row)
                    + 4 * (planned or bool(row.get('evidence', {}).get('observations'))),
        'findability': 2 * bool(row.get('aliases')) + 3 * bool(row.get('docs')),
        'freshness': 3 * valid_date(row.get('reviewed_at')) + 2 * (planned or bool(locations)),
    }
    return {'total': sum(parts.values()), 'categories': parts}


def audit(root, manifest):
    version = manifest['schema_version']
    reports = []
    for row in manifest['routes']:
        try:
            resolved = resolve_route(root, row, version)
            quality = score(resolved) if version == 2 else None
            reports.append({'id': row['id'], 'valid': True, 'score': quality,
                            'locations': len(resolved['locations']),
                            'plan_coverage': {'numerator': 6, 'denominator': 6} if version == 2 and row.get('kind') == 'plan' else None,
                            'gaps': [field for field in ('kind', 'interface', 'rules', 'impact', 'unknowns', 'evidence', 'reviewed_at') if field not in row]})
        except (ValueError, OSError, SyntaxError, TypeError) as error:
            reports.append({'id': row['id'], 'valid': False, 'error': str(error), 'score': None})
    totals = [item['score']['total'] for item in reports if item['score'] is not None]
    floor = manifest.get('quality', {}).get('min_structural_score', 85)
    ready = version == 2 and bool(reports) and all(item['valid'] and item['score']['total'] >= floor for item in reports)
    return {'schema_version': version, 'mode': 'structural' if version == 2 else 'legacy-gap-analysis',
            'ready': ready, 'routes': reports, 'route_count': len(reports),
            'structural_average': round(sum(totals) / len(totals), 2) if totals else None,
            'structural_minimum': min(totals) if totals else None, 'required_per_route': floor,
            'semantic_accuracy': 'not measured', 'independent_adoption': 'not measured'}


def words(value):
    return set(re.findall(r'\w+', value.casefold())) - STOP


def rank(query, routes):
    value = query.casefold().strip()
    if not value:
        return []
    tokens = words(value)
    hits = []
    for row in routes:
        aliases = [row['id'], row['title'], *row.get('aliases', [])]
        points = 0
        for alias in aliases:
            alias = alias.casefold().strip()
            matched = (re.search(r'(?<!\w)' + re.escape(alias) + r'(?!\w)', value) is not None
                       if alias.isascii() else alias in value)
            if matched:
                points += 10 + min(len(alias), 30) / 10
        points += len(tokens & words(' '.join(aliases)))
        if points:
            hits.append((points, row))
    return [dict(row, match_score=round(points, 2))
            for points, row in sorted(hits, key=lambda item: (-item[0], item[1]['id']))]


def query(root, manifest, question, limit=2):
    results = []
    for row in rank(question, manifest['routes'])[:limit]:
        try:
            results.append(resolve_route(root, row, manifest['schema_version']))
        except (ValueError, OSError, SyntaxError, TypeError) as error:
            results.append(dict(row, locations=[], warning=str(error)))
    return results


def query_text(results, total_candidates=None):
    if not results:
        return 'No curated route. Try list, then a targeted source search; repair the missing route. No location guessed.'
    lines = []
    if total_candidates is not None and total_candidates > len(results):
        lines.append(f'Showing top {len(results)} of {total_candidates} candidates. Split compound requests by interface/feature; this is not a complete impact inventory.')
    for row in results:
        lines.append(f'{row["id"]}: {row["title"]}')
        if row.get('warning'):
            lines.append('  WARNING: ' + row['warning'])
            refs = row.get('docs', [])
            lines.append('  docs: ' + (' | '.join(refs) if strings(refs) else 'invalid document references'))
            continue
        for source in row.get('locations', []):
            lines.append(f'  {source["path"]}:{source["line"]} [{source.get("role", "legacy")}] '
                         f'{source.get("symbol") or source.get("needle")} — {source.get("reason", "")}')
        lines.append('  docs: ' + ' | '.join(row.get('docs', [])))
        contract = row.get('interface', {})
        if contract:
            lines.append('  contract: ' + json.dumps(contract, ensure_ascii=False))
        for rule in row.get('rules', []):
            lines.append('  rule: ' + rule['statement'])
        if row.get('impact'):
            lines.append('  impact: ' + ' | '.join(row['impact']))
        lines.append('  tests: ' + ' '.join(row.get('tests', [])))
        for check in row.get('checks', []):
            lines.append('  check: ' + (check if isinstance(check, str) else check['command'] + ' :: ' + check['scope']))
        lines.append('  boundary: ' + row.get('boundary', 'not recorded'))
        if row.get('unknowns'):
            lines.append('  unknowns: ' + ' | '.join(row['unknowns']))
    return '\n'.join(lines)


def snapshot(root, manifest):
    if manifest['schema_version'] != 2:
        raise Invalid('Schema 1 is query/audit only; review and migrate before building schema 2')
    return {'schema_version': 2, 'project': manifest['project'],
            'routes': [resolve_route(root, row, 2) for row in manifest['routes']]}


def markdown_index(current):
    lines = [f'# {current["project"]}: engineering routes', '',
             'Generated positions; source wins over stale prose. Read only the relevant route.', '',
             '| Task / ID | Current source and role | Local explanation |', '| --- | --- | --- |']
    for row in current['routes']:
        sources = '<br>'.join(f'`{item["path"]}:{item["line"]}` ({item["role"]})' for item in row['locations']) or 'Planned; no implementation asserted'
        links = []
        for reference in row.get('docs', []):
            if reference.startswith('docs/wiki/'):
                links.append(f'[{reference.removeprefix("docs/wiki/")}]({reference.removeprefix("docs/wiki/")})')
        lines.append(f'| {row["id"]}: {row["title"]} | {sources} | {"<br>".join(links)} |')
    return '\n'.join(lines) + '\n'


def index_paths(root):
    return local(root, 'docs/wiki/route-index.json'), local(root, 'docs/wiki/route-index.md')


def is_stale(root, current):
    machine, human = index_paths(root)
    if not machine.is_file() or not human.is_file():
        return True
    try:
        return read_json(machine) != current or human.read_text(encoding='utf-8-sig') != markdown_index(current)
    except (ValueError, OSError):
        return True


def ratio(numerator, denominator):
    return {'numerator': numerator, 'denominator': denominator,
            'rate': round(numerator / denominator, 4) if denominator else None}


def evaluate(root, manifest, taskfile):
    if not isinstance(taskfile, dict) or type(taskfile.get('schema_version')) is not int or taskfile.get('schema_version') != 1 or not isinstance(taskfile.get('tasks'), list):
        raise Invalid('Task file requires schema_version 1 and tasks')
    thresholds = {'min_top1': .8, 'min_top2': .9, 'min_tasks': 10, 'min_unknown': 2}
    custom = taskfile.get('thresholds', {})
    if not isinstance(custom, dict) or set(custom) - set(thresholds):
        raise Invalid('Unknown evaluation threshold')
    thresholds.update(custom)
    for key in ('min_top1', 'min_top2'):
        if isinstance(thresholds[key], bool) or not isinstance(thresholds[key], (int, float)) or not 0 <= thresholds[key] <= 1:
            raise Invalid(f'Invalid {key}')
    for key in ('min_tasks', 'min_unknown'):
        if type(thresholds[key]) is not int or thresholds[key] < 1:
            raise Invalid(f'{key} must be a positive integer')
    route_ids = {row['id'] for row in manifest['routes']}
    seen = set()
    outcomes = []
    for task in taskfile['tasks']:
        if not isinstance(task, dict) or not text(task.get('id')) or task['id'] in seen or not text(task.get('query')):
            raise Invalid('Tasks require unique IDs and nonempty queries')
        seen.add(task['id'])
        expected = task.get('expected_routes')
        if not strings(expected) or any(item not in route_ids for item in expected):
            raise Invalid(f'{task["id"]}: expected_routes must reference real IDs or be []')
        hits = query(root, manifest, task['query'])
        ids = [row['id'] for row in hits]
        candidates = len(rank(task['query'], manifest['routes']))
        content = query_text(hits, candidates)
        outcomes.append({'id': task['id'], 'query': task['query'], 'expected': expected, 'actual': ids,
                         'top1': bool(ids and ids[0] in expected) if expected else None,
                         'top2': bool(set(ids) & set(expected)) if expected else None,
                         'unknown_rejected': not hits if not expected else None,
                         'locations_ok': bool(hits) and all(not row.get('warning') for row in hits) if expected else not hits,
                         'response_words': len(content.split()), 'response_bytes': len(content.encode('utf-8')),
                         'candidate_count': candidates, 'truncated': candidates > len(hits)})
    known = [row for row in outcomes if row['expected']]
    unknown = [row for row in outcomes if not row['expected']]
    top1 = ratio(sum(row['top1'] for row in known), len(known))
    top2 = ratio(sum(row['top2'] for row in known), len(known))
    rejected = ratio(sum(row['unknown_rejected'] for row in unknown), len(unknown))
    maximum = manifest.get('quality', {}).get('max_query_words', 450)
    passed = (bool(known) and len(outcomes) >= thresholds['min_tasks'] and len(unknown) >= thresholds['min_unknown']
              and top1['rate'] >= thresholds['min_top1'] and top2['rate'] >= thresholds['min_top2']
              and all(row['locations_ok'] and row['response_words'] <= maximum for row in outcomes))
    return {'evaluation': 'curated routing self-test; not an independent semantic/adoption trial',
            'passed': passed, 'thresholds': thresholds, 'task_count': len(outcomes),
            'top1': top1, 'top2': top2, 'unknown_rejection': rejected,
            'location_success': ratio(sum(row['locations_ok'] for row in outcomes), len(outcomes)),
            'max_response_words': max((row['response_words'] for row in outcomes), default=0),
            'word_count_method': 'whitespace proxy; not a tokenizer or cross-language segmentation measure',
            'semantic_accuracy': 'not measured', 'independent_adoption': 'not measured',
            'time_savings': 'not measured', 'tasks': outcomes}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('query', 'list', 'audit', 'build', 'check', 'evaluate'):
        sub = commands.add_parser(command)
        sub.add_argument('--root', type=Path, default=Path.cwd())
        if command == 'query':
            sub.add_argument('question')
            sub.add_argument('--limit', type=int, choices=range(1, 6), default=2)
            sub.add_argument('--json', action='store_true')
        if command == 'evaluate':
            sub.add_argument('--tasks', type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        manifest = load(root)
        if args.command == 'list':
            print('\n'.join(row['id'] + ': ' + row['title'] for row in manifest['routes']))
            return 0
        if args.command == 'query':
            hits = query(root, manifest, args.question, args.limit)
            candidate_count = len(rank(args.question, manifest['routes']))
            if args.json:
                emit({'query': args.question, 'candidate_count': candidate_count,
                      'truncated': candidate_count > len(hits), 'matches': hits})
            else:
                print(query_text(hits, candidate_count))
            return 1 if any(row.get('warning') for row in hits) else 0
        if args.command == 'evaluate':
            report = evaluate(root, manifest, read_json(args.tasks))
            emit(report)
            return 0 if report['passed'] else 1
        report = audit(root, manifest)
        if args.command == 'audit':
            emit(report)
            return 0 if report['ready'] else 1
        if not report['ready']:
            emit(report)
            return 1
        current = snapshot(root, manifest)
        if args.command == 'build':
            machine, human = index_paths(root)
            machine.parent.mkdir(parents=True, exist_ok=True)
            machine.write_text(json.dumps(current, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
            human.write_text(markdown_index(current), encoding='utf-8', newline='\n')
            emit({'built': len(current['routes']), 'outputs': [machine.relative_to(root).as_posix(), human.relative_to(root).as_posix()]})
            return 0
        stale = is_stale(root, current)
        emit({'valid': True, 'snapshot_stale': stale, 'ready': not stale,
              'route_count': len(current['routes']), 'structural_minimum': report['structural_minimum'],
              'scope': 'structure and drift, not semantic truth or runtime acceptance'})
        return 1 if stale else 0
    except (ValueError, OSError, SyntaxError, TypeError, KeyError) as error:
        emit({'valid': False, 'error': str(error)})
        return 1


if __name__ == '__main__':
    # Redirected Windows stdout may default to cp1252; reports include CJK queries.
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
