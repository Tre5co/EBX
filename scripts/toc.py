"""toc — rebuild the `## Contents` block between <!-- TOC --> and <!-- /TOC -->.

    python3 scripts/toc.py [files…]      # default: README.md and docs/*.md

Lists every `##` and `###` heading outside code fences (not `## Contents`
itself), with GitHub-style anchors. INSTRUCTIONS build-seq §999a.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def anchor(text: str, seen: dict) -> str:
    a = text.strip().lower()
    a = re.sub(r"[^\w\- ]", "", a, flags=re.UNICODE).replace(" ", "-").strip("-")
    n = seen.get(a, 0)
    seen[a] = n + 1
    return a if n == 0 else f"{a}-{n}"


def build(md: str) -> str:
    out, seen, fence = [], {}, False
    body = md.split("<!-- /TOC -->", 1)[1] if "<!-- /TOC -->" in md else md
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^(##|###) (.+?)\s*$", line)
        if not m or m.group(2).strip() == "Contents":
            continue
        indent = "" if m.group(1) == "##" else "  "
        out.append(f"{indent}- [{m.group(2).strip()}](#{anchor(m.group(2), seen)})")
    return "\n".join(out)


def main(paths):
    files = [Path(p).resolve() for p in paths] or [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    for f in files:
        s = f.read_text()
        if "<!-- TOC -->" not in s:
            continue
        head, rest = s.split("<!-- TOC -->", 1)
        _, tail = rest.split("<!-- /TOC -->", 1)
        new = head + "<!-- TOC -->\n## Contents\n\n" + build(s) + "\n\n<!-- /TOC -->" + tail
        if new != s:
            f.write_text(new)
            print(f"updated {f.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
