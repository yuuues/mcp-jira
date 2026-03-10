"""Markdown to Atlassian Document Format (ADF) converter."""
from __future__ import annotations

import re
from typing import Any


def markdown_to_adf(text: str) -> dict[str, Any]:
    """Convert a Markdown string to an Atlassian Document Format (ADF) document.

    Supported Markdown elements:
        - Fenced code blocks (```lang ... ```)
        - ATX headings (# through ######)
        - Bullet lists (- or * prefixed lines, with optional nesting via indentation)
        - Ordered lists (1. prefixed lines, with optional nesting via indentation)
        - Horizontal rules (--- or ***)
        - Blank lines as paragraph separators
        - Inline marks within paragraph / list-item text:
            bold (**text** or __text__), italic (*text* or _text_),
            inline code (`code`), links ([label](url))
    """
    lines = text.splitlines()
    content: list[dict[str, Any]] = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # --- Fenced code block ---
        fence_match = re.match(r'^(`{3,}|~{3,})(.*)', line)
        if fence_match:
            fence_char = fence_match.group(1)
            lang = fence_match.group(2).strip()
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].startswith(fence_char[:3]):
                code_lines.append(lines[i])
                i += 1
            i += 1  # consume closing fence
            node: dict[str, Any] = {"type": "codeBlock", "content": [{"type": "text", "text": "\n".join(code_lines)}]}
            if lang:
                node["attrs"] = {"language": lang}
            content.append(node)
            continue

        # --- ATX Heading ---
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            content.append({
                "type": "heading",
                "attrs": {"level": level},
                "content": _parse_inline(heading_text),
            })
            i += 1
            continue

        # --- Horizontal rule ---
        if re.match(r'^(\-{3,}|\*{3,}|_{3,})\s*$', line):
            content.append({"type": "rule"})
            i += 1
            continue

        # --- List block (bullet or ordered) ---
        list_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)', line)
        if list_match:
            i, list_node = _parse_list(lines, i)
            content.append(list_node)
            continue

        # --- Blank line ---
        if line.strip() == "":
            i += 1
            continue

        # --- Paragraph ---
        # Accumulate consecutive non-special lines into one paragraph
        para_lines: list[str] = []
        while i < len(lines):
            l = lines[i]
            if l.strip() == "":
                break
            if re.match(r'^(`{3,}|~{3,})', l):
                break
            if re.match(r'^#{1,6}\s', l):
                break
            if re.match(r'^(\-{3,}|\*{3,}|_{3,})\s*$', l):
                break
            if re.match(r'^(\s*)([-*]|\d+\.)\s+', l):
                break
            para_lines.append(l)
            i += 1

        if para_lines:
            content.append({
                "type": "paragraph",
                "content": _parse_inline(" ".join(para_lines)),
            })

    # Ensure the document always has at least one node (Jira requires it)
    if not content:
        content.append({"type": "paragraph", "content": []})

    return {"type": "doc", "version": 1, "content": content}


# ---------------------------------------------------------------------------
# List parsing
# ---------------------------------------------------------------------------

def _parse_list(lines: list[str], start: int) -> tuple[int, dict[str, Any]]:
    """Parse a list block starting at `start`, returning (next_index, adf_node)."""
    first_match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)', lines[start])
    assert first_match, "Expected list marker"
    base_indent = len(first_match.group(1))
    is_ordered = bool(re.match(r'\d+\.', first_match.group(2)))
    list_type = "orderedList" if is_ordered else "bulletList"

    items: list[dict[str, Any]] = []
    i = start

    while i < len(lines):
        line = lines[i]
        match = re.match(r'^(\s*)([-*]|\d+\.)\s+(.*)', line)
        if not match:
            break
        indent = len(match.group(1))
        if indent < base_indent:
            break
        if indent > base_indent:
            # Sub-list — attach to the last item
            i, sub_node = _parse_list(lines, i)
            if items:
                items[-1]["content"].append(sub_node)
            continue

        item_text = match.group(3)
        item_content: list[dict[str, Any]] = [{"type": "paragraph", "content": _parse_inline(item_text)}]
        items.append({"type": "listItem", "content": item_content})
        i += 1

    return i, {"type": list_type, "content": items}


# ---------------------------------------------------------------------------
# Inline mark parsing
# ---------------------------------------------------------------------------

# Each entry: (pattern, handler) where handler receives the match and returns ADF nodes.
# Order matters — code first to prevent nested processing, then links, bold, italic.

_INLINE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r'`([^`]+)`'), "code"),
    (re.compile(r'\[([^\]]+)\]\(([^)]+)\)'), "link"),
    (re.compile(r'\*\*(.+?)\*\*|__(.+?)__'), "strong"),
    (re.compile(r'\*(.+?)\*|_(.+?)_'), "em"),
]


def _parse_inline(text: str) -> list[dict[str, Any]]:
    """Convert an inline Markdown string to a list of ADF inline nodes."""
    return _tokenise(text)


def _tokenise(text: str) -> list[dict[str, Any]]:
    """Recursively tokenise inline Markdown into ADF text/mark nodes."""
    if not text:
        return []

    # Find the earliest match across all patterns
    earliest_match: re.Match[str] | None = None
    earliest_pattern_key: str | None = None
    earliest_start = len(text)

    for pattern, key in _INLINE_PATTERNS:
        m = pattern.search(text)
        if m and m.start() < earliest_start:
            earliest_match = m
            earliest_pattern_key = key
            earliest_start = m.start()

    if earliest_match is None:
        # No more marks — plain text node
        return [{"type": "text", "text": text}]

    nodes: list[dict[str, Any]] = []

    # Text before the match
    if earliest_start > 0:
        nodes.append({"type": "text", "text": text[:earliest_start]})

    key = earliest_pattern_key
    m = earliest_match

    if key == "code":
        nodes.append({"type": "text", "text": m.group(1), "marks": [{"type": "code"}]})

    elif key == "link":
        label = m.group(1)
        url = m.group(2)
        inner = _tokenise(label)
        link_mark = {"type": "link", "attrs": {"href": url}}
        for node in inner:
            node.setdefault("marks", []).append(link_mark)
        nodes.extend(inner)

    elif key == "strong":
        inner_text = m.group(1) if m.group(1) is not None else m.group(2)
        inner = _tokenise(inner_text)
        strong_mark = {"type": "strong"}
        for node in inner:
            node.setdefault("marks", []).insert(0, strong_mark)
        nodes.extend(inner)

    elif key == "em":
        inner_text = m.group(1) if m.group(1) is not None else m.group(2)
        inner = _tokenise(inner_text)
        em_mark = {"type": "em"}
        for node in inner:
            node.setdefault("marks", []).insert(0, em_mark)
        nodes.extend(inner)

    # Text after the match
    after = text[m.end():]
    if after:
        nodes.extend(_tokenise(after))

    return nodes
