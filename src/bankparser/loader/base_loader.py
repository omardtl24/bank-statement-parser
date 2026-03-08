"""Abstract interface for loading raw bank extract content."""

from abc import ABC, abstractmethod


class Loader(ABC):
    """Loaders read an extract source and return its raw text content."""

    @abstractmethod
    def load(file_path: str) -> object:
        """Load raw extract content from a file path.

        Args:
            file_path: Path to the file that should be read.

        Returns:
            Implementation-defined raw content object.

        Raises:
            NotImplementedError: Always raised by the abstract base
                implementation. Concrete loaders must override this method.
        """
        raise NotImplementedError
