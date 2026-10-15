"""Actual offline checks for the tiny Python fixture only."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from service import get_articles
from client import read_articles
from tagging import effective_tag, resolve_tags, sanitize_suggestions


class ContractTests(unittest.TestCase):
    def test_unavailable_differs_from_empty_and_legacy_client_is_preserved(self):
        class Source:
            def __init__(self, rows):
                self.rows = rows

            def list_articles(self, query):
                return self.rows

        self.assertEqual(get_articles(Source(None), {})['error'], 'unavailable')
        self.assertEqual(get_articles(Source([]), {}), {'ok': True, 'data': []})
        self.assertIsNone(read_articles(get_articles, Source(None), {}))
        self.assertEqual(read_articles(get_articles, Source([]), {}), [])

    def test_equal_tier_conflict_is_not_an_effective_tag(self):
        assertions = [{'tier': 2, 'op': 'add'}, {'tier': 2, 'op': 'remove'}]
        self.assertEqual(resolve_tags(assertions), 'disputed')
        self.assertFalse(effective_tag(assertions))

    def test_model_failure_is_not_an_empty_suggestion(self):
        class Model:
            def suggest(self, title):
                return None

        self.assertIsNone(sanitize_suggestions(Model(), 'Example'))


if __name__ == '__main__':
    unittest.main()
