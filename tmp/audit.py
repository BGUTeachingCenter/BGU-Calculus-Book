import re, glob, html

# 1. CITATION AUDIT -----------------------------------------------------------
# Every rendered box id, NUMBERED OR NOT (numbered="false" and the .thmkey/.thmwarn
# classes produce ids with no number in the label — they are still link targets).
ids = set()
for f in glob.glob("_book/*.html"):
    ids |= set(re.findall(r'<div id="(box-[^"]+)"', open(f, encoding="utf-8").read()))
bad = []
for q in sorted(glob.glob("*.qmd")):
    src = open(q, encoding="utf-8").read()
    for m in re.finditer(r'\[([^\]]*?)\]\(([^)]*?)#(box-[^)\s]+)\)', src):
        if m.group(3) not in ids:
            bad.append(f"{q}: DANGLING #{m.group(3)}  (text: {m.group(1).strip()})")
        # link text must NAME the target, never carry the filter's number
        if re.search(r'\d+\.\d+\.\d+', m.group(1)):
            bad.append(f"{q}: NUMBER IN LINK TEXT  {m.group(1).strip()} -> #{m.group(3)}")
print(f"1. citation audit          : {len(bad)}")
for b in bad: print("     " + b)

# 2. em-dash straight after math ----------------------------------------------
hits = [f"{q}:{i}" for q in sorted(glob.glob("*.qmd"))
        for i, l in enumerate(open(q, encoding="utf-8"), 1) if re.search(r'\$ *—', l)]
print(f"2. '$ —' after math        : {len(hits)}")
for h in hits: print("     " + h)

# 3. bullets inside a .thmproof / .thmsol fence -------------------------------
hits = []
for q in sorted(glob.glob("*.qmd")):
    depth, inbox = 0, None
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        o = re.match(r'^(:{3,})\s*(\{.*\}|\w.*)?$', l.rstrip())
        if o and o.group(2):
            depth += 1
            if inbox is None and re.search(r'thmproof|thmsol', o.group(2)): inbox = depth
        elif re.match(r'^:{3,}\s*$', l.rstrip()):
            if inbox is not None and depth == inbox: inbox = None
            depth = max(0, depth - 1)
        elif inbox is not None and re.match(r'^\s*- ', l):
            hits.append(f"{q}:{i}")
print(f"3. bullets in proof/sol    : {len(hits)}")
for h in hits: print("     " + h)

# 4. centred caption div with no enclosing when-format="pdf" ------------------
# Tracks the fence stack; a 6-line proximity test gives false positives, because the
# guard sits above a ```{=latex}``` block and is 7+ lines up.
hits = []
for q in sorted(glob.glob("*.qmd")):
    stack = []
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        m = re.match(r'^(:{3,})(\s*\{.*\}|\s+\w.*)?\s*$', l.rstrip())
        if not m: continue
        attrs = (m.group(2) or "").strip()
        if attrs:
            if attrs == '{style="text-align:center"}' and \
               not any('when-format="pdf"' in a for a in stack):
                hits.append(f"{q}:{i}")
            stack.append(attrs)
        elif stack:
            stack.pop()
print(f"4. unguarded centred div   : {len(hits)}")
for h in hits: print("     " + h)

# 5. every #box- id defined exactly once book-wide --------------------------
# Check 1 only tests link -> id, so a duplicated DEFINITION slips past it. Duplicates are
# invalid HTML in the merged PDF pass and make the [] resolver ambiguous, silently.
seen = {}
for q in sorted(glob.glob("*.qmd")):
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        m = re.match(r'^:{3,}\s*\{#(box-[\w-]+)', l)
        if m:
            seen.setdefault(m.group(1), []).append(f"{q}:{i}")
dups = {k: v for k, v in seen.items() if len(v) > 1}
print(f"5. duplicate box ids       : {len(dups)}")
for k, v in sorted(dups.items()):
    print(f"     {k}  ->  {', '.join(v)}")

# 6. empty-link citation of a box the filter never records ---------------------
# theorem-numbering.lua calls record() only for boxes it NUMBERS. The UNNUMBERED classes
# below, and anything carrying numbered="false", are skipped — so an empty [](#box-...)
# pointing at one renders a literal "??". Such a box must be cited with NAMED link text
# instead (which is the house convention anyway), or opt in with numbered="true".
UNNUMBERED = ("thmexpl", "thmwarn", "thmkey", "thmchk")
unrecorded = set()
for q in sorted(glob.glob("*.qmd")):
    # .optional and .extra set in_optional=true, and process() then skips record() for
    # EVERY box inside them, whatever the class. Track that nesting with a fence stack.
    stack = []
    for l in open(q, encoding="utf-8"):
        f = re.match(r'^(:{3,})(\s*\{.*\}|\s+\w.*)?\s*$', l.rstrip())
        if f:
            attrs = (f.group(2) or "").strip()
            if attrs:
                stack.append(".optional" in attrs or re.search(r'(^|[\s{.])extra\b', attrs) is not None)
            elif stack:
                stack.pop()
        m = re.match(r'^:{3,}\s*\{#(box-[\w-]+)([^}]*)\}', l)
        if not m:
            continue
        bid, attrs = m.group(1), m.group(2)
        opts_in = 'numbered="true"' in attrs
        # stack[:-1] — the box's own fence is already on the stack by now
        if any(stack[:-1]):
            unrecorded.add(bid)
        elif 'numbered="false"' in attrs and not opts_in:
            unrecorded.add(bid)
        elif any(f".{c}" in attrs for c in UNNUMBERED) and not opts_in:
            unrecorded.add(bid)
hits = []
for q in sorted(glob.glob("*.qmd")):
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        for m in re.finditer(r'\[\]\(([^)]*?)#(box-[^)\s]+)\)', l):
            if m.group(2) in unrecorded:
                hits.append(f"{q}:{i}  [](#{m.group(2)}) -> renders ??")
print(f"6. empty ref to unnumbered : {len(hits)}")
for h in hits: print("     " + h)

# ---------------------------------------------------------------------------------
# 7-12 added 2026-09-23 with STYLE-GUIDE.md (next to CALCULUS-PROJECT.md). Checks 7-8
# and 10-12 should report zero; check 9 lists lines to READ, not errors.

STMT = re.compile(r'^:{3,}\s*\{#(box-[\w-]+)[^}]*\.(thmdef|thmthm|thmprp|thmlem|thmcor)\b')
ARROW = re.compile(r'\\(?:long)?(?:to|rightarrow)\b')
# Definitions that INTRODUCE the arrow notation are allowed to show it.
ARROW_OK = {"box-def-convergence", "box-def-convergence-strict"}
# Theorems whose CONCLUSION is inherently "from some point on".
EVENTUAL_OK = {"box-thm-limit-window"}

def statement_lines():
    for q in sorted(glob.glob("*.qmd")):
        box = None
        for i, l in enumerate(open(q, encoding="utf-8"), 1):
            m = STMT.match(l)
            if m:
                box = (m.group(1), m.group(2)); continue
            if box and re.match(r'^:{3,}\s*$', l):
                box = None; continue
            if box:
                yield q, i, box, l

# 7. arrow notation in a statement box -- statements use \lim_{n\to\infty} a_n = L
hits = []
for q, i, (bid, cls), l in statement_lines():
    t = l.replace(r"n\to\infty", "").replace(r"n \to \infty", "")
    if ARROW.search(t) and bid not in ARROW_OK:
        hits.append(f"{q}:{i}  {bid}")
print(f"7. arrow in statement box  : {len(hits)}")
for h in hits: print("     " + h)

# 8. the extended-reals symbol (removed at the lecturer's request)
hits = [f"{q}:{i}" for q in sorted(glob.glob("*.qmd"))
        for i, l in enumerate(open(q, encoding="utf-8"), 1) if "overline{\\mathbb{R}}" in l]
print(f"8. overline R              : {len(hits)}")
for h in hits: print("     " + h)

# 9. "from some point on" inside a theorem-like statement: READ each one. Hypotheses
#    must be the clean "for all n" version; only conclusions may be eventual.
hits = []
for q, i, (bid, cls), l in statement_lines():
    if "ממקום מסוים" in l and bid not in EVENTUAL_OK:   # definitions too (B2)
        hits.append(f"{q}:{i}  {bid}")
print(f"9. eventual in statement   : {len(hits)}  (read: hypothesis or conclusion?)")
for h in hits: print("     " + h)

# 10. a ## heading inside .extra/.optional (Quarto numbers it; the filter does not)
hits = []
for q in sorted(glob.glob("*.qmd")):
    stack = []
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        f = re.match(r'^(:{3,})(\s*\{.*\}|\s+\w.*)?\s*$', l.rstrip())
        if f:
            attrs = (f.group(2) or "").strip()
            if attrs: stack.append(".optional" in attrs or re.search(r'(^|[\s{.])extra\b', attrs) is not None)
            elif stack: stack.pop()
        elif l.startswith("## ") and any(stack):
            hits.append(f"{q}:{i}")
print(f"10. ## inside extra/optional: {len(hits)}")
for h in hits: print("     " + h)

# 11. colour models MathJax 4 does not know (it has RGB, rgb, gray; no HTML)
hits = [f"{q}:{i}" for q in sorted(glob.glob("*.qmd"))
        for i, l in enumerate(open(q, encoding="utf-8"), 1)
        if re.search(r'\\(?:text)?color\[(?:HTML|cmyk)\]', l)]
print(f"11. bad colour model       : {len(hits)}")
for h in hits: print("     " + h)

# 12. a paragraph that is nothing but one inline formula (a stray line break: the
#     formula belongs at the end of its sentence, or in display math)
hits = []
for q in sorted(glob.glob("*.qmd")):
    L = open(q, encoding="utf-8").read().split("\n")
    for i in range(1, len(L) - 1):
        if (re.fullmatch(r'\$[^$]+\$', L[i].strip()) and not L[i-1].strip() and not L[i+1].strip()):
            hits.append(f"{q}:{i+1}  {L[i].strip()[:60]}")
print(f"12. formula-only paragraph : {len(hits)}")
for h in hits: print("     " + h)

# 13. inline colour switch in RTL text -- the 2026-09-24 PDF colour leak. XeTeX reverses
#     each RTL line, colour push/pop specials included, so a {\color{..}..} inside a line
#     can pop before it pushes and the colour never switches off. Safe forms: each coloured
#     piece in its own \parbox{\linewidth}{\color{..}..}, or \textcolor inside math.
#     Scans the preamble, the filter and the chapter sources (raw LaTeX can live in any).
UNSAFE = re.compile(r'(?<!\\parbox\{\\linewidth\})\{\\color\{')
hits = []
for f in ["_quarto.yml", "theorem-numbering.lua"] + sorted(glob.glob("*.qmd")):
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        if l.lstrip().startswith("%"):
            continue
        if UNSAFE.search(l):
            hits.append(f"{f}:{i}  {l.strip()[:90]}")
print(f"13. inline \\color in RTL   : {len(hits)}")
for h in hits: print("     " + h)

# 14. bold part heading inside a single proof box -- each part of a multi-part theorem
#     gets its own .thmproof (STYLE-GUIDE B6). A box titled with several parts
#     ("סעיפים (ב), (ד) ו-(ה)") may legitimately carry bold per-part lines; skip those.
hits = []
for q in sorted(glob.glob("*.qmd")):
    inproof = False; multi = False
    for i, l in enumerate(open(q, encoding="utf-8"), 1):
        m = re.match(r'^:::+\s*(\{[^}]*\.thmproof[^}]*\}|thmproof)\s*$', l.rstrip())
        if m:
            inproof = True; multi = "סעיפים" in l; continue
        if inproof and re.match(r'^:::+\s*$', l):
            inproof = False; continue
        if inproof and not multi and l.startswith("**סעיף ("):
            hits.append(f"{q}:{i}")
print(f"14. part heading in proof  : {len(hits)}")
for h in hits: print("     " + h)
