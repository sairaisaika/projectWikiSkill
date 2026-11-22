"""Terminal CLI v0: find/status/eval fail closed and keep witnessed measurement opt-in and strict."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
HELPER = REPO / 'project-wiki/scripts/wiki.py'
spec = importlib.util.spec_from_file_location('wiki_terminal', HELPER)
wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiki)

KNOWN = 'Change the ArticleSource failure contract'


def header(project='Synthetic interface fixture', **extra):
    return {'record': 'ledger', 'schema_version': 1, 'project': project, 'data_class': 'synthetic', 'predicate_version': 'p1', **extra}


def baseline(id, query, seconds=40):
    return {'record': 'baseline', 'id': id, 'query': query, 'method': 'repo-wide grep', 'elapsed_seconds': seconds}


def trial(id, query, route='public-api', condition='wiki', witness='independent', eligible=True, seconds=10, baseline_id=None, **extra):
    found = route is not None
    return {'record': 'trial', 'id': id, 'query': query, 'condition': condition, 'witness': witness, 'eligible': eligible,
            'route_id': route, 'found': found, 'cold': True, 'used': condition == 'wiki' and eligible and found, 'elapsed_seconds': seconds, 'baseline_id': baseline_id, **extra}


class TerminalCliTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'project'
        shutil.copytree(REPO / 'evals/fixture-project', self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.root = self.root.resolve()
        self.manifest = wiki.load(self.root)

    def call(self, *args, root=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = wiki.main([*args, '--root', str(root or self.root)])
        return code, output.getvalue()

    def call_json(self, *args, root=None):
        code, output = self.call(*args, root=root)
        return code, json.loads(output)

    def ledger(self, *records):
        path = self.root / 'ledger.jsonl'
        path.write_text(''.join(json.dumps(item) + '\n' for item in records), encoding='utf-8')
        return path

    # find

    def test_find_returns_owner_sections_and_hashed_evidence(self):
        code, result = self.call_json('find', KNOWN, '--json')
        self.assertEqual(code, 0)
        self.assertTrue(result['determinable'])
        self.assertEqual(result['owner']['route_id'], 'public-api')
        self.assertIn('docs/wiki/interfaces.md#public-api', result['sections'])
        self.assertEqual({item['role'] for item in result['evidence']['locations']}, {'declaration', 'implementation', 'consumer'})
        self.assertTrue(all(len(item['sha256']) == 64 and item['line'] > 0 for item in result['evidence']['locations']))
        self.assertEqual(result['match']['candidate_count'], 1)
        code, text = self.call('find', KNOWN)
        self.assertEqual(code, 0)
        self.assertTrue(text.startswith('OWNER public-api:'))
        self.assertIn('section: docs/wiki/interfaces.md#public-api', text)

    def test_find_unknown_question_fails_closed_without_guessing(self):
        code, result = self.call_json('find', 'deploy the helm chart to kubernetes', '--json')
        self.assertEqual(code, 1)
        self.assertEqual(result, {'determinable': False, 'reason': 'unknown', 'detail': result['detail'], 'candidate_count': 0})
        self.assertNotIn('owner', result)

    def test_find_fails_closed_on_stale_index_until_build(self):
        source = self.root / self.manifest['routes'][0]['sources'][1]['path']
        source.write_text('# moved\n' + source.read_text(encoding='utf-8'), encoding='utf-8')
        code, result = self.call_json('find', KNOWN, '--json')
        self.assertEqual((code, result['determinable'], result['reason']), (1, False, 'stale_index'))
        self.assertNotIn('owner', result)
        self.assertEqual(self.call('build')[0], 0)
        code, result = self.call_json('find', KNOWN, '--json')
        self.assertEqual((code, result['owner']['route_id']), (0, 'public-api'))

    def test_find_fails_closed_on_invalid_wiki(self):
        self.manifest['routes'][0]['sources'][1]['symbol'] = 'does_not_exist'
        (self.root / 'docs/wiki/routes.json').write_text(json.dumps(self.manifest), encoding='utf-8')
        code, result = self.call_json('find', KNOWN, '--json')
        self.assertEqual((code, result['reason']), (1, 'invalid_wiki'))
        self.assertIn('public-api', result['detail'])

    def test_find_without_wiki_reports_no_wiki_and_exit_2(self):
        empty = Path(self.temporary.name) / 'empty'
        empty.mkdir()
        code, result = self.call_json('find', KNOWN, '--json', root=empty)
        self.assertEqual((code, result['determinable'], result['reason'], result['error_code']), (2, False, 'no_wiki', 'helper_manifest_missing'))

    def test_find_tie_is_ambiguous_not_first_match(self):
        twin = dict(self.manifest['routes'][0], id='public-api-twin', title='Twin of public API')
        self.manifest['routes'].append(twin)
        (self.root / 'docs/wiki/routes.json').write_text(json.dumps(self.manifest), encoding='utf-8')
        self.assertEqual(self.call('build')[0], 0)
        code, result = self.call_json('find', 'ArticleSource', '--json')
        self.assertEqual((code, result['reason']), (1, 'ambiguous'))
        self.assertEqual(set(result['candidates']), {'public-api', 'public-api-twin'})

    # status

    def test_status_gate_follows_index_freshness(self):
        code, result = self.call_json('status')
        self.assertEqual((code, result['find_gate'], result['route_count']), (0, 'open', 9))
        self.assertTrue(result['measurement'].startswith('not measured'))
        source = self.root / self.manifest['routes'][0]['sources'][1]['path']
        source.write_text(source.read_text(encoding='utf-8') + '\n# touched\n', encoding='utf-8')
        code, result = self.call_json('status')
        self.assertEqual((code, result['find_gate'], result['closed_reason']), (1, 'closed', 'stale_index'))

    # eval

    def test_eval_without_ledger_marks_witnessed_tiers_not_measured(self):
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'))
        self.assertEqual(code, 0)
        self.assertTrue(result['passed'])
        self.assertTrue(result['tiers']['fixture_reachability']['passed'])
        self.assertEqual(result['tiers']['fixture_reachability']['top1'], {'numerator': 24, 'denominator': 24, 'rate': 1.0})
        for tier in ('cold_discovery', 'eligible_use', 'time_savings', 'negative_controls'):
            self.assertEqual(result['tiers'][tier], 'not measured')
        self.assertFalse(result['ledger_supplied'])

    def test_compound_eval_does_not_treat_overlap_as_complete(self):
        report = {'passed': True, 'tasks': [
            {'id': 'compound', 'expected': ['A', 'B'], 'actual': ['A', 'C'],
             'top2': True, 'locations_ok': True}
        ]}
        with patch.object(wiki, 'evaluate', return_value=report):
            alternative = wiki.tiered_eval(self.root, self.manifest, {})
            result = wiki.tiered_eval(self.root, {'routes': [{'id': 'A'}, {'id': 'B'}, {'id': 'C'}]},
                                      {'tasks': [{'id': 'compound', 'required_routes': ['A', 'B']}]})
        self.assertTrue(alternative['passed'])
        self.assertEqual(alternative['tiers']['fixture_reachability']['compound_cases'], [])
        fixture = result['tiers']['fixture_reachability']
        self.assertFalse(result['passed'])
        self.assertTrue(fixture['tasks'][0]['top2'])
        self.assertTrue(fixture['tasks'][0]['locations_ok'])
        self.assertEqual(fixture['compound_cases'], [
            {'id': 'compound', 'missing_routes': ['B'], 'unexpected_routes': ['C'], 'passed': False}
        ])
        self.assertEqual(fixture['compound_exact'], {'numerator': 0, 'denominator': 1, 'rate': 0.0})

    def test_eval_with_vetted_ledger_reports_each_tier_with_denominators(self):
        other = 'What if an external source has no counts capability?'
        path = self.ledger(header(), baseline('b1', KNOWN, 45), baseline('b2', other, 30),
                           trial('t1', KNOWN, seconds=12, baseline_id='b1'),
                           trial('t2', other, route='external-source', seconds=20, baseline_id='b2', witness='self'),
                           trial('t3', 'rotate the archive key', route=None, eligible=False),
                           trial('t4', KNOWN, route=None, condition='stale'),
                           trial('t5', KNOWN, route=None, condition='no-wiki'))
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        self.assertEqual(code, 0)
        tiers = result['tiers']
        self.assertEqual(tiers['cold_discovery'], {'numerator': 1, 'denominator': 1, 'rate': 1.0})
        self.assertEqual(tiers['eligible_use'], {'numerator': 2, 'denominator': 2, 'rate': 1.0})
        self.assertEqual(tiers['time_savings'], 'not measured')
        self.assertEqual(tiers['negative_controls'], {'stale': {'numerator': 1, 'denominator': 1, 'rate': 1.0},
                                                      'no-wiki': {'numerator': 1, 'denominator': 1, 'rate': 1.0}})
        witnessed = tiers['witnessed']
        self.assertEqual(witnessed['self_witnessed_discovery'], {'numerator': 1, 'denominator': 1, 'rate': 1.0})
        self.assertEqual(witnessed['unknown_under_wiki'], {'count': 1})
        self.assertEqual(witnessed['routing_agreement'], {'numerator': 2, 'denominator': 2, 'rate': 1.0})
        self.assertTrue(witnessed['probe_validated'])
        self.assertEqual(witnessed['control_anomalies'], [])
        self.assertTrue(result['ledger_supplied'])
        self.assertNotIn(path.as_posix(), json.dumps(result))

    def test_eval_ledger_without_pairs_or_controls_makes_no_savings_claim(self):
        path = self.ledger(header(), trial('t1', KNOWN, witness='self'))
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        self.assertEqual(code, 0)
        tiers = result['tiers']
        self.assertEqual(tiers['cold_discovery'], 'not measured')
        self.assertEqual(tiers['time_savings'], 'not measured')
        self.assertEqual(tiers['negative_controls'], {'stale': 'not measured', 'no-wiki': 'not measured'})
        self.assertFalse(tiers['witnessed']['probe_validated'])

    def test_discovery_is_not_use_and_one_clean_control_is_not_validation(self):
        path = self.ledger(header(), trial('t1', KNOWN, used=False),
                           trial('t2', KNOWN, route=None, condition='stale'))
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        self.assertEqual(code, 0)
        self.assertEqual(result['tiers']['cold_discovery']['numerator'], 1)
        self.assertEqual(result['tiers']['eligible_use']['numerator'], 0)
        self.assertFalse(result['tiers']['witnessed']['probe_validated'])

    def test_eval_control_that_finds_a_route_is_an_anomaly_not_validation(self):
        path = self.ledger(header(), trial('t1', KNOWN), trial('t2', KNOWN, condition='no-wiki'))
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        self.assertEqual(code, 0)
        witnessed = result['tiers']['witnessed']
        self.assertEqual(witnessed['control_anomalies'], ['no-wiki'])
        self.assertFalse(witnessed['probe_validated'])
        self.assertEqual(result['tiers']['negative_controls']['no-wiki'], {'numerator': 0, 'denominator': 1, 'rate': 0.0})

    def test_eval_rejects_defective_ledgers_without_partial_results(self):
        cases = {
            'empty': [],
            'missing_header': [trial('t1', KNOWN)],
            'second_header': [header(), header()],
            'project_mismatch': [header(project='Another project'), trial('t1', KNOWN)],
            'private_data_class': [header(data_class='private'), trial('t1', KNOWN)],
            'unexpected_field': [header(), trial('t1', KNOWN, transcript='raw')],
            'missing_field': [header(), {key: value for key, value in trial('t1', KNOWN).items() if key != 'witness'}],
            'duplicate_id': [header(), trial('t1', KNOWN), trial('t1', KNOWN)],
            'id_shared_with_baseline': [header(), baseline('x', KNOWN), trial('x', KNOWN)],
            'unknown_route': [header(), trial('t1', KNOWN, route='no-such-route')],
            'found_without_route': [header(), dict(trial('t1', KNOWN, route=None), found=True)],
            'route_without_found': [header(), dict(trial('t1', KNOWN), found=False)],
            'reused_baseline': [header(), baseline('b1', KNOWN), trial('t1', KNOWN, baseline_id='b1'), trial('t2', KNOWN, baseline_id='b1')],
            'contradictory_use': [header(), trial('t1', KNOWN, route=None, used=True)],
            'huge_seconds': [header(), trial('t1', KNOWN, seconds=10**400)],
            'nonscalar_condition': [header(), dict(trial('t1', KNOWN), condition=['wiki'])],
            'dangling_baseline': [header(), trial('t1', KNOWN, baseline_id='b9')],
            'baseline_query_mismatch': [header(), baseline('b1', 'another question'), trial('t1', KNOWN, baseline_id='b1')],
            'unknown_record': [header(), {'record': 'session', 'id': 's1'}],
            'bad_condition': [header(), trial('t1', KNOWN, condition='prod')],
            'negative_seconds': [header(), trial('t1', KNOWN, seconds=-1)],
            'boolean_seconds': [header(), trial('t1', KNOWN, seconds=True)],
        }
        for name, records in cases.items():
            with self.subTest(name):
                path = self.ledger(*records)
                code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
                self.assertEqual(code, 1)
                self.assertEqual(set(result), {'valid', 'error'})
                self.assertFalse(result['valid'])
                self.assertIn('ledger', result['error'])
        path = self.root / 'ledger.jsonl'
        path.write_text(json.dumps(header()) + '\n\n' + json.dumps(trial('t1', KNOWN)) + '\n', encoding='utf-8')
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        self.assertEqual((code, result['valid']), (1, False))
        self.assertIn('line 2: blank line', result['error'])
        path.write_text('{not json\n', encoding='utf-8')
        code, result = self.call_json('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        self.assertEqual((code, result['valid']), (1, False))
        self.assertIn('line 1: invalid JSON', result['error'])

    def test_ledger_rejects_without_echoing_values_and_wrong_owner_does_not_validate(self):
        path = self.ledger(header(project='DO_NOT_ECHO'), trial('t1', KNOWN))
        args = ('eval', '--tasks', str(REPO / 'evals/tasks.json'), '--ledger', str(path))
        code, output = self.call(*args)
        self.assertEqual(code, 1)
        self.assertNotIn('DO_NOT_ECHO', output)
        self.assertNotIn(str(path), output)
        path.write_text('{"record":"ledger","record":"ledger"}', encoding='utf-8')
        code, output = self.call(*args)
        self.assertEqual(code, 1)
        self.assertIn('duplicate field', output)
        path = self.ledger(header(predicate_version='DO_NOT_ECHO'),
                           trial('DO_NOT_ECHO', KNOWN, route='external-source'),
                           trial('t2', KNOWN, route=None, condition='stale'),
                           trial('t3', KNOWN, route=None, condition='no-wiki'))
        code, output = self.call(*args)
        self.assertEqual(code, 0)
        self.assertNotIn('DO_NOT_ECHO', output)
        self.assertFalse(json.loads(output)['tiers']['witnessed']['probe_validated'])

    def test_existing_commands_and_import_surface_are_unchanged(self):
        code, output = self.call('evaluate', '--tasks', str(REPO / 'evals/tasks.json'))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output), wiki.evaluate(self.root, self.manifest, wiki.read_json(REPO / 'evals/tasks.json')))
        source = HELPER.read_text(encoding='utf-8')
        self.assertNotIn('import os', source)
        self.assertNotIn('subprocess', source)


if __name__ == '__main__':
    unittest.main()
