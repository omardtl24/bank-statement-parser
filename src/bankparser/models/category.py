from dataclasses import dataclass, field


@dataclass(slots=True)
class Subcategory:
    """Represents a transaction subcategory within a parent category."""

    name: str


@dataclass(slots=True)
class Category:
    """Represents a transaction category and its available subcategories."""

    name: str
    subcategories: list[Subcategory] = field(default_factory=list)
