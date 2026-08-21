#!/usr/bin/env python3
"""Remove em-dashes that sit directly after a math span.

The rule: `$...$ —` reads as a minus sign glued to the formula in RTL. A dash after a
WORD is fine and is left alone, including on lines that also carry an offending one.
Every replacement is exact-string and asserted, so a stale pattern fails loudly instead
of silently editing the wrong place.
"""
import os
import sys

BOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# (file, old, new, expected occurrences)
EDITS = [
    # ---------------------------------------------------------------- 01-logic
    ("01-logic.qmd",
     "תכונה — פסוק פתוח $P(x)$ — ואנו רוצים",
     "תכונה, פסוק פתוח $,P(x)$ ואנו רוצים", 1),
    ("01-logic.qmd",
     "שאינו מקיים את $P$ — איבר כזה נקרא",
     "שאינו מקיים את $;P$ איבר כזה נקרא", 1),
    ("01-logic.qmd",
     "נובע $\\neg A$ — כלומר הפסוק שרצינו",
     "נובע $,\\neg A$ כלומר הפסוק שרצינו", 1),
    ("01-logic.qmd",
     "הגדול מ-$N$ — סתירה.",
     "הגדול מ-$,N$ וזו סתירה.", 1),

    # ----------------------------------------------------------------- 02-sets
    ("02-sets.qmd", "- $a \\in A$ — נכון,", "- $:a \\in A$ נכון,", 1),
    ("02-sets.qmd", "- $\\{a\\} \\subseteq A$ — נכון,", "- $:\\{a\\} \\subseteq A$ נכון,", 1),
    ("02-sets.qmd", "- $\\{a\\} \\in A$ — **לא נכון**:", "- $,\\{a\\} \\in A$ **לא נכון**:", 1),
    ("02-sets.qmd", "- $a \\subseteq A$ — **חסר משמעות**,", "- $:a \\subseteq A$ **חסר משמעות**,", 1),
    ("02-sets.qmd",
     "- $\\forall n \\in \\mathbb{N},\\ n \\ge 1$ — אמת,",
     "- $:\\forall n \\in \\mathbb{N},\\ n \\ge 1$ אמת,", 1),
    ("02-sets.qmd",
     "- $\\exists n \\in \\mathbb{N},\\ n > 5$ — אמת,",
     "- $:\\exists n \\in \\mathbb{N},\\ n > 5$ אמת,", 1),
    ("02-sets.qmd",
     "- $\\forall x \\in \\mathbb{R},\\ x^{2} \\ge 0$ — אמת,",
     "- $:\\forall x \\in \\mathbb{R},\\ x^{2} \\ge 0$ אמת,", 1),
    ("02-sets.qmd",
     "- $\\exists x \\in \\mathbb{R},\\ x^{2} = 4$ — אמת,",
     "- $:\\exists x \\in \\mathbb{R},\\ x^{2} = 4$ אמת,", 1),
    ("02-sets.qmd",
     "- $\\forall n \\in \\mathbb{N},\\ n > 5$ — **שקר**:",
     "- $,\\forall n \\in \\mathbb{N},\\ n > 5$ **שקר**:", 1),
    ("02-sets.qmd",
     "$U \\setminus A$ — מקרה פרטי של פעולת ההפרש.",
     "$,U \\setminus A$ שהוא מקרה פרטי של פעולת ההפרש.", 1),

    # -------------------------------------------------------- 03-number-systems
    ("03-number-systems.qmd",
     "והממשיים $\\mathbb{R}$ — הבנויות זו על גבי זו:",
     "והממשיים $,\\mathbb{R}$ הבנויות זו על גבי זו:", 1),
    ("03-number-systems.qmd",
     "אז בהכרח $a$ קטן מ-$c$ — זוהי **טרנזיטיביות**.",
     "אז בהכרח $a$ קטן מ-$,c$ וזוהי **טרנזיטיביות**.", 1),
    ("03-number-systems.qmd",
     "על קבוצה $X$ — כלומר, לכל שני איברים",
     "על קבוצה $,X$ כלומר לכל שני איברים", 1),
    ("03-number-systems.qmd",
     "עם $a = a + n$ — בסתירה ל-(i).",
     "עם $,a = a + n$ בסתירה ל-(i).", 1),
    ("03-number-systems.qmd",
     "ולכן $a = a + (n + m)$ — בסתירה ל-(i).",
     "ולכן $,a = a + (n + m)$ בסתירה ל-(i).", 1),
    ("03-number-systems.qmd",
     "וגם $N + 1 > N$ — וזאת סתירה.",
     "וגם $,N + 1 > N$ וזאת סתירה.", 1),
    ("03-number-systems.qmd",
     "$T = S \\cap \\{1, \\dots, x\\}$ — אברי $S$ שאינם גדולים",
     "$,T = S \\cap \\{1, \\dots, x\\}$ כלומר אברי $S$ שאינם גדולים", 1),
    ("03-number-systems.qmd",
     "אחרת — למשל $3 - 5$ — אין לו תשובה",
     "אחרת, למשל $,3 - 5$ אין לו תשובה", 1),
    ("03-number-systems.qmd",
     "כלומר $1, 2, 3, \\dots$ — והם בדיוק המספרים הטבעיים",
     "כלומר $,1, 2, 3, \\dots$ והם בדיוק המספרים הטבעיים", 1),
    ("03-number-systems.qmd",
     "ולכן $\\mathbb{N} = \\{1, 2, 3, \\dots\\}$ — בדיוק השלמים החיוביים.",
     "ולכן $,\\mathbb{N} = \\{1, 2, 3, \\dots\\}$ שהם בדיוק השלמים החיוביים.", 1),
    ("03-number-systems.qmd",
     "כאשר $\\gcd(a, b) = 1$ — כלומר, המחלק המשותף היחיד של $a$ ו-$b$ הוא $1$ — אומרים",
     "כאשר $,\\gcd(a, b) = 1$ כלומר כאשר המחלק המשותף היחיד של $a$ ו-$b$ הוא $,1$ אומרים", 1),
    ("03-number-systems.qmd",
     "אחרת — למשל $3 / 2$ — אין לה תשובה",
     "אחרת, למשל $,3 / 2$ אין לה תשובה", 1),
    ("03-number-systems.qmd",
     "ב-$\\gcd(m, n)$ — וכפי שראינו על השלמים,",
     "ב-$,\\gcd(m, n)$ וכפי שראינו על השלמים,", 1),

    # ------------------------------------------------------ 09-sequences-infinity
    ("09-sequences-infinity.qmd",
     "$(-1)^n$ — לא מתכנסת אפילו במובן הרחב",
     "$(-1)^n$ (לא מתכנסת אפילו במובן הרחב)", 1),

    # ------------------------------------------------------- 12-function-limits
    # captions come in pairs: the centred PDF line and the ![] HTML line
    ("12-function-limits.qmd",
     "לפי $\\varepsilon$-$\\delta$ — רצועה אופקית",
     "לפי $\\varepsilon$-$,\\delta$ רצועה אופקית", 2),
    ("12-function-limits.qmd",
     "$f(x)=\\sin\\left(\\frac{1}{x}\\right)$ — תנודות צפופות",
     "$,f(x)=\\sin\\left(\\frac{1}{x}\\right)$ תנודות צפופות", 2),
    ("12-function-limits.qmd",
     "$f(x)=\\lfloor x \\rfloor$ — קפיצה בנקודה",
     "$,f(x)=\\lfloor x \\rfloor$ קפיצה בנקודה", 2),
    ("12-function-limits.qmd",
     "$f(x)=\\frac{1}{x^2}$ — שואפת לאינסוף בקרבת הראשית",
     "$,f(x)=\\frac{1}{x^2}$ שואפת לאינסוף בקרבת הראשית", 2),
    ("12-function-limits.qmd",
     "$f(x)=\\arctan x$ — אסימפטוטה אופקית",
     "$,f(x)=\\arctan x$ אסימפטוטה אופקית", 4),
    ("12-function-limits.qmd",
     "$f(x)=x^2$ — שואפת לאינסוף, עם סימוני",
     "$,f(x)=x^2$ שואפת לאינסוף, עם סימוני", 2),
    ("12-function-limits.qmd",
     "$f(x)=\\frac{1}{x^2}$ — אסימפטוטה אנכית",
     "$,f(x)=\\frac{1}{x^2}$ אסימפטוטה אנכית", 2),
    ("12-function-limits.qmd",
     "$f(x)=x^2$ — שואפת לאינסוף, עם הסימונים",
     "$,f(x)=x^2$ שואפת לאינסוף, עם הסימונים", 2),

    # ----------------------------------------------------------- 13-continuity
    ("13-continuity.qmd",
     "אי-רציפות ב-$x=2$ — $\\lim_{x\\to 2}f(x)=3$",
     "אי-רציפות ב-$:x=2$ מתקיים $\\lim_{x\\to 2}f(x)=3$", 2),
    ("13-continuity.qmd",
     "על הקטע הפתוח ליד $b$ — אי אפשר ליישם את המשפט.",
     "על הקטע הפתוח ליד $,b$ ולכן אי אפשר ליישם את המשפט.", 1),
    ("13-continuity.qmd",
     "ו-$x_{\\min}$ — אפשר ליישם את המשפט.",
     "ו-$,x_{\\min}$ וכאן אפשר ליישם את המשפט.", 1),
    ("13-continuity.qmd",
     "ו-$x_{\\min}$ — אפשר ליישם](figures/c13_fig12.png)",
     "ו-$,x_{\\min}$ וכאן אפשר ליישם](figures/c13_fig12.png)", 1),

    # ------------------------------------------------------ 16-higher-derivatives
    ("16-higher-derivatives.qmd",
     "$f^{(n)}(x) = (\\ldots(f')'\\ldots)'$ — ח נגזרות",
     "$,f^{(n)}(x) = (\\ldots(f')'\\ldots)'$ ח נגזרות", 1),
    ("16-higher-derivatives.qmd",
     "$f(x)=\\frac{x^2+1}{x}$ — ענף ימני עם מינימום",
     "$,f(x)=\\frac{x^2+1}{x}$ ענף ימני עם מינימום", 2),
    ("16-higher-derivatives.qmd",
     "$f(x)=\\frac{x^2+1}{x}$ — הענף הימני",
     "$,f(x)=\\frac{x^2+1}{x}$ הענף הימני", 2),
    ("16-higher-derivatives.qmd",
     "מקווקוות ב-$x=0$ — הענף הימני",
     "מקווקוות ב-$,x=0$ הענף הימני", 2),

    # ------------------------------------------------------ 18-definite-integral
    ("18-definite-integral.qmd",
     "בקטע $[0,2]$ — ערך $1$ ברציונליים",
     "בקטע $:[0,2]$ ערך $1$ ברציונליים", 2),
    ("18-definite-integral.qmd",
     "$F(x)=\\int_a^x f(t)\\,dt$ — השטח מ-$a$",
     "$,F(x)=\\int_a^x f(t)\\,dt$ השטח מ-$a$", 2),
]


def main():
    texts, problems = {}, []
    for fname, old, new, n in EDITS:
        if fname not in texts:
            texts[fname] = open(os.path.join(BOOK, fname), encoding="utf-8").read()
        got = texts[fname].count(old)
        if got != n:
            problems.append("%s: expected %d, found %d for %r" % (fname, n, got, old[:48]))
        else:
            texts[fname] = texts[fname].replace(old, new)

    if problems:
        print("NOT WRITTEN — patterns did not match:")
        for p in problems:
            print("  " + p)
        sys.exit(1)

    for fname, body in texts.items():
        open(os.path.join(BOOK, fname), "w", encoding="utf-8").write(body)
        print("wrote %s" % fname)


main()
