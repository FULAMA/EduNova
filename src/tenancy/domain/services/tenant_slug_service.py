import re
import unicodedata
from collections.abc import Callable
from uuid import uuid4


class TenantSlugService:
    """Domain service responsible for tenant slug normalization and collision handling.

    Transforms establishment names into clean, URL-safe identifiers and ensures
    uniqueness by resolving potential collisions.
    """

    @staticmethod
    def normalize_slug(name: str) -> str:
        """Normalizes an establishment name into an ASCII URL-safe slug.

        - Decomposes accents (NFKD) and removes non-spacing marks.
        - Converts to lowercase.
        - Replaces punctuation, whitespace, and special characters with hyphens.
        - Collapses consecutive hyphens and strips outer hyphens.
        - Defaults to 'etablissement' if the resulting slug is empty.
        """
        if not name or not name.strip():
            return "etablissement"

        # Normalize unicode and strip accents
        normalized = unicodedata.normalize("NFKD", name.strip())
        ascii_text = "".join(c for c in normalized if not unicodedata.combining(c))

        # Convert to lower and replace non-alphanumeric with hyphens
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_text.lower())
        slug = re.sub(r"-+", "-", slug).strip("-")

        return slug if slug else "etablissement"

    @classmethod
    def generate_unique_slug(
        cls,
        name: str,
        is_slug_taken: Callable[[str], bool],
        max_attempts: int = 100,
    ) -> str:
        """Generates a guaranteed unique slug for an establishment.

        Checks against an existing slug lookup (such as repository.find_by_slug).
        If a collision occurs, appends an incrementing counter (-2, -3...) or a
        short random suffix if the attempt threshold is reached.
        """
        base_slug = cls.normalize_slug(name)

        if not is_slug_taken(base_slug):
            return base_slug

        # Progressive numeric suffix: e.g. 'cs-malula-2', 'cs-malula-3'
        for counter in range(2, max_attempts + 2):
            candidate = f"{base_slug}-{counter}"
            if not is_slug_taken(candidate):
                return candidate

        # Ultimate fallback with short hex suffix if all sequential attempts collided
        hex_suffix = uuid4().hex[:6]
        return f"{base_slug[:40]}-{hex_suffix}"
