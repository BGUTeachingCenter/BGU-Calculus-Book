import re, glob, html, os, sys

# 1. CITATION AUDIT -----------------------------------------------------------
# Build id -> number from the RENDERED html (the filter's own output), then check
# every [.. N.N.N ..](..#box-..) in the .qmd sources against it.
num = {}
for f in glob.glob("_book/*.html"):
    t = open(f, encoding="utf-8").read()
    for m in re.finditer(r'<div id="(box-[^"]+)"[^>]*>\s*<p><strong>(.*?)</strong>', t, re.S):
        lab = html.unescape(re.sub('<[^>]+>', '', m.group(2)))
        g = re.search(r'(\d+\.\d+\.\d+)', lab)
        if g:
            num[m.group(1)] = g.group(1)

bad = []
for q in sorted(glob.glob("*.qmd")):
    for m in re.finditer(r'\[([^\]]*?)\]\(([^)]*?)#(box-[^)\s]+)\)', open(q, encoding="utf-8").read()):
        text, bid = m.group(1), m.group(3)
        g = re.search(r'(\d+\.\d+\.\d+)', text)
        if bid not in num:
            bad.append(f"{q}: DANGLING #{bid}  (link text: {text.strip()})")
        elif g and g.group(1) != num[bid]:
            bad.append(f"{q}: STALE  #{bid}  text says {g.group(1)}, rendered is {num[bid]}")
print(f"1. citation audit          : {len(bad)}")
for b in bad: print("     " + b)

# 2. em-dash straight after math ----------------------------------------------
hits = [(q, i) for q in sorted(glob.glob("*.qmd"))
        for i, l in enumerate(open(q, encoding="utf-8"), 1) if re.search(r'\$ *—', l)]
print(f"2. '$ —' after math        : {len(hits)}")
for q, i in hits: print(f"     {q}:{i}")

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

# 4. unguarded centred caption div --------------------------------------------
hits = []
for q in sorted(glob.glob("*.qmd")):
    lines = open(q, encoding="utf-8").read().split("\n")
    open_pdf = 0
    for i, l in enumerate(lines, 1):
        if 'when-format="pdf"' in l: open_pdf = i
        if re.match(r'^:{3,}\s*\{style="text-align:center"\}\s*$', l.strip()):
            # legal only inside a when-format="pdf" wrapper opened just above
            if not (0 < i - open_pdf <= 6): hits.append(f"{q}:{i}")
print(f"4. unguarded centred div   : {len(hits)}")
for h in hits: print("     " + h)
