# Installing on an iPhone

The app walks her through this itself — on an iPhone the guide is the **first screen she sees**,
before she is asked anything else. This file is the same content for reference, plus a short
version you can paste into a text.

---

## Why it is the first screen, not a footnote

Two iOS behaviours make installing-later actively costly:

1. **A home-screen web app on iOS gets its own storage container.** `localStorage` is *not* shared
   with Safari. If she works through the check-up in Safari and installs afterwards, the installed
   app opens completely empty and her answers stay stranded in the browser. So the app asks her to
   install *before* she starts, and provides a copyable code to carry a session across if she
   didn't.
2. **"Add to Home Screen" does not appear in in-app browsers.** Tapping a link in Messages opens
   a WKWebView, not Safari, and the button is simply absent — with no explanation. The app detects
   this and tells her to open Safari first.

Both are verified in `pwa_check.mjs` by emulating an iPhone user agent, including the Messages
in-app browser case.

---

## Paste this into a text to her

> Hey — here's your precalc app: https://javendean.github.io/precalc-1113/
>
> One thing first: when you tap that link it opens a mini browser inside Messages, and that one
> can't add apps to your home screen. Tap the little **compass icon** (bottom right) to open it
> in **Safari**.
>
> Then in Safari: tap the **Share** button at the bottom middle (the square with an arrow going
> up) → scroll down → **Add to Home Screen** → **Add**.
>
> Open **Precalc** from your home screen and start there. Do that *before* answering anything —
> the app keeps its progress separately from Safari, so answers you give in the browser won't
> follow you across.
>
> It's a check-up, not a test. Nothing is graded. Just don't look anything up — a wrong answer is
> genuinely more useful to me than a right one you had to search for. Takes about 20 minutes, and
> it works with no signal.

---

## The steps, in full

**If you opened the link from a text, email or Instagram — do this first**

1. Look for the **compass icon** (usually bottom-right) and tap it. That opens the page in Safari.
2. Or tap **Share** → **Open in Safari**.

**In Safari**

1. Tap the **Share** button — a square with an arrow pointing up out of it, in the bar at the
   **bottom** of the screen, in the middle.
2. A panel slides up. **Scroll down** past the row of apps and past *Add Bookmark*.
3. Tap **Add to Home Screen** (a square with a **+**).
4. Tap **Add**, top-right. The name can stay as **Precalc**.
5. Leave Safari and open **Precalc** from the Home Screen. It opens full screen with no address
   bar — that is how you know it worked.

**If "Add to Home Screen" isn't there**

- Scroll further; it sits well down the list.
- Still missing: scroll to the very bottom of the panel → **Edit Actions…** → find
  **Add to Home Screen** → tap the green **+** → go back.
- If it is still absent you are not in Safari. See the first section.

---

## If she already started in the browser

The app handles it. On the install screen there is a **Moving answers across** panel:

1. In Safari, tap **Copy my progress code**.
2. Open the installed app → the same panel → paste into the box → **Bring my answers over**.

The carried session also marks those questions as already asked, so the diagnostic resumes rather
than re-serving them. `test_engine.mjs` covers this round trip; if it broke she would silently
lose a whole session.
