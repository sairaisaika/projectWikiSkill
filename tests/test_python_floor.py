"""User-facing helpers refuse an unsupported interpreter with an actionable message."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'project-wiki/scripts'


def load(name):
    spec = importlib.util.spec_from_file_location(f'python_floor_{name}', SCRIPTS / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PythonFloorTests(unittest.TestCase):
    def test_old_interpreter_exits_before_any_command_work(self):
        for name in ('wiki', 'workflow'):
            module = load(name)
            err = io.StringIO()
            with self.subTest(script=name), patch.object(sys, 'version_info', (3, 9, 6, 'final', 0)), \
                    contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as raised:
                module.main(['--help'])
            self.assertEqual(raised.exception.code, 2)
            self.assertIn('needs Python 3.10+', err.getvalue())
            self.assertIn('3.9.6', err.getvalue())

    def test_supported_interpreter_passes_the_guard(self):
        for name in ('wiki', 'workflow'):
            with self.subTest(script=name):
                self.assertIsNone(load(name).require_supported_python())


if __name__ == '__main__':
    unittest.main()
