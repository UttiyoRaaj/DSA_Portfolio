"""Content loaders and a small, dependency-free Markdown renderer for learning paths."""

from html import escape
from pathlib import Path
import re

from markupsafe import Markup


CONTENT_DIR = Path(__file__).resolve().parent / "learning_content"


def _inline(text: str) -> str:
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def render_markdown(markdown: str) -> Markup:
    """Render the Markdown features used by the supplied learning content."""
    output, paragraph, list_type, table_lines = [], [], None, []
    in_code, code_lines = False, []

    def close_paragraph():
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list():
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    def close_table():
        nonlocal table_lines
        if not table_lines:
            return
        rows = [
            [cell.strip() for cell in row.strip().strip("|").split("|")]
            for row in table_lines
        ]
        header, data_rows = rows[0], rows[2:]
        output.append("<div class=\"markdown-table\"><table><thead><tr>" + "".join(
            f"<th>{_inline(cell)}</th>" for cell in header
        ) + "</tr></thead><tbody>" + "".join(
            "<tr>" + "".join(f"<td>{_inline(cell)}</td>" for cell in row) + "</tr>"
            for row in data_rows
        ) + "</tbody></table></div>")
        table_lines = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            close_paragraph()
            close_list()
            if in_code:
                output.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
            in_code = not in_code
            continue
        if in_code:
            code_lines.append(raw_line)
            continue
        if line.startswith("|"):
            close_paragraph()
            close_list()
            table_lines.append(line)
            continue
        close_table()
        if not line:
            close_paragraph()
            close_list()
            continue
        if line == "---":
            close_paragraph()
            close_list()
            output.append("<hr>")
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            close_paragraph()
            close_list()
            level = len(heading.group(1)) + 1
            output.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue
        if line.startswith("> "):
            close_paragraph()
            close_list()
            output.append(f"<blockquote><p>{_inline(line[2:])}</p></blockquote>")
            continue
        unordered = re.match(r"^[-*]\s+(.+)$", line)
        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if unordered or ordered:
            close_paragraph()
            wanted = "ul" if unordered else "ol"
            if list_type and list_type != wanted:
                close_list()
            if not list_type:
                output.append(f"<{wanted}>")
                list_type = wanted
            output.append(f"<li>{_inline((unordered or ordered).group(1))}</li>")
            continue
        close_list()
        paragraph.append(line)

    close_paragraph()
    close_list()
    close_table()
    if in_code:
        output.append(f"<pre><code>{escape(chr(10).join(code_lines))}</code></pre>")
    return Markup("\n".join(output))


def _parse_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        title = next((line[2:] for line in raw.splitlines() if line.startswith("# ")), path.stem.replace("-", " ").title())
        return {"title": title, "category": "RAG / Information Retrieval / Azure AI Search", "difficulty": "Advanced", "description": "Hybrid retrieval, semantic ranking, and practical tuning.", "slug": path.stem, "content": render_markdown(raw)}
    frontmatter, body = raw.split("---\n", 2)[1:]
    metadata = {}
    for line in frontmatter.splitlines():
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    metadata["slug"] = path.stem
    metadata["content"] = render_markdown(body.strip())
    return metadata


def get_learning_questions(path_slug: str) -> list[dict]:
    directory = CONTENT_DIR / path_slug
    if not directory.exists():
        return []
    return [_parse_file(path) for path in sorted(directory.glob("*.md"))]


def get_learning_question(path_slug: str, question_slug: str) -> dict | None:
    path = CONTENT_DIR / path_slug / f"{question_slug}.md"
    return _parse_file(path) if path.exists() else None
