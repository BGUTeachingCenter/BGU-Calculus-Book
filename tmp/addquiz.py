p="09-sequences-infinity.qmd"; s=open(p,encoding="utf-8").read()
PH="לדוגמה: 3/2 או inf"
def wrap(h): return '\n::: {.content-visible when-format="html"}\n```{=html}\n'+h+'\n```\n:::\n'
def seq(label, ans, ph=PH):
    return wrap(f'<div class="seq-quiz" data-answer="{ans}"><span class="seq-label">{label}</span><input class="seq-input" type="text" placeholder="{ph}"><button class="seq-check">בדיקה</button><span class="seq-feedback"></span></div>')
def st(label, ans):
    return wrap(f'<div class="set-quiz" data-answer="{ans}"><span class="set-label">{label}</span><input class="set-input" type="text" placeholder="לדוגמה: 1/2, -1, inf"><button class="set-check">בדיקה</button><span class="set-feedback"></span></div>')
def after(line, block, scope_start=None):
    global s
    start = s.index(scope_start) if scope_start else 0
    i = s.index(line, start); j = i+len(line)
    # the line must end here
    assert s[j]=="\n", (line[:40], repr(s[j:j+5]))
    s = s[:j+1] + block + s[j+1:]
# §9.2 exercises
sc="### תרגילים {#sec-arithmetic-exercises}"
for lab,line,ans in [("(א)",r"(א) $\lim\limits_{n\to\infty} \left(n - \sqrt{n}\right)$","inf"),
                     ("(ב)",r"(ב) $\lim\limits_{n\to\infty} \dfrac{n^{2} + \sin n}{n}$","inf"),
                     ("(ג)",r"(ג) $\lim\limits_{n\to\infty} \left(\sqrt{n+1} - \sqrt{n}\right)$","0"),
                     ("(ד)",r"(ד) $\lim\limits_{n\to\infty} \dfrac{3 + \sin n}{\sqrt{n+1} - \sqrt{n}}$","inf"),
                     ("(ה)",r"(ה) $\lim\limits_{n\to\infty} \left(2n^{2} - n\sqrt{n}\right)$","inf")]:
    after(line, seq(lab,ans), sc)
after(r"**תרגיל 4.** האם קיים הגבול $?\lim\limits_{n\to\infty} \dfrac{n}{2 + \left(-1\right)^{n}}$", seq("הגבול","inf"), sc)
# §9.5 exercises
sc="### תרגילים {#sec-growth-exercises}"
for lab,line,ans in [("(א)",r"(א) $\lim\limits_{n\to\infty} \dfrac{n^{20}}{1.05^{n}}$","0"),
                     ("(ב)",r"(ב) $\lim\limits_{n\to\infty} \dfrac{3^{n} - n^{3}}{3^{n} + n^{3}}$","1"),
                     ("(ג)",r"(ג) $\lim\limits_{n\to\infty} \dfrac{5^{n} + n!}{n! + n^{5}}$","1"),
                     ("(ד)",r"(ד) $\lim\limits_{n\to\infty} \dfrac{n^{2} + 2^{n}}{n^{3} + 3^{n}}$","0")]:
    after(line, seq(lab,ans), sc)
after(r"**תרגיל 3.** חשבו את $\lim\limits_{n\to\infty} \dfrac{2^{n}\, n!}{n^{n}}$ ואת $.\lim\limits_{n\to\infty} \dfrac{3^{n}\, n!}{n^{n}}$ מה מבדיל בין שני המקרים?",
      seq("שני הגבולות, לפי הסדר","0, inf","לדוגמה: 1/2, inf"), sc)
# §9.6 exercises
sc="### תרגילים {#sec-subsequences-exercises}"
after(r"(א) $a_n = \left(-1\right)^{n}\left(1 + \dfrac{1}{n}\right)$",
      st("(א) הגבולות החלקיים","1, -1")+seq("(א) הגבול העליון והתחתון, לפי הסדר","1, -1","לדוגמה: 2, -1"), sc)
after(r"(ב) $a_n = \cos\left(\dfrac{\pi}{3} n\right)$",
      st("(ב) הגבולות החלקיים","1/2, -1/2, -1, 1")+seq("(ב) הגבול העליון והתחתון, לפי הסדר","1, -1","לדוגמה: 2, -1"), sc)
after(r"(ג) $a_n = n^{\left(-1\right)^{n}}$", st("(ג) הגבולות החלקיים","0"), sc)
open(p,"w",encoding="utf-8").write(s); print("ok")
