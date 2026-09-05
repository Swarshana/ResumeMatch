"""Lightweight requirement-importance cues. Defaults to unspecified when unsure."""

from __future__ import annotations

import re

from app.analysis.types import RequirementImportance

_REQUIRED = re.compile(
    r"\b(required|must have|must be|mandatory|minimum of)\b",
    re.IGNORECASE,
)
_PREFERRED = re.compile(
    r"\b(preferred|nice to have|nice-to-have|optional|a plus|bonus)\b",
    re.IGNORECASE,
)


def detect_importance(text: str, section: str | None = None) -> RequirementImportance:
    """Tag a requirement as required, preferred, or unspecified.

    This is a conservative cue layer, not NLP classification. Ambiguous text
    stays unspecified so later work can replace this module without touching matching.
    """
    has_required = bool(_REQUIRED.search(text))
    has_preferred = bool(_PREFERRED.search(text))
    if has_required and not has_preferred:
        return "required"
    if has_preferred and not has_required:
        return "preferred"

    if section:
        sec_required = bool(_REQUIRED.search(section))
        sec_preferred = bool(_PREFERRED.search(section))
        if sec_required and not sec_preferred and not has_preferred:
            return "required"
        if sec_preferred and not sec_required and not has_required:
            return "preferred"

    return "unspecified"
