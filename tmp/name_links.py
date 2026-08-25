import sys
REPL = {
"07-sequences-limit.qmd": [
 ("[שאלה 5.2.2](05-induction.qmd#box-qst-induction-2n-geq-n)",
  "[את השאלה בפרק האינדוקציה](05-induction.qmd#box-qst-induction-2n-geq-n)", 1),
 ("[משפט 7.4.1](#box-thm-limit-window)",
  "[המשפט על טווח ערכי הסדרה](#box-thm-limit-window)", 2),
 ("[שאלה 7.3.6](#box-q-one-over-n)",
  "[שאלה על הסדרה $\\frac{1}{n}$](#box-q-one-over-n)", 1),
],
"08-sequences-properties.qmd": [
 ("[מסקנה 4.5.4](04-abs-value.qmd#box-cor-bounded-abs)",
  "[המסקנה על קבוצה חסומה וערך מוחלט](04-abs-value.qmd#box-cor-bounded-abs)", 1),
 ("[משפט 8.2.3](#box-thm-bounded-abs)",
  "[המשפט על חסימות וערך מוחלט](#box-thm-bounded-abs)", 2),
 ("[דוגמה 8.2.2](#box-exm-bounded-sequences)",
  "[דוגמה על סדרות חסומות ושאינן חסומות](#box-exm-bounded-sequences)", 1),
 ("[משפט 8.2.5](#box-thm-convergent-bounded)",
  "[המשפט על התכנסות וחסימות](#box-thm-convergent-bounded)", 1),
 ("[הערה 8.3.2](#box-rem-denominator-nonzero)",
  "[הערה על המכנה שאינו מתאפס](#box-rem-denominator-nonzero)", 1),
 ("[משפט 8.3.1](#box-thm-sequence-arithmetic)",
  "[משפט אריתמטיקת הגבולות](#box-thm-sequence-arithmetic)", 1),
 ("[שאלה 7.3.6](07-sequences-limit.qmd#box-q-one-over-n)",
  "[שאלה על הסדרה $\\frac{1}{n}$](07-sequences-limit.qmd#box-q-one-over-n)", 1),
 ("[מסקנה 8.2.6](#box-cor-unbounded-diverges)",
  "[המסקנה על סדרות שאינן חסומות](#box-cor-unbounded-diverges)", 1),
 ("[משפט 8.7.2](#box-thm-e-sequence-monotone-bounded)",
  "[משפט על מונוטוניות וחסימות](#box-thm-e-sequence-monotone-bounded)", 1),
]}
apply = "--apply" in sys.argv
for f, rules in REPL.items():
    t = open(f, encoding="utf-8").read()
    for old, new, want in rules:
        got = t.count(old)
        if got != want:
            sys.exit(f"ABORT {f}: expected {want} of {old!r}, found {got}")
        t = t.replace(old, new)
        print(f"  {f}: {got}x  {old.split('](')[0][1:]}  ->  {new.split('](')[0][1:]}")
    if apply:
        open(f, "w", encoding="utf-8").write(t)
print("APPLIED" if apply else "dry run only — rerun with --apply")
