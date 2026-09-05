"""Turn resume and job-description text into meaningful evidence/requirement chunks."""

from __future__ import annotations

import re
from typing import Literal

from app.analysis.types import TextChunk

_BULLET_PREFIX = re.compile(
    r"^[\s]*([-\*•·–—▪►+]\s+|\d+[\.\)]\s+|[a-zA-Z][\.\)]\s+)"
)
_WHITESPACE = re.compile(r"[ \t\u00a0]+")

_RESUME_SECTION_HEADERS = {
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "work history",
    "education",
    "academic background",
    "skills",
    "technical skills",
    "core competencies",
    "areas of expertise",
    "projects",
    "personal projects",
    "academic projects",
    "key projects",
    "summary",
    "professional summary",
    "executive summary",
    "profile",
    "objective",
    "certifications",
    "certificates",
    "licenses",
    "awards",
    "honors",
    "publications",
    "volunteer experience",
}

_JD_REQUIREMENT_HEADERS = {
    "responsibilities",
    "key responsibilities",
    "duties",
    "core duties",
    "what you'll do",
    "what you will do",
    "the role",
    "about the role",
    "job description",
    "requirements",
    "minimum requirements",
    "basic qualifications",
    "minimum qualifications",
    "qualifications",
    "required qualifications",
    "required skills",
    "what we're looking for",
    "what you bring",
    "preferred qualifications",
    "desired skills",
    "nice to have",
    "bonus qualifications",
    "preferred requirements",
}

_JD_NON_REQUIREMENT_HEADERS = {
    "about us",
    "about the company",
    "who we are",
    "company overview",
    "our mission",
    "benefits",
    "perks",
    "what we offer",
    "compensation",
    "salary & benefits",
    "equal opportunity employer",
    "eeo statement",
    "diversity & inclusion",
    "how to apply",
}

_ALL_KNOWN_HEADERS = _RESUME_SECTION_HEADERS | _JD_REQUIREMENT_HEADERS | _JD_NON_REQUIREMENT_HEADERS

_EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_REGEX = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
_URL_REGEX = re.compile(r"https?://\S+|www\.\S+|linkedin\.com/\S+|github\.com/\S+")
_PAGE_MARKER = re.compile(r"^(?:page\s+\d+(?:\s+of\s+\d+)?|\d+\s*/\s*\d+)$", re.IGNORECASE)
_STANDALONE_DATE = re.compile(
    r"^(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}"
    r"|\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*"
    r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}"
    r"|\d{1,2}/\d{4}|\d{4}|present|current)$",
    re.IGNORECASE,
)

_PROTECTED_DOTS = [
    ("Node.js", "Node__DOT__js"),
    ("node.js", "node__DOT__js"),
    ("Next.js", "Next__DOT__js"),
    ("next.js", "next__DOT__js"),
    ("Vue.js", "Vue__DOT__js"),
    ("vue.js", "vue__DOT__js"),
    ("React.js", "React__DOT__js"),
    ("react.js", "react__DOT__js"),
    (".NET", "__DOT__NET"),
    (".net", "__DOT__net"),
    ("ASP.NET", "ASP__DOT__NET"),
    ("asp.net", "asp__DOT__net"),
    ("e.g.", "e__DOT__g__DOT__"),
    ("i.e.", "i__DOT__e__DOT__"),
    ("vs.", "vs__DOT__"),
    ("v1.", "v1__DOT__"),
    ("v2.", "v2__DOT__"),
]


def normalize_whitespace(text: str) -> str:
    """Normalize inline whitespace while preserving characters."""
    return _WHITESPACE.sub(" ", text).strip()


def is_section_header(text: str) -> bool:
    """Determine if a line is a section heading."""
    cleaned = text.strip()
    if cleaned.startswith(("#", "##", "###", "####")):
        return True
    cleaned = cleaned.rstrip(":").strip()
    if not cleaned:
        return True
    lowered = cleaned.lower()
    if lowered in _ALL_KNOWN_HEADERS:
        return True
    words = cleaned.split()
    if len(words) <= 5 and (cleaned.isupper() or (cleaned.istitle() and text.strip().endswith(":"))):
        return True
    return False


def _is_section_header(text: str) -> bool:
    """Backward compatibility alias for internal usage."""
    return is_section_header(text)


def is_non_requirement_section(header: str | None) -> bool:
    """Check if the active JD section is non-requirement text (e.g. benefits, about us)."""
    if not header:
        return False
    lowered = header.lower().rstrip(":").strip()
    return lowered in _JD_NON_REQUIREMENT_HEADERS


def is_administrative_content(text: str) -> bool:
    """Detect administrative lines like standalone emails, phones, URLs, dates, or page numbers."""
    cleaned = text.strip()
    if not cleaned:
        return True
    if _PAGE_MARKER.match(cleaned):
        return True
    if _STANDALONE_DATE.match(cleaned):
        return True

    # If the line is almost entirely a URL, email, or phone number with little or no natural text
    no_url = _URL_REGEX.sub("", cleaned).strip()
    no_email = _EMAIL_REGEX.sub("", no_url).strip()
    no_phone = _PHONE_REGEX.sub("", no_email).strip()

    alpha_count = sum(1 for c in no_phone if c.isalnum())
    if len(cleaned) >= 10 and alpha_count < 6:
        return True

    return False


def _protect_tokens(text: str) -> str:
    res = text
    for original, placeholder in _PROTECTED_DOTS:
        res = res.replace(original, placeholder)
    res = re.sub(r"(\d+)\.(\d+)", r"\1__DECIMAL__\2", res)
    return res


def _restore_tokens(text: str) -> str:
    res = text
    for original, placeholder in _PROTECTED_DOTS:
        res = res.replace(placeholder, original)
    res = res.replace("__DECIMAL__", ".")
    return res


def split_long_text(text: str, max_chars: int = 420) -> list[str]:
    """Split a text into sentences if it exceeds max_chars, keeping coherent sentences intact."""
    if len(text) <= max_chars:
        return [text]

    protected = _protect_tokens(text)
    raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'\(]|$)", protected)
    sentences = [_restore_tokens(s).strip() for s in raw_sentences if s.strip()]

    if not sentences:
        return [text[:max_chars].strip()]

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        extra = len(sentence) + (1 if current else 0)
        if current and (current_len + extra > max_chars):
            chunks.append(" ".join(current))
            current = [sentence]
            current_len = len(sentence)
        else:
            current.append(sentence)
            current_len += extra

    if current:
        chunks.append(" ".join(current))
    return chunks


def extract_section_chunks(
    text: str,
    source: Literal["resume", "job"] = "resume",
    min_chars: int = 20,
    max_chars: int = 420,
) -> list[tuple[str, str | None]]:
    """Extract (chunk_text, section_header) tuples while tracking section context."""
    if not text or not text.strip():
        return []

    raw_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    candidates: list[tuple[str, str | None]] = []
    current_section: str | None = None
    recognized_structural_lines = 0

    for raw_line in raw_lines:
        line = raw_line.strip()
        if not line:
            continue

        if is_section_header(line):
            current_section = line.lstrip("#").rstrip(":").strip()
            recognized_structural_lines += 1
            continue

        if source == "job" and is_non_requirement_section(current_section):
            recognized_structural_lines += 1
            continue

        if is_administrative_content(line):
            recognized_structural_lines += 1
            continue

        stripped = _BULLET_PREFIX.sub("", line).strip()
        if not stripped:
            continue

        normalized = normalize_whitespace(stripped)
        split_units = split_long_text(normalized, max_chars)
        for unit in split_units:
            candidates.append((unit, current_section))

    if not candidates and recognized_structural_lines == 0:
        fallback = normalize_whitespace(text)
        if (
            fallback
            and not is_section_header(fallback)
            and not is_administrative_content(fallback)
        ):
            for unit in split_long_text(fallback, max_chars):
                candidates.append((unit, None))

    seen: set[str] = set()
    result: list[tuple[str, str | None]] = []
    for chunk, section in candidates:
        if len(chunk) < min_chars:
            continue
        key = chunk.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append((chunk, section))

    return result


def split_into_chunks(text: str, min_chars: int = 20, max_chars: int = 420) -> list[str]:
    """Split free text into bullet/sentence chunks suitable for embedding."""
    return [
        chunk
        for chunk, _ in extract_section_chunks(
            text, source="resume", min_chars=min_chars, max_chars=max_chars
        )
    ]


def to_text_chunks(
    text: str,
    source: Literal["resume", "job"],
    min_chars: int = 20,
    max_chars: int = 420,
) -> list[TextChunk]:
    """Convert text into TextChunk objects preserving section context."""
    prefix = "ev" if source == "resume" else "req"
    items = extract_section_chunks(
        text, source=source, min_chars=min_chars, max_chars=max_chars
    )
    return [
        TextChunk(id=f"{prefix}_{index}", text=chunk, source=source, section=section)
        for index, (chunk, section) in enumerate(items)
    ]
