## מסקנות מיידיות מהגדרת הגבול

בסעיף הזה נוציא מהגדרת הגבול כמה מסקנות קצרות. ההוכחות כולן בנות שורות אחדות, אך התוצאות עצמן ילוו אותנו לאורך כל הספר.

### חלון סביב הגבול

ההגדרה אומרת שהחל ממקום מסוים כל איברי הסדרה רחוקים מ-$L$ פחות מ-$,\varepsilon$ כלומר כלואים בקטע $.\left(L-\varepsilon,\ L+\varepsilon\right)$ זהו קטע **סימטרי** סביב $.L$ המשפט הבא אומר שאפשר לוותר על הסימטריה: אפשר לחסום את הסדרה מלמטה בכל מספר הקטן מ-$,L$ ומלמעלה בכל מספר הגדול ממנו.

::: {#box-thm-limit-window .thmthm}
תהי $(a_n)_{n=1}^{\infty}$ סדרה המקיימת $.\lim\limits_{n\to\infty} a_n = L$ אז:

(א) לכל $m < L$ קיים $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים $.a_n > m$

(ב) לכל $M > L$ קיים $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים $.a_n < M$
:::

::::: {.thmproof title="סעיף (א)"}
יהי $.m < L$ המרחק בין $m$ ל-$L$ חיובי, ולכן מותר להפעיל את הגדרת הגבול עם $:\varepsilon = L - m > 0$ קיים $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים $,\left|a_n - L\right| < \varepsilon$ ובפרט

$$.a_n > L - \varepsilon = L - \left(L - m\right) = m$$
:::::

::::: {.thmproof title="סעיף (ב)"}
יהי $.M > L$ הפעם ניקח $,\varepsilon = M - L > 0$ ונקבל $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים $,\left|a_n - L\right| < \varepsilon$ ובפרט

$$.a_n < L + \varepsilon = L + \left(M - L\right) = M$$
:::::

::: {#box-rem-limit-window .thmrem title="חלון כלשהו סביב הגבול"}
שני הסעיפים יחד אומרים דבר אחד: לכל $m$ ו-$M$ המקיימים $,m < L < M$ קיים $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים

$$.m < a_n < M$$

מפעילים כל סעיף בנפרד, מקבלים $N_1$ ו-$,N_2$ ולוקחים $.N = \max\left\{N_1,\ N_2\right\}$

במילים: **הסדרה נכנסת בסופו של דבר לכל קטע שמכיל את $L$ בתוכו**, ולא רק לקטעים הסימטריים $\left(L-\varepsilon,\ L+\varepsilon\right)$ שבהגדרה. הקטע אינו חייב להיות סימטרי, ו-$L$ אינו חייב לשבת באמצעו.
:::

```{python}
#| echo: false
#| output: false
import numpy as np
import matplotlib.pyplot as plt

# Static stand-in for the widget, in the print edition. Same sequence, same window,
# and the same thing to notice: the terms that fall outside sit at the START.
n = np.arange(1, 41)
a = 1 + np.sin(n) / n
m, M = 0.85, 1.15
outside = (a <= m) | (a >= M)
N = int(n[outside].max()) + 1

fig, ax = plt.subplots(figsize=(6.4, 3.2))
ax.axhspan(m, M, color="tab:green", alpha=0.10)
ax.axhline(1.0, color="0.35", lw=1.0, ls="--")
ax.axhline(m, color="tab:blue", lw=1.4)
ax.axhline(M, color="tab:red", lw=1.4)
ax.axvline(N, color="0.2", lw=1.1, ls=":")

ax.plot(n[~outside], a[~outside], "o", ms=4.5, color="tab:green")
ax.plot(n[outside], a[outside], "o", ms=4.5, color="tab:red")

ax.annotate("L", xy=(40.6, 1.0), va="center", fontsize=12, color="0.25")
ax.annotate("m", xy=(40.6, m), va="center", fontsize=12, color="tab:blue")
ax.annotate("M", xy=(40.6, M), va="center", fontsize=12, color="tab:red")
ax.annotate("N = %d" % N, xy=(N, 1.92), ha="center", fontsize=11, color="0.2")

ax.set_xlim(0, 43)
ax.set_ylim(0.62, 1.98)
ax.set_xlabel("n")
ax.spines[["top", "right"]].set_visible(False)
fig.savefig("figures/c07_fig15.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

:::::::: {#box-sim-window .thmsim title="חלון בין $m$ ל-$M$"}
::: {.content-visible when-format="html"}
```{=html}
<iframe class="widget-frame" src="widgets/ch07/window-m-M.html" loading="lazy" title="איברי הסדרה, חלון בין m ל-M סביב הגבול, והאינדקס N שממנו והלאה כל האיברים בתוך החלון"></iframe>
```
:::

הזיזו את $m$ ואת $,M$ וראו כיצד $N$ משתנה. שימו לב לשני דברים: $N$ מגיב לשני המחוונים ולא רק לצר שביניהם, והחלון אינו חייב להיות סימטרי — אפשר להצמיד את $m$ קרוב מאוד ל-$L$ ולהשאיר את $M$ רחוק, ועדיין יימצא $N$ מתאים.

:::: {.content-visible when-format="pdf"}
```{=latex}
\par\medskip
\noindent\beginL\hbox to \linewidth{\hss\includegraphics[width=0.62\linewidth]{figures/c07_fig15.png}\hss}\endL\par
\medskip
```

::: {style="text-align:center"}
תרשים: איברי הסדרה $a_n = 1 + \frac{\sin n}{n}$ והחלון שבין $m$ ל-$.M$ האיברים האדומים חורגים ממנו, וכולם נמצאים בהתחלה; החל מ-$N$ כל האיברים בפנים.
:::
::::
::::::::

::: {#box-qst-window-equivalent .thmqst}
הוכיחו את הכיוון ההפוך. תהי $(a_n)_{n=1}^{\infty}$ סדרה ויהי $,L \in \mathbb{R}$ ונניח שלכל $m$ ו-$M$ המקיימים $m < L < M$ קיים $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים $.m < a_n < M$ הוכיחו כי $.\lim\limits_{n\to\infty} a_n = L$

יחד עם ההערה שלמעלה נובע מכך שהתנאי הזה **שקול** להתכנסות ל-$,L$ ואפשר היה לקחת אותו כהגדרה.
:::

::: {.thmsol .foldable}
יהי $.\varepsilon > 0$ נפעיל את ההנחה על $m = L - \varepsilon$ ועל $,M = L + \varepsilon$ שאכן מקיימים $.m < L < M$ נקבל $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים

$$,L - \varepsilon < a_n < L + \varepsilon$$

כלומר $.\left|a_n - L\right| < \varepsilon$ זוהי בדיוק הגדרת הגבול, ולכן $.\lim\limits_{n\to\infty} a_n = L$
:::

### אי-שוויונות עוברים לגבול

המסקנה הבאה נובעת מיד מן המשפט הקודם: אם כל איברי הסדרה נמצאים מעל מספר מסוים, גם הגבול נמצא מעליו.

::: {#box-thm-limit-preserves-order .thmthm}
תהי $(a_n)_{n=1}^{\infty}$ סדרה מתכנסת, ונסמן $.\lim\limits_{n\to\infty} a_n = L$ אז:

(א) אם $a_n \geq m$ לכל $,n$ אז $.L \geq m$

(ב) אם $a_n \leq M$ לכל $,n$ אז $.L \leq M$
:::

::::: {.thmproof title="סעיף (א)"}
נניח בשלילה ש-$.L < m$ אז $m$ הוא מספר הגדול מן הגבול, ולכן לפי סעיף (ב) של [משפט 7.4.1](#box-thm-limit-window) קיים $N \in \mathbb{N}$ כך שלכל $n \geq N$ מתקיים $.a_n < m$ בפרט $,a_N < m$ בסתירה להנחה ש-$a_n \geq m$ לכל $.n$ לכן $.L \geq m$
:::::

::::: {.thmproof title="סעיף (ב)"}
באותו אופן. אילו היה $,L > M$ היה $M$ מספר הקטן מן הגבול, ולפי סעיף (א) של אותו משפט היה קיים $N$ שממנו והלאה $,a_n > M$ בסתירה להנחה. לכן $.L \leq M$
:::::

::: {#box-warn-strict-becomes-weak .thmwarn title="אי-שוויון חד אינו נשמר בגבול"}
גם אם **כל** איברי הסדרה מקיימים אי-שוויון **חד**, על הגבול מובטח רק אי-שוויון **חלש**.

הדוגמה הפשוטה ביותר היא $:a_n = \dfrac{1}{n}$ לכל $n$ מתקיים $,a_n > 0$ ובכל זאת ראינו ב[שאלה 7.3.6](#box-q-one-over-n) שהגבול הוא $,0$ ולא מספר חיובי כלשהו.

לכן מ-$a_n > m$ לכל $n$ אפשר להסיק רק $,L \geq m$ ולעולם לא $.L > m$
:::

### יחידות הגבול

אם הגדרת ההתכנסות היא הפורמליזציה של הרעיון ״הסדרה מקרבת מספר״, עלינו לוודא שהיא מאפשרת לקרב מספר אחד בלבד. המשפט הבא אומר שאכן כך.

::: {#box-thm-limit-uniqueness .thmthm}
תהי $(a_n)_{n=1}^{\infty}$ סדרה. אם מתקיים $\lim_{n\to\infty}a_n = L_1$ וגם $\lim_{n \to \infty} a_n = L_2$ אז $.L_1 = L_2$

כלומר, אם סדרה מתכנסת אז הגבול שלה הוא יחיד.
:::

```{python}
#| echo: false
#| output: false
import matplotlib.pyplot as plt

L1, L2 = -1.0, 1.0
Mid = (L1 + L2) / 2

fig, ax = plt.subplots(figsize=(6.4, 1.9))
ax.axhline(0, color="0.2", lw=1.3)

for x, col, lab in [(L1, "tab:blue", "$L_1$"), (L2, "tab:red", "$L_2$")]:
    ax.plot([x], [0], "o", ms=8, color=col, zorder=4)
    ax.annotate(lab, xy=(x, -0.30), ha="center", fontsize=13, color=col)

ax.plot([Mid, Mid], [-0.13, 0.13], color="0.15", lw=1.6, zorder=5)
ax.annotate("$M$", xy=(Mid, -0.30), ha="center", fontsize=13, color="0.15")

# the two halves, marked equal: M is the midpoint, and that is all the proof needs
for x0, x1, y in [(L1, Mid, 0.34), (Mid, L2, 0.34)]:
    ax.annotate("", xy=(x0, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="<->", color="0.35", lw=1.1))
ax.annotate("$\\frac{L_2-L_1}{2}$", xy=((L1 + Mid) / 2, 0.44), ha="center", fontsize=11,
            color="0.35")
ax.annotate("$\\frac{L_2-L_1}{2}$", xy=((Mid + L2) / 2, 0.44), ha="center", fontsize=11,
            color="0.35")

ax.annotate("", xy=(L1 - 0.75, 0.13), xytext=(Mid, 0.13),
            arrowprops=dict(arrowstyle="-", color="tab:blue", lw=2.4, alpha=0.55))
ax.annotate("$a_n < M$", xy=((L1 - 0.75 + Mid) / 2, 0.20), ha="center", fontsize=11,
            color="tab:blue")
ax.annotate("", xy=(Mid, -0.13), xytext=(L2 + 0.75, -0.13),
            arrowprops=dict(arrowstyle="-", color="tab:red", lw=2.4, alpha=0.55))
ax.annotate("$a_n > M$", xy=((Mid + L2 + 0.75) / 2, -0.24), ha="center", fontsize=11,
            color="tab:red")

ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-0.55, 0.62)
ax.axis("off")
fig.savefig("figures/c07_fig16.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```

::::: thmproof
נניח בשלילה ש-$.L_1 \neq L_2$

**בלי הגבלת הכלליות נניח ש-$.L_1 < L_2$** הביטוי הזה חוזר בהוכחות רבות וכדאי לעמוד על משמעותו: הטענה סימטרית ב-$L_1$ וב-$,L_2$ ולכן אם השניים שונים אחד מהם קטן מן האחר, ואין שום הפסד בכך שנקרא לקטן שבהם $.L_1$ המקרה השני הוא בדיוק אותה הוכחה עם החלפת התפקידים, ולכן אין צורך לכתוב אותו.

ניקח את נקודת האמצע שבין שני הגבולות:

$$.M = \frac{L_1 + L_2}{2}$$

מתקיים $,L_1 < M < L_2$ ולכן אפשר להפעיל את [משפט 7.4.1](#box-thm-limit-window) פעמיים, פעם על כל גבול:

- הסדרה מתכנסת ל-$L_1$ ומתקיים $,M > L_1$ ולכן לפי סעיף (ב) קיים $N_1$ כך שלכל $n \geq N_1$ מתקיים $;a_n < M$
- הסדרה מתכנסת ל-$L_2$ ומתקיים $,M < L_2$ ולכן לפי סעיף (א) קיים $N_2$ כך שלכל $n \geq N_2$ מתקיים $.a_n > M$

נבחר $.N = \max\left\{N_1,\ N_2\right\}$ שני התנאים מתקיימים עבור $,n = N$ כלומר $a_N < M$ וגם $,a_N > M$ וזו סתירה.

לכן ההנחה $L_1 \neq L_2$ אינה יכולה להתקיים, ומכאן $.L_1 = L_2$

```{=latex}
\par\medskip
\noindent\beginL\hbox to \linewidth{\hss\includegraphics[width=0.62\linewidth]{figures/c07_fig16.png}\hss}\endL\par
\medskip
```

::: {.content-visible when-format="pdf" style="text-align:center"}
תרשים: $M$ היא נקודת האמצע בין $L_1$ ל-$.L_2$ מצד אחד הסדרה חייבת להיכנס בסופו של דבר מתחת ל-$M$ (כי היא מתכנסת ל-$L_1$), ומצד שני מעליו (כי היא מתכנסת ל-$L_2$).
:::

::: {.content-visible when-format="html"}
![$M$ היא נקודת האמצע בין $L_1$ ל-$L_2$. מצד אחד הסדרה חייבת להיכנס בסופו של דבר מתחת ל-$M$ (כי היא מתכנסת ל-$L_1$), ומצד שני מעליו (כי היא מתכנסת ל-$L_2$).](figures/c07_fig16.png){#fig-uniqueness-midpoint width="62%" fig-align="center"}
:::
:::::
