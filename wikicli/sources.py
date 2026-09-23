"""Read original sources from vault/raw/ and split them into titled sections.

Sections are the unit for wiki notes (one subject each) and the parent of the
retrieval chunks, so every passage keeps its file path, section and PDF page.
"""

import hashlib
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import config

# Course per source file. The file name prefix is the source ID convention.
COURSES = {
    "leading-people": "Leading People",
    "micro": "Microeconomics",
    "data-and-decisions": "Data and Decisions",
    "marketing": "Marketing",
    "finance": "Finance",
    "buscomm": "Business Communication",
}


@dataclass
class Section:
    source_id: str      # file stem, e.g. "micro-final-cheat-sheet"
    path: str           # path relative to the vault, e.g. "raw/micro-final-cheat-sheet.md"
    course: str
    title: str          # heading from the original, cleaned
    text: str
    page: int | None = None     # first PDF page of the section (1-based)
    pages: list = field(default_factory=list)  # (page, char_offset) markers inside text

    @property
    def section_id(self) -> str:
        return f"{self.source_id}#{slug(self.title)}"

    @property
    def digest(self) -> str:
        return hashlib.sha1(self.text.encode("utf-8")).hexdigest()[:12]


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "section"


def course_for(source_id: str) -> str:
    for prefix, course in COURSES.items():
        if source_id.startswith(prefix):
            return course
    return "General"


def clean_heading(line: str) -> str:
    """'# **1\\. MARKETING FOUNDATIONS**' -> 'Marketing Foundations'."""
    text = re.sub(r"^#+\s*", "", line)
    text = text.replace("\\", "").replace("*", "").strip()
    text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)          # drop numbering like 1.1
    text = re.sub(r"\s*\((Session|Sessions) [^)]*\)$", "", text)
    text = re.sub(r"^Session \d+:\s*", "", text)
    if text.isupper():
        text = text.title()
    return text.strip(" :") or "Overview"


def list_sources(target: Path | None = None) -> list[Path]:
    """All supported files in raw/, or a single file/folder given on the command line."""
    target = target or config.RAW_DIR
    if target.is_file():
        return [target]
    return sorted(p for p in target.iterdir() if p.suffix.lower() in {".md", ".txt", ".pdf"})


def load_sections(path: Path) -> list[Section]:
    source_id = path.stem
    rel = path.resolve().relative_to(config.VAULT.resolve()).as_posix()
    course = course_for(source_id)
    if path.suffix.lower() == ".pdf":
        return _pdf_sections(path, source_id, rel, course)
    text = path.read_text(encoding="utf-8")
    return _markdown_sections(text, source_id, rel, course)


# ---------------------------------------------------------------- Markdown / text

_MD_HEADING = re.compile(r"^(#{1,3})\s+\S")
_CAPS_HEADING = re.compile(r"^[A-Z][A-Z /&()\-]{3,}$")
SINGLE_SECTION_MAX = 5000   # short documents (essays, cases) stay whole: one subject
SPLIT_ABOVE = 4000         # sections longer than this are split at the next heading level


def _level(line: str, caps_as_headings: bool) -> int | None:
    """Heading depth of a line (1-3), or None. ALL-CAPS lines count as level 1 in plain cheat sheets."""
    m = _MD_HEADING.match(line)
    if m:
        return len(m.group(1))
    if caps_as_headings and _CAPS_HEADING.match(line.strip()):
        return 1
    return None


def _markdown_sections(text, source_id, rel, course) -> list[Section]:
    lines = text.splitlines()
    doc_title = source_id.replace("-", " ").title()
    # A single "# Title" on the first line is the document title, not a section.
    if lines and lines[0].startswith("# ") and sum(l.startswith("# ") for l in lines) == 1:
        doc_title = clean_heading(lines[0])
        lines = lines[1:]
    body = "\n".join(lines).strip()
    if len(body) <= SINGLE_SECTION_MAX:
        return [Section(source_id, rel, course, doc_title, body)]

    caps = not any(_MD_HEADING.match(l) for l in lines)
    sections = [Section(source_id, rel, course, t, b)
                for t, b in _split(lines, caps, doc_title)]
    return _unique_titles(_merge_small(sections))


def _split(lines: list[str], caps: bool, title: str, min_level: int = 1) -> list[tuple[str, str]]:
    """Split at the shallowest heading level present; re-split only sections that are too long."""
    levels = [lv for l in lines if (lv := _level(l, caps)) and lv >= min_level]
    if not levels:
        return [(title, "\n".join(lines).strip())]
    top = min(levels)
    parts, cur_title, buf = [], title, []
    for line in lines:
        if _level(line, caps) == top:
            if "\n".join(buf).strip():
                parts.append((cur_title, buf))
            cur_title, buf = clean_heading(line), [line]
        else:
            buf.append(line)
    if "\n".join(buf).strip():
        parts.append((cur_title, buf))

    out = []
    for t, buf in parts:
        text = "\n".join(buf).strip()
        deeper = any((_level(l, caps) or 0) > top for l in buf[1:])
        if len(text) > SPLIT_ABOVE and deeper:
            # Children keep their parent as context: "Segmentation — Examples".
            # Short child headings like "Examples" keep their parent as context.
            parent = t.split(" — ")[-1]
            out.extend((c if c == t or len(c) > 24 else f"{parent} — {c}", b)
                       for c, b in _split(buf[1:], caps, t, top + 1))
        else:
            out.append((t, text))
    return out


def _merge_small(sections: list[Section], min_chars: int = 250) -> list[Section]:
    """Headings with almost no body (e.g. 'ELASTICITY' right above 'MONOPOLY') join the next section."""
    out: list[Section] = []
    carry = None
    for s in sections:
        if carry:
            s.text = carry.text + "\n" + s.text
            carry = None
        if len(s.text) < min_chars:
            carry = s
            continue
        out.append(s)
    if carry:
        if out:
            out[-1].text += "\n" + carry.text
        else:
            out.append(carry)
    return out


# ---------------------------------------------------------------- PDF

_LECTURE = re.compile(r"^\s*Lecture\s+\d+\s*$", re.M)


def _pdf_sections(path, source_id, rel, course) -> list[Section]:
    from pypdf import PdfReader
    logging.getLogger("pypdf").setLevel(logging.ERROR)

    reader = PdfReader(str(path))
    full, markers = [], []
    offset = 0
    for i, page in enumerate(reader.pages, start=1):
        txt = page.extract_text() or ""
        txt = re.sub(r"^\s*\d+\s*\n", "", txt)          # page number printed at the top
        txt = "\n".join(l.rstrip() for l in txt.splitlines())
        markers.append((i, offset))
        full.append(txt)
        offset += len(txt) + 1
    text = "\n".join(full)

    starts = [m.start() for m in _LECTURE.finditer(text)] or [0]
    if starts[0] != 0:
        starts.insert(0, 0)
    sections = []
    for a, b in zip(starts, starts[1:] + [len(text)]):
        body = text[a:b].strip()
        if not body:
            continue
        first = body.splitlines()[0].strip()
        title = first if _LECTURE.match(first) else "Overview"
        page = max(p for p, off in markers if off <= a)
        local = [(p, max(0, off - a)) for p, off in markers if a <= off < b]
        sections.append(Section(source_id, rel, course, title, body, page=page,
                                pages=[(page, 0)] + local))
    return _unique_titles(sections)


def _unique_titles(sections: list[Section]) -> list[Section]:
    """Two sections can share a heading (the PDF has two "Lecture 13"): keep section IDs unique."""
    seen = {}
    for s in sections:
        seen[s.title] = seen.get(s.title, 0) + 1
        if seen[s.title] > 1:
            s.title = f"{s.title} (part {seen[s.title]})"
    return sections


def page_at(section: Section, char_offset: int) -> int | None:
    """PDF page containing a character offset within the section text."""
    if not section.pages:
        return None
    page = section.pages[0][0]
    for p, off in section.pages:
        if off <= char_offset:
            page = p
    return page
