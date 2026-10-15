"""Independent vectors/boundaries of the actual synthetic implementations."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from heartbeat import decode_heartbeat, encode_heartbeat
from recovery import next_action, retry_delay


class EngineeringContracts(unittest.TestCase):
    def test_exact_network_order_vector_and_decode(self):
        payload = bytes.fromhex('01 03 00 08 01 02 03 04')
        self.assertEqual(encode_heartbeat(3, 0x01020304), payload)
        self.assertEqual(decode_heartbeat(payload), {'version': 1, 'flags': 3, 'length': 8, 'sequence': 0x01020304})

    def test_rejects_wrong_size_header_and_reserved_flags(self):
        for payload in [b'', bytes.fromhex('02 00 00 08 00 00 00 01'),
                        bytes.fromhex('01 04 00 08 00 00 00 01'), bytes.fromhex('01 00 00 09 00 00 00 01')]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                decode_heartbeat(payload)
        with self.assertRaises(ValueError):
            encode_heartbeat(4, 1)

    def test_timeout_then_retry_has_bounded_decision_and_backoff(self):
        self.assertEqual(next_action('running', 'timeout'), ('backoff', 'schedule_retry'))
        self.assertEqual(retry_delay(0), 25)
        self.assertEqual(retry_delay(1), 50)
        self.assertIsNone(retry_delay(2))
        self.assertEqual(next_action('backoff', 'retry', 1), ('running', 'send'))
        self.assertEqual(next_action('backoff', 'retry', 2), ('failed', 'exhausted'))

    def test_late_reply_or_retry_cannot_repeat_commit_after_terminal(self):
        self.assertEqual(next_action('running', 'ok'), ('done', 'commit'))
        for state in ['done', 'failed']:
            for event in ['start', 'ok', 'timeout', 'retry', 'cancel']:
                self.assertEqual(next_action(state, event), (state, 'ignored'))

    def test_cancel_and_invalid_inputs(self):
        self.assertEqual(next_action('backoff', 'cancel'), ('failed', 'stop'))
        with self.assertRaises(ValueError):
            next_action('unknown', 'start')
        with self.assertRaises(ValueError):
            retry_delay(-1)

    def test_late_reply_during_backoff_and_after_retry_have_different_meaning(self):
        self.assertEqual(next_action('backoff', 'ok'), ('backoff', 'ignored'))
        state, action = next_action('backoff', 'retry', 0)
        self.assertEqual(action, 'send')
        # No request/generation identity exists: any ok at running can commit.
        self.assertEqual(next_action(state, 'ok'), ('done', 'commit'))

    def test_retry_bound_depends_on_caller_and_attempt_validation_is_branch_local(self):
        state = 'running'
        for _ in range(3):
            state, _ = next_action(state, 'timeout')
            state, action = next_action(state, 'retry', 0)
            self.assertEqual((state, action), ('running', 'send'))
        self.assertEqual(next_action('done', 'retry', -1), ('done', 'ignored'))
        with self.assertRaises(ValueError):
            next_action('backoff', 'retry', -1)

    def test_wire_uint32_does_not_imply_strict_python_integer_type(self):
        self.assertEqual(encode_heartbeat(0, True), bytes.fromhex('01 00 00 08 00 00 00 01'))


if __name__ == '__main__':
    unittest.main()
