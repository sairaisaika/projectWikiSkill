"""Synthetic dependency contract; no provider or IO is implemented here."""
from typing import Protocol


class ArticleSource(Protocol):
    def list_articles(self, query):
        """Return list on success (possibly empty); None if unavailable."""
        ...
