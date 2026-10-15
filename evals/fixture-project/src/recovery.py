"""Pure synthetic recovery decisions: no requests, sleeps, threads or device IO."""

STATES = {'idle', 'running', 'backoff', 'done', 'failed'}
EVENTS = {'start', 'ok', 'timeout', 'retry', 'cancel'}
MAX_RETRIES = 2
BACKOFF_MS = 25
TRANSITIONS = {
    ('idle', 'start'): ('running', 'send'),
    ('running', 'ok'): ('done', 'commit'),
    ('running', 'timeout'): ('backoff', 'schedule_retry'),
    ('backoff', 'retry'): ('running', 'send'),
    ('running', 'cancel'): ('failed', 'stop'),
    ('backoff', 'cancel'): ('failed', 'stop'),
}


def retry_delay(attempt):
    if type(attempt) is not int or attempt < 0:
        raise ValueError('invalid attempt')
    return None if attempt >= MAX_RETRIES else BACKOFF_MS * 2 ** attempt


def next_action(state, event, attempt=0):
    if state not in STATES or event not in EVENTS:
        raise ValueError('invalid state or event')
    if state == 'backoff' and event == 'retry' and retry_delay(attempt) is None:
        return 'failed', 'exhausted'
    return TRANSITIONS.get((state, event), (state, 'ignored'))
