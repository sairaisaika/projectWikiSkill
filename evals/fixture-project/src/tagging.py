"""Minimal fixture: suggestions and effective tags deliberately stay separate."""


class Tagger:
    def suggest(self, title):
        raise NotImplementedError


def sanitize_suggestions(tagger, title):
    suggestions = tagger.suggest(title)
    if suggestions is None:
        return None
    return sorted({tag.strip().lower() for tag in suggestions if tag.strip()})


def resolve_tags(assertions):
    """Highest tier wins; conflicting operations at that tier are disputed."""
    if not assertions:
        return 'absent'
    highest = max(item['tier'] for item in assertions)
    operations = {item['op'] for item in assertions if item['tier'] == highest}
    if len(operations) != 1:
        return 'disputed'
    return 'present' if 'add' in operations else 'absent'


def effective_tag(assertions):
    return resolve_tags(assertions) == 'present'
