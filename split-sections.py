#!/usr/bin/env python3
"""Split rendered chapter pages into one page per section.

Runs on the OUTPUT in _book/, never on the .qmd sources. That is the whole point:
Quarto renders the book normally, so every number it produces — 7.3, תרשים 7.9,
הגדרה 7.3.1 — is already correct, and this script only re-paginates. It computes
no numbers of its own. Delete the script and re-render to undo it completely.

Why not do it in Quarto: a book page IS a chapter there. Chapter numbers come from
the position in `chapters:` and `number-offset` is ignored, so making a section into
a page necessarily makes it a chapter and shifts every chapter after it.

For each chapter listed in SPLIT:
  * <section class="level2"> blocks each become their own page; the first keeps the
    original filename so inbound links and bookmarks still land somewhere sensible
  * the sidebar (in every page of the book) gains a nested, collapsible level
  * links are retargeted to whichever page now holds their anchor, both inside the
    chapter and from the other 19 chapters
  * prev/next is rewired through the new pages
  * search.json entries are repointed
"""

import json
import os
import re
import sys

BOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_book")

# Every rendered chapter page — the NN-slug.html files. index.html and the part
# landing pages are not chapters and are left alone; so is anything with fewer
# than two sections, which has nothing to split.
CHAPTER_RE = re.compile(r"^\d\d-.*\.html$")
EXCLUDE = {"index.html"}


def chapters_to_split(book):
    return sorted(n for n in os.listdir(book)
                  if CHAPTER_RE.match(n) and n not in EXCLUDE)


# ---------------------------------------------------------------- html helpers

def element_span(html, start, tag="section"):
    """(start, end) of the element opening at `start`, honouring nesting."""
    pat = re.compile(r"</?%s\b" % tag, re.I)
    depth, i = 0, start
    while True:
        m = pat.search(html, i)
        if not m:
            raise ValueError("unbalanced <%s> from offset %d" % (tag, start))
        if html[m.start():m.start() + 2] == "</":
            depth -= 1
            if depth == 0:
                return start, html.index(">", m.start()) + 1
        else:
            depth += 1
        i = m.end()


def main_span(html):
    m = re.search(r"<main\b[^>]*>", html)
    return m.end(), html.rindex("</main>")


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def ids_in(fragment):
    return set(re.findall(r'\sid="([^"]+)"', fragment))


# ------------------------------------------------------------------- splitting

def section_pages(path):
    """Cut one chapter page into [(filename, title, section_html, ids), ...]."""
    html = open(path, encoding="utf-8").read()
    lo, hi = main_span(html)
    body = html[lo:hi]

    header, head_end = "", 0
    m = re.search(r"<header id=\"title-block-header\".*?</header>", body, re.S)
    if m:
        header, head_end = m.group(0), m.end()

    spans = []
    for m in re.finditer(r'<section id="[^"]+" class="level2[^"]*"', body):
        if spans and m.start() < spans[-1][1]:
            continue                      # nested, not a top-level section
        spans.append(element_span(body, m.start()))
    if len(spans) < 2:
        return []

    # Cut the body at section ends so EVERY byte after the header lands on exactly
    # one page: the first page keeps any intro text that sits between the <h1> and
    # the first <h2>, the last page absorbs anything trailing the final section.
    bounds = [head_end] + [b for _, b in spans]
    bounds[-1] = len(body)
    frags = [body[bounds[i]:bounds[i + 1]] for i in range(len(spans))]
    assert sum(len(f) for f in frags) == len(body) - head_end, \
        "content dropped while splitting %s" % path

    base = os.path.basename(path)
    stem = base[:-5]
    out = []
    for n, frag in enumerate(frags, start=1):
        title = strip_tags(re.search(r"<h2[^>]*>(.*?)</h2>", frag, re.S).group(1))
        name = base if n == 1 else "%s-%d.html" % (stem, n)
        out.append({"file": name, "title": title, "html": header + "\n" + frag,
                    "ids": ids_in(frag), "template": html})
    return out


def rebuild_toc(page_html, frag):
    """Right-hand TOC: keep only the headings that live on this page."""
    m = re.search(r'(<nav id="TOC"[^>]*>)(.*?)(</nav>)', page_html, re.S)
    if not m:
        return page_html
    items = []
    for h in re.finditer(r'<h([234])[^>]*id="([^"]+)"[^>]*>(.*?)</h\1>', frag, re.S):
        lvl, hid, txt = int(h.group(1)), h.group(2), strip_tags(h.group(3))
        if txt:
            items.append((lvl, hid, txt))
    if not items:
        return page_html
    top = min(l for l, _, _ in items)
    lis = []
    for lvl, hid, txt in items:
        if lvl > top + 1:                 # keep the TOC to two levels, as before
            continue
        cls = "" if lvl == top else ' class="toc-indent"'
        lis.append('<li%s><a href="#%s" class="nav-link">%s</a></li>' % (cls, hid, txt))
    toc = '<ul class="nav nav-pills flex-column">%s</ul>' % "".join(lis)
    keep = re.search(r'(<h2 id="toc-title">.*?</h2>)', m.group(2), re.S)
    return page_html[:m.start()] + m.group(1) + (keep.group(1) if keep else "") + \
        toc + m.group(3) + page_html[m.end():]


# ------------------------------------------------------------------- navigation

TOGGLE = (
    '<a class="sidebar-item-toggle text-start{collapsed}" data-bs-toggle="collapse" '
    'data-bs-target="#{sid}" role="navigation" aria-expanded="{expanded}" '
    'aria-label="הצג/הסתר מקטע"><i class="bi bi-chevron-right ms-2"></i></a>'
)


def sidebar_with_sections(html, chapter_file, pages, current):
    """Nest the section pages under their chapter's sidebar entry.

    Only the chapter being read starts expanded. Expanding all of them buries the
    chapter list under a few hundred section links, and the sidebar stops being a
    map of the book. Bootstrap drives the state from `show` on the <ul> and
    aria-expanded on the toggle; the chevron rotation is aria-expanded alone.
    """
    m = re.search(
        r'<li class="sidebar-item">\s*<div class="sidebar-item-container">\s*'
        r'<a href="\./%s"[^>]*>(.*?)</a>\s*</div>\s*</li>' % re.escape(chapter_file),
        html, re.S)
    if not m:
        return html
    link, label = m.group(0), m.group(1)
    sid = "quarto-sidebar-sub-" + chapter_file[:-5]
    here = any(p["file"] == current for p in pages)
    toggle = TOGGLE.format(sid=sid,
                           collapsed="" if here else " collapsed",
                           expanded="true" if here else "false")

    chapter_link = re.sub(r'\sclass="sidebar-item-text sidebar-link[^"]*"',
                          ' class="sidebar-item-text sidebar-link"', label)
    kids = []
    for p in pages:
        active = " active" if p["file"] == current else ""
        kids.append(
            '<li class="sidebar-item"><div class="sidebar-item-container">'
            '<a href="./%s" class="sidebar-item-text sidebar-link%s">'
            '<span class="menu-text">%s</span></a></div></li>'
            % (p["file"], active, p["title"]))
    block = (
        '<li class="sidebar-item sidebar-item-section">'
        '<div class="sidebar-item-container">'
        '<a href="./%s" class="sidebar-item-text sidebar-link">%s</a>%s</div>'
        '<ul id="%s" class="collapse list-unstyled sidebar-section depth2%s">%s</ul>'
        '</li>'
    ) % (pages[0]["file"], chapter_link, toggle, sid,
         " show" if here else "", "".join(kids))
    return html.replace(link, block)


def nav_link(href, label, direction):
    icon = "bi-arrow-left-short" if direction == "previous" else "bi-arrow-right-short"
    inner = ('<i class="bi %s"></i> <span class="nav-page-text">%s</span>' % (icon, label)
             if direction == "previous" else
             '<span class="nav-page-text">%s</span> <i class="bi %s"></i>' % (label, icon))
    return ('<div class="nav-page nav-page-%s"><a href="./%s" class="pagination-link" '
            'aria-label="%s">%s</a></div>' % (direction, href, strip_tags(label), inner))


def set_page_navigation(html, prev, nxt):
    m = re.search(r'<nav class="page-navigation">.*?</nav>', html, re.S)
    if not m:
        return html
    parts = []
    if prev:
        parts.append(nav_link(prev[0], prev[1], "previous"))
    if nxt:
        parts.append(nav_link(nxt[0], nxt[1], "next"))
    return html[:m.start()] + '<nav class="page-navigation">%s</nav>' % "".join(parts) + \
        html[m.end():]


def neighbours(html):
    """(href, label) of the chapter's original prev/next, before we rewire."""
    out = {}
    for d in ("previous", "next"):
        m = re.search(r'<div class="nav-page nav-page-%s">\s*<a href="\./([^"]+)"[^>]*>'
                      r'.*?<span class="nav-page-text">(.*?)</span>' % d, html, re.S)
        out[d] = (m.group(1), m.group(2)) if m else None
    return out


# ------------------------------------------------------------------------- main

def main():
    if not os.path.isdir(BOOK):
        sys.exit("no _book/ — render first")

    all_pages, id_home, retarget = {}, {}, {}

    for chapter in chapters_to_split(BOOK):
        path = os.path.join(BOOK, chapter)
        pages = section_pages(path)
        if len(pages) < 2:
            print("  %-34s single section, left whole" % chapter)
            continue
        all_pages[chapter] = pages
        # per chapter, not global: the same id may legitimately exist in two
        # chapters, and a same-page link must never be sent to the other one
        id_home[chapter] = {i: p["file"] for p in pages for i in p["ids"]}
        # anything still pointing at the chapter as a whole goes to its first page
        retarget[chapter] = pages[0]["file"]
        print("  %-34s %d pages" % (chapter, len(pages)))

    if not all_pages:
        return

    # ---- emit the section pages
    for chapter, pages in all_pages.items():
        template = pages[0]["template"]
        lo, hi = main_span(template)
        ends = neighbours(template)
        for n, p in enumerate(pages):
            doc = template[:lo] + p["html"] + template[hi:]
            doc = rebuild_toc(doc, p["html"])
            prev = ends["previous"] if n == 0 else \
                (pages[n - 1]["file"], pages[n - 1]["title"])
            nxt = ends["next"] if n == len(pages) - 1 else \
                (pages[n + 1]["file"], pages[n + 1]["title"])
            doc = set_page_navigation(doc, prev, nxt)
            open(os.path.join(BOOK, p["file"]), "w", encoding="utf-8").write(doc)

    # ---- fix links + sidebar across every page in the book
    for name in sorted(os.listdir(BOOK)):
        if not name.endswith(".html"):
            continue
        path = os.path.join(BOOK, name)
        doc = open(path, encoding="utf-8").read()
        owner = next((c for c, ps in all_pages.items()
                      if name in [p["file"] for p in ps]), None)

        for chapter, pages in all_pages.items():
            home = id_home[chapter]
            # Cross-chapter anchors. Quarto writes these WITHOUT a "./" prefix in
            # body text but WITH one in the sidebar, so the prefix is optional and
            # preserved as found: 01-logic.html#sec-x -> 01-logic-4.html#sec-x
            def fix(m, _h=home, _c=chapter):
                anchor = m.group(2)
                return "%s%s#%s" % (m.group(1) or "", _h.get(anchor, retarget[_c]), anchor)
            doc = re.compile(r'(\./)?' + re.escape(chapter) + r'#([^"\'\s#]+)').sub(fix, doc)
            # a bare link to the chapter lands on its first page (same filename) — nothing to do
            if owner == chapter:
                # within the split chapter, same-page "#foo" may now live elsewhere
                def local(m, _h=home):
                    anchor = m.group(1)
                    target = _h.get(anchor)
                    return 'href="#%s"' % anchor if (target is None or target == name) \
                        else 'href="./%s#%s"' % (target, anchor)
                doc = re.sub(r'href="#([^"]+)"', local, doc)
            doc = sidebar_with_sections(doc, chapter, pages, name)

        open(path, "w", encoding="utf-8").write(doc)

    # ---- search index
    sj = os.path.join(BOOK, "search.json")
    if os.path.exists(sj):
        data = json.load(open(sj, encoding="utf-8"))
        for entry in data:
            href = entry.get("href", "")
            base, _, anchor = href.partition("#")
            if base in all_pages and anchor:
                entry["href"] = "%s#%s" % (
                    id_home[base].get(anchor, retarget[base]), anchor)
        json.dump(data, open(sj, "w", encoding="utf-8"), ensure_ascii=False)
        print("  search.json repointed (%d entries)" % len(data))


if __name__ == "__main__":
    print("splitting sections in _book/ ...")
    main()
    print("done")
