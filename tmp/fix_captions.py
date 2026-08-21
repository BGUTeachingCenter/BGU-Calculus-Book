#!/usr/bin/env python3
"""Guard the PDF-branch figure captions, and give every caption a closing period.

Each figure emits three blocks: a {=latex} \includegraphics (PDF-only by nature), a
centred "תרשים: …" caption, and an ![]() image wrapped in when-format="html". The
centred caption carried NO format guard, so it rendered in HTML too — on top of the
![]() figure's own numbered caption. Every such figure showed its caption twice.

Fix: add .content-visible when-format="pdf" to the caption div, unless it already sits
inside a pdf-only wrapper (the .thmsim blocks already nest theirs correctly).

Also: a caption is a sentence, so it ends with a period. Applied to both branches of
each figure, and only when the caption does not already end in . : ! ? or ־
"""
import glob
import os
import re
import sys

BOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

OPEN = re.compile(r'^(:{3,})\s*\{style="text-align:center"\}\s*$')
FENCE_OPEN = re.compile(r'^:{3,}\s*\{')
FENCE_CLOSE = re.compile(r'^:{3,}\s*$')
# a caption line: the centred "תרשים: …" form, or an ![]() whose alt text we must close
CAPTION_IMG = re.compile(r'^!\[(.+)\]\((figures/[^)]+)\)(.*)$')

ENDINGS = (".", ":", "!", "?", "־", ")")


def close_sentence(text):
    t = text.rstrip()
    if not t or t.endswith(ENDINGS):
        return text
    return t + "."


def main():
    guarded = periods = 0
    for path in sorted(glob.glob(os.path.join(BOOK, "[0-9][0-9]-*.qmd"))):
        lines = open(path, encoding="utf-8").read().split("\n")
        out, stack, changed = [], [], False

        for ln in lines:
            s = ln.strip()

            m = OPEN.match(s)
            if m and "pdf" not in stack:
                # unguarded PDF caption div -> add the guard
                out.append('%s {.content-visible when-format="pdf" style="text-align:center"}'
                           % m.group(1))
                stack.append("other")
                guarded += 1
                changed = True
                continue

            if FENCE_OPEN.match(s):
                stack.append("pdf" if 'when-format="pdf"' in s else "other")
                out.append(ln)
                continue
            if FENCE_CLOSE.match(s):
                if stack:
                    stack.pop()
                out.append(ln)
                continue

            if s.startswith("תרשים:"):
                new = close_sentence(ln)
                if new != ln:
                    periods += 1
                    changed = True
                out.append(new)
                continue

            im = CAPTION_IMG.match(s)
            if im:
                alt = close_sentence(im.group(1))
                if alt != im.group(1):
                    periods += 1
                    changed = True
                    ln = "![%s](%s)%s" % (alt, im.group(2), im.group(3))
                out.append(ln)
                continue

            out.append(ln)

        if changed:
            open(path, "w", encoding="utf-8").write("\n".join(out))
            print("  %s" % os.path.basename(path))

    print("guards added: %d   periods added: %d" % (guarded, periods))


main()
