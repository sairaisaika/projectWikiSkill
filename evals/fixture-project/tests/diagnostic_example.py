"""Fixture-specific diagnostic acceptance; no logging, IO or production schema."""
import re

CONTRACT = 'article-result/v1'
BUILD = 'fixture-source-v1'
# Bound to the existing native declarations, implementation and consumer.
SOURCE_HASHES = {'src/ports.py': '039afac6ce19d88d0638111d3c4201a609d78c9d21add0b1ab51932a240c6028', 'src/service.py': 'bc11b983be14dbe2f219a98da6bf93963355f3266cbf8ad4c0474ad70f75d786', 'src/client.py': 'f97d14a3cd5188902208f5aaa3b458544f9740e5537f298468f2db0decf00388'}
FIELDS = {'timestamp', 'service', 'build', 'environment', 'operation', 'event',
          'outcome', 'error_code', 'failure_class', 'retry', 'data_state',
          'correlation_id', 'contract'}
VALUES = {
    'service': {'article-service', 'legacy-client'},
    'event': {'service.result', 'client.result', 'service.accepted'},
    'outcome': {'succeeded', 'failed', 'accepted', 'queued'},
    'error_code': {'none', 'unavailable', 'legacy_none', 'unknown'},
    'failure_class': {'none', 'known', 'unknown'},
    'retry': {'not_applicable', 'unknown'},
    'data_state': {'empty', 'present', 'unavailable', 'unknown'},
}


def event(component, data, correlation='synthetic-op-1'):
    """Construct invented observations only; this is not a production redactor."""
    failed = data is None
    return {'timestamp': '2000-01-01T00:00:00Z', 'service': component,
            'build': BUILD, 'environment': 'synthetic', 'operation': 'article.read',
            'event': 'service.result' if component == 'article-service' else 'client.result',
            'outcome': 'failed' if failed else 'succeeded',
            'error_code': ('unavailable' if component == 'article-service' else 'legacy_none') if failed else 'none',
            'failure_class': ('known' if component == 'article-service' else 'unknown') if failed else 'none',
            'retry': 'unknown' if failed else 'not_applicable',
            'data_state': 'unavailable' if failed else ('empty' if not data else 'present'),
            'correlation_id': correlation, 'contract': CONTRACT}


def assess(packet):
    """Return safe categorical findings only; never interpolate supplied values."""
    def answer(status, reason, observed=()):
        return {'status': status, 'reason': reason, 'observed': list(observed),
                'runtime': 'unverified'}

    events = packet.get('events')
    if not isinstance(events, list):
        return answer('unusable', 'invalid_packet')
    if len(events) > 2:
        return answer('unusable', 'noisy_or_ambiguous')
    for row in events:
        if not isinstance(row, dict) or set(row) != FIELDS:
            return answer('unusable', 'field_allowlist')
        if any(not isinstance(value, str) for value in row.values()):
            return answer('unusable', 'invalid_category')
        if any(row[key] not in options for key, options in VALUES.items()):
            return answer('unusable', 'invalid_category')
        if (row['build'] != BUILD or row['contract'] != CONTRACT
                or row['environment'] != 'synthetic' or row['operation'] != 'article.read'
                or row['timestamp'] != '2000-01-01T00:00:00Z'
                or not re.fullmatch(r'synthetic-op-[0-9]+', row['correlation_id'])):
            return answer('unusable', 'unbound_evidence')
    observed = [row['event'] + ':' + row['outcome'] for row in events]
    if packet.get('coverage') != 'complete':
        return answer('unknown', 'coverage_gap', observed)
    if len(events) != 2 or {row['event'] for row in events} != {'service.result', 'client.result'}:
        return answer('unknown', 'terminal_pair_missing', observed)
    if len({row['correlation_id'] for row in events}) != 1:
        return answer('unusable', 'operation_not_joined', observed)
    by_event = {row['event']: row for row in events}
    producer, consumer = by_event['service.result'], by_event['client.result']
    state = producer['data_state']
    # Compare a bounded observation to the actual fixture's declared mapping.
    rows = None if state == 'unavailable' else ([] if state == 'empty' else ['synthetic'])
    expected = [event('article-service', rows, producer['correlation_id']),
                event('legacy-client', rows, producer['correlation_id'])]
    if [producer, consumer] != expected:
        return answer('contract_mismatch', 'observed_mapping_differs', observed)
    return answer('consistent_error' if rows is None else 'consistent_success',
                  'offline_mapping_only', observed)
