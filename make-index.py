#!/usr/bin/env python3
"""Generate BOOK-INDEX.md: a navigable outline of the whole book.

Parses the .qmd SOURCES, not the render, so it works without building and cannot drift
from what is actually written. Deliberately carries no box NUMBERS — numbers come from
the Lua filter and are regenerated on every render, and the book cites boxes by id
anyway (see the cross-reference convention in CALCULUS-PROJECT.md).

    python3 make-index.py

Chapter order follows _quarto.yml when it lists the chapters, else filename order.
"""

import re
import pathlib

HERE = pathlib.Path(__file__).parent

# Mirrors the BOX / UNNUMBERED tables in theorem-numbering.lua. Keep in step with it.
LABEL = {
    "thmdef": "הגדרה", "thmthm": "משפט", "thmprp": "טענה", "thmexm": "דוגמה",
    "thmexr": "תרגיל פתור", "thmqst": "שאלה", "thmsim": "סימולציה", "thmlem": "למה",
    "thmcor": "מסקנה", "thmrem": "הערה", "thmexpl": "הסבר", "thmwarn": "שימו לב",
    "thmkey": "חשוב לזכור", "thmchk": "בדיקה עצמית",
}

# Greedy to the LAST brace: a title= may contain braces of its own, as in
# title="הסדרה $b_n = \\frac{1}{n}$", and a lazy match would stop inside the fraction.
FENCE = re.compile(r'^:{3,}\s*\{(.*)\}\s*$')
HEAD = re.compile(r'^(#{1,4})\s+(.*?)\s*(\{.*\})?\s*$')
EXERCISE = re.compile(r'^\*\*תרגיל\s')


def chapter_order():
    yml = (HERE / "_quarto.yml").read_text(encoding="utf-8")
    listed = re.findall(r'^\s*-\s+(\d\d-[\w-]+\.qmd)\s*$', yml, re.M)
    known = {p.name for p in HERE.glob("[0-9][0-9]-*.qmd")}
    ordered = [f for f in listed if f in known]
    return ordered + sorted(known - set(ordered))


def parse(path):
    """Yield ('head', level, text) and ('box', label, id, title) in document order."""
    for line in path.read_text(encoding="utf-8").split("\n"):
        h = HEAD.match(line)
        if h and not line.startswith("#|"):
            yield ("head", len(h.group(1)), h.group(2))
            continue
        if EXERCISE.match(line):
            yield ("exercise",)
            continue
        f = FENCE.match(line)
        if not f:
            continue
        attrs = f.group(1)
        cls = next((c for c in LABEL if "." + c in attrs), None)
        if cls is None:
            if ".todo" in attrs:
                yield ("box", "TODO", "", "")
            continue
        bid = (re.search(r'#([\w-]+)', attrs) or [None, ""])[1]
        title = (re.search(r'title="([^"]*)"', attrs) or [None, ""])[1]
        if 'numbered="false"' in attrs:
            title = (title + " ") if title else ""
            title += "(ללא מספר)"
        yield ("box", LABEL[cls], bid, title)


def main():
    out = [
        "# Book index",
        "",
        "**Generated — do not edit by hand.** Regenerate with `python3 make-index.py`",
        "from `BGU-Calculus-Book/`. Parses the `.qmd` sources, so it needs no render.",
        "",
        "Box numbers are deliberately absent: they are produced by `theorem-numbering.lua`",
        "at render time and shift whenever a box is inserted. Cite by the `#box-…` id.",
        "",
    ]
    totals = {}
    for name in chapter_order():
        path = HERE / name
        items = list(parse(path))
        title = next((t for k, lvl, t in items if k == "head" and lvl == 1), name)
        out += ["", f"## `{name}` — {title}", ""]
        pending = []           # exercises are counted, not listed one by one

        def flush():
            if pending:
                out.append(f"    - {len(pending)} תרגילים")
                pending.clear()

        for item in items:
            if item[0] == "head":
                flush()
                _, lvl, text = item
                if lvl == 2:
                    out.append(f"- **{text}**")
                elif lvl == 3:
                    out.append(f"  - *{text}*")
                elif lvl == 4:
                    out.append(f"    - {text}")
            elif item[0] == "exercise":
                pending.append(1)
                totals["תרגיל"] = totals.get("תרגיל", 0) + 1
            else:
                flush()
                _, label, bid, title_ = item
                totals[label] = totals.get(label, 0) + 1
                ref = f"`{bid}`" if bid else "—"
                title_ = title_.replace("\\\\", "\\")
                out.append(f"    - {label:<11} {ref}" + (f" · {title_}" if title_ else ""))
        flush()
    out += ["", "## Totals", ""]
    for label in sorted(totals, key=lambda k: -totals[k]):
        out.append(f"- {label}: {totals[label]}")
    (HERE / "BOOK-INDEX.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"BOOK-INDEX.md written: {sum(totals.values())} boxes across "
          f"{len(chapter_order())} chapters")


if __name__ == "__main__":
    main()
