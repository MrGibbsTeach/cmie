"""Shared markdown -> HTML conversion for pasting listing copy into
marketplace rich-text editors (TPT, Gumroad). Both platforms' description
fields are contenteditable rich-text editors that render literal `##`/`-`
characters if you paste raw markdown -- convert to HTML first so headings
and bullet lists actually render."""

import html as _html


def markdown_to_html(text: str) -> str:
    html_lines: list[str] = []
    in_list = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{_html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{_html.escape(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{_html.escape(line[2:])}</li>")
        elif not line:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<p>{_html.escape(line)}</p>")
    if in_list:
        html_lines.append("</ul>")
    return "".join(html_lines)
