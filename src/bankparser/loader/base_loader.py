"""Abstract interface for loading raw bank extract content."""

from abc import ABC, abstractmethod


class Loader(ABC):
    """Loaders read an extract source and return its raw text content."""

    @abstractmethod
    def load(self, file_path: str) -> object:
        """Load and return raw text content from an extract path."""
        raise NotImplementedError
