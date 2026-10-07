"""Multi-step web-lead funnel (ad landing page) shared by RingaRoofer and BathVisionary.
Writes /get-matched/ (the page you promote in ads), /get-matched/thanks/ and /partners/ into the site's public folder,
plus /assets/quote.css, /assets/quote.js and /assets/zip3.json. Leads POST to /api/quote (Cloudflare function), which
forwards them to your ping tree. TrustedForm is loaded on the form page; consent wording is tagged for TrustedForm."""
import json, os, re
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
TF = '''<script>
(function () {
  var field = "xxTrustedFormCertUrl", provideReferrer = false, invertFieldSensitivity = false;
  var tf = document.createElement("script"); tf.type = "text/javascript"; tf.async = true;
  tf.src = "https://api.trustedform.com/trustedform.js?provide_referrer=" + escape(provideReferrer) + "&field=" + escape(field) +
    "&l=" + new Date().getTime() + Math.random() + "&invert_field_sensitivity=" + invertFieldSensitivity + "&use_tagged_consent=true";
  var s = document.getElementsByTagName("script")[0]; s.parentNode.insertBefore(tf, s);
})();
</script><noscript><img src="https://api.trustedform.com/ns.gif" alt=""></noscript>'''

CHECK = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>'
LOCK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'
PHONE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'

def consent(c):
    partners = "<a href='/partners/' target='_blank' rel='noopener'>its marketing partners</a>"
    return (f"<p class='qf-consent' data-consent><label class='qf-cb'><input type='checkbox' name='consent' value='yes' required data-tf-element-role='consent-opt-in'>"
            f"<span data-tf-element-role='consent-language'>By checking this box and clicking “<span data-tf-element-role='submit-text'>{c['submit']}</span>”, I agree to the "
            f"<a href='/terms/' target='_blank' rel='noopener'>Terms</a> and <a href='/privacy/' target='_blank' rel='noopener'>Privacy Policy</a> and give my express written consent for "
            f"<span data-tf-element-role='consent-opted-advertiser-name-1'>{c['brand']}</span>, {partners}, and the {c['trade']} companies they work with to contact me about my {c['trade']} project "
            "at the phone number and email I provided, including calls and text messages made with an automatic telephone dialing system or an artificial or prerecorded voice, "
            "even if my number is on a Do Not Call list. Consent is not a condition of any purchase; you can call us instead. Message frequency varies. Msg &amp; data rates may apply. "
            "Reply STOP to opt out, HELP for help.</span></label></p>")

def tiles(opts, name):
    out = []
    for o in opts:
        val, label = o[0], o[1]
        media = f'<span class="qt-img"><img src="{o[2]}" alt="" loading="lazy" width="320" height="220"></span>' if len(o) > 2 and o[2] else f'<span class="qt-ic">{o[3] if len(o) > 3 else "•"}</span>'
        out.append(f'<button type="button" class="qt{" pic" if len(o) > 2 and o[2] else ""}" data-name="{name}" data-val="{esc(val)}">{media}<span class="qt-l">{esc(label)}</span></button>')
    return "".join(out)

def step(i, s):
    body = ""
    if s["kind"] == "zip":
        body = ('<div class="qf-row"><input class="qf-in big" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="ZIP code" aria-label="ZIP code" data-req>'
                '<button type="button" class="qf-btn" data-next>Next</button></div><p class="qf-err" data-err hidden>Enter a 5-digit US ZIP code.</p>')
    elif s["kind"] == "tiles":
        body = f'<div class="qt-grid{" two" if len(s["opts"]) <= 4 else ""}">{tiles(s["opts"], s["name"])}</div>'
    elif s["kind"] == "address":
        body = ('<div class="qf-fields"><label>Street address<input class="qf-in" name="address" autocomplete="street-address" data-req placeholder="123 Main St"></label>'
                '<div class="qf-two"><label>City<input class="qf-in" name="city" autocomplete="address-level2" data-req></label>'
                '<label>State<input class="qf-in" name="state" autocomplete="address-level1" maxlength="2" data-req placeholder="TX"></label></div></div>'
                '<button type="button" class="qf-btn block" data-next>Next</button><p class="qf-err" data-err hidden>Please fill in your street address and city.</p>'
                '<p class="qf-note">So local companies know they serve your area. We never share it publicly.</p>')
    elif s["kind"] == "name":
        body = ('<div class="qf-fields"><div class="qf-two"><label>First name<input class="qf-in" name="first_name" autocomplete="given-name" data-req></label>'
                '<label>Last name<input class="qf-in" name="last_name" autocomplete="family-name" data-req></label></div>'
                '<label>Email<input class="qf-in" name="email" type="email" autocomplete="email" data-req placeholder="you@example.com"></label></div>'
                '<button type="button" class="qf-btn block" data-next>Next</button><p class="qf-err" data-err hidden>Please enter your name and a valid email.</p>')
    elif s["kind"] == "phone":
        body = ''  # filled by caller (needs consent)
    return body

def write(out, c, check):
    """c: dict(brand, url, phone, tel, trade, submit, h1, sub, bullets, hero_img, steps, gallery, faqs, partners, kicker, logo_html, vertical)"""
    steps = c["steps"]; n = len(steps)
    secs = []
    for i, s in enumerate(steps):
        if s["kind"] == "phone":
            body = ('<div class="qf-fields"><label>Mobile phone<input class="qf-in big" name="phone" type="tel" inputmode="tel" autocomplete="tel" data-req placeholder="(555) 555-5555"></label></div>'
                    + consent(c) +
                    f'<button type="submit" class="qf-btn block go" data-tf-element-role="submit">{c["submit"]}</button><p class="qf-err" data-err hidden>Please enter a valid 10-digit US mobile number and check the consent box.</p>'
                    f'<p class="qf-secure">{LOCK} Your details are encrypted and only shared as described above.</p>')
        else:
            body = step(i, s)
        secs.append(f'<fieldset class="qf-step" data-step="{i}" data-kind="{s["kind"]}"{"" if i == 0 else " hidden"}><legend class="qf-q">{esc(s["q"])}</legend>'
                    + (f'<p class="qf-hint">{esc(s["hint"])}</p>' if s.get("hint") else "") + body + '</fieldset>')
    dq = (f'<div class="qf-dq" data-dq hidden><h3>Thanks for checking</h3><p>The {c["trade"]} companies in our network work with homeowners. '
          f'If you manage the property for an owner, ask them to start the request, or call us at <a href="tel:{c["tel"]}">{c["phone"]}</a>.</p><button type="button" class="qf-back" data-restart>Start over</button></div>')
    form = (f'<form class="qf" id="qf" novalidate data-vertical="{c["vertical"]}"><div class="qf-top"><span class="qf-count" data-count>Step 1 of {n}</span><button type="button" class="qf-back" data-back hidden>‹ Back</button></div>'
            f'<div class="qf-bar"><i data-bar style="width:{round(100 / n)}%"></i></div>' + "".join(secs) + dq +
            '<div class="qf-wait" data-wait hidden><span class="qf-spin"></span><h3>Matching you with local pros…</h3><p>Checking companies that serve your ZIP code.</p></div>'
            '<input type="text" name="website" tabindex="-1" autocomplete="off" class="qf-hp" aria-hidden="true"><input type="hidden" name="xxTrustedFormCertUrl"></form>')
    bullets = "".join(f'<li>{CHECK}<span>{b}</span></li>' for b in c["bullets"])
    gallery = "".join(f'<figure><img src="{u}" alt="{esc(a)}" loading="lazy" width="480" height="360"><figcaption>{esc(a)}</figcaption></figure>' for u, a in c["gallery"])
    faqs = "".join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in c["faqs"])
    how = "".join(f'<li><b>{i + 1}</b><h3>{h}</h3><p>{t}</p></li>' for i, (h, t) in enumerate(c["how"]))
    head = lambda title, desc, robots, extra="": f'''<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="{robots}"><link rel="canonical" href="{c["url"]}/get-matched/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><meta name="theme-color" content="{c["dark"]}">
<link rel="stylesheet" href="/assets/quote.css?v={c["v"]}"><style>:root{{--brand:{c["brand_color"]};--brand2:{c["brand_color2"]};--dark:{c["dark"]}}}</style>
<script src="/assets/config.js?v={c["v"]}"></script><script src="/assets/site.js?v={c["v"]}" defer></script>{extra}</head>'''
    top = (f'<header class="lp-top"><div class="lp-wrap lp-top-in"><a class="lp-brand" href="/">{c["logo_html"]}</a>'
           f'<a class="lp-call" href="tel:{c["tel"]}" data-call="get-matched-top">{PHONE}<span>Rather talk? <b>{c["phone"]}</b></span></a></div></header>')
    foot = (f'<footer class="lp-foot"><div class="lp-wrap"><p>{c["disclaimer"]}</p><nav><a href="/privacy/">Privacy Policy</a><a href="/terms/">Terms</a>'
            f'<a href="{c["ca"]}">California Privacy</a><a href="{c["ca"]}#opt-out">Do Not Sell or Share My Personal Information</a><a href="/partners/">Marketing Partners</a>'
            f'<a href="/referral-disclosure/">Referral Disclosure</a></nav><p>&copy; 2026 {c["brand"]}</p></div></footer>')
    page = (head(c["title"], c["desc"], "index, follow", TF) + '<body class="lp">' + top +
            f'<main><section class="lp-hero"><div class="lp-bg"><img src="{c["hero_img"]}" alt="" fetchpriority="high" width="1800" height="1000"></div><div class="lp-wrap lp-hero-in">'
            f'<div class="lp-copy"><p class="lp-kick">{c["kicker"]}</p><h1>{c["h1"]}</h1><p class="lp-sub">{c["sub"]}</p><ul class="lp-ticks">{bullets}</ul></div>'
            f'<div class="lp-card">{form}</div></div></section>'
            f'<section class="lp-sec"><div class="lp-wrap"><h2>How it works</h2><ol class="lp-how">{how}</ol></div></section>'
            f'<section class="lp-sec soft"><div class="lp-wrap"><h2>{c["gallery_h"]}</h2><div class="lp-gal">{gallery}</div></div></section>'
            f'<section class="lp-sec"><div class="lp-wrap lp-faq"><h2>Questions</h2>{faqs}<p class="lp-again"><a href="#qf" class="qf-btn">Start my request</a></p></div></section></main>'
            + foot + f'<script type="application/json" id="qf-cfg">{json.dumps({"brand": c["brand"], "vertical": c["vertical"], "steps": [s["kind"] for s in steps], "owner_field": "homeowner"})}</script>'
            f'<script src="/assets/quote.js?v={c["v"]}" defer></script></body></html>')
    cons = consent(c)
    check(page.replace(cons, " ").replace(c["disclaimer"], " "), "/get-matched/")
    thanks = (head(f"Thanks! | {c['brand']}", "Your request is in.", "noindex, follow") + '<body class="lp">' + top +
              f'<main><section class="lp-sec"><div class="lp-wrap lp-thanks"><span class="lp-ok">{CHECK}</span><h1>You&rsquo;re all set</h1>'
              f'<p class="lp-sub dark">Thanks! Your request is in. Local {c["trade"]} companies that serve your area may call or text you shortly from a number you may not recognize, so keep your phone handy.</p>'
              f'<ul class="lp-next"><li><b>Pick up the call</b> and tell them about your project.</li><li><b>Compare</b> what each company offers before you decide.</li><li><b>Never feel pressured.</b> You are not obligated to hire anyone.</li></ul>'
              f'<p>Rather talk now? <a class="qf-btn" href="tel:{c["tel"]}" data-call="thanks">{PHONE} Call {c["phone"]}</a></p></div></section></main>' + foot + '</body></html>')
    plist = "".join(f"<li>{esc(p)}</li>" for p in c["partners"])
    partners = (head(f"Marketing Partners | {c['brand']}", "Companies that may contact you about your request.", "noindex, follow") + '<body class="lp">' + top +
                f'<main><section class="lp-sec"><div class="lp-wrap lp-doc"><h1>Marketing Partners</h1><p>When you submit a request on {c["url"].split("//")[1]} and agree to be contacted, '
                f'{c["brand"]} may share your request with the following companies and the {c["trade"]} companies they work with, so they can contact you about your project:</p>'
                f'<ul>{plist}</ul><p>You can ask any of them to stop contacting you at any time. To stop contact from us, see our <a href="/privacy/">Privacy Policy</a> or email <a href="mailto:{c["email"]}">{c["email"]}</a>.</p>'
                '</div></section></main>' + foot + '</body></html>')
    for path, html in (("get-matched", page), ("get-matched/thanks", thanks), ("partners", partners)):
        d = os.path.join(out, path); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w").write(html)
    for f in ("quote.css", "quote.js", "zip3.json"):
        open(os.path.join(out, "assets", f), "w").write(open(os.path.join(HERE, "qf_assets", f)).read())
    return ["/get-matched/"]
