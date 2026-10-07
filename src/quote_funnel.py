"""3-step smart quote form (ad landing page) shared by RingaRoofer and BathVisionary — eLocal/Networx style.
Writes /get-a-quote/ (promote this in ads), /get-a-quote/thanks/ and /partners/ into the site's public folder, plus
/assets/quote.css, /assets/quote.js, /assets/zip3.json, and a redirect from the earlier /get-matched/ draft.
Step 1: photo tiles (one tap)  ·  Step 2: ZIP + homeowner + chips (one card)  ·  Step 3: name, phone, email (+ optional address),
answer summary with "change", consent text right above the button (button-click consent, tagged for TrustedForm).
Leads POST to /api/quote (Cloudflare function) which forwards them to the ping tree."""
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
LOCK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>'
PHONE = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'
PIN = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/></svg>'

OLD_STEP3 = '''<fieldset class="qf-step" data-step="2" hidden><legend class="qf-q">{q}</legend>
 <div class="qf-sum" data-sum></div>
 <div class="qf-fields"><label>Full name<input class="qf-in" name="full_name" autocomplete="name" placeholder="First and last name"></label>
 <label>Mobile phone<input class="qf-in" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="(555) 555-5555"></label>
 <label>Email<input class="qf-in" name="email" type="email" autocomplete="email" placeholder="you@example.com"></label>
 <label>Street address <span class="opt">(optional, helps local pros)</span><input class="qf-in" name="address" autocomplete="street-address" placeholder="123 Main St"></label></div>
 {consent}
 <button type="submit" class="qf-btn block go" data-tf-element-role="submit">{submit}</button>
 <p class="qf-err" data-err hidden>Please add your full name, a valid mobile number and email.</p>
 <p class="qf-secure">{LOCK} Secure · Your details go only to the companies named above.</p></fieldset>
'''

def consent(c):
    return (f"<p class='qf-consent' data-tf-element-role='consent-language'>By clicking “<span data-tf-element-role='submit-text'>{c['submit']}</span>”, I agree to the "
            "<a href='/terms/' target='_blank' rel='noopener'>Terms</a> and <a href='/privacy/' target='_blank' rel='noopener'>Privacy Policy</a> and give my express written consent for "
            f"<span data-tf-element-role='consent-opted-advertiser-name-1'>{c['brand']}</span>, <a href='/partners/' target='_blank' rel='noopener'>its marketing partners</a>, and the {c['trade']} companies they work with "
            f"to contact me about my {c['trade']} project at the phone number and email I provided, including calls and text messages made with an automatic telephone dialing system or an "
            "artificial or prerecorded voice, even if my number is on a Do Not Call list. Consent is not a condition of any purchase; you can call us instead. "
            "Message frequency varies. Msg &amp; data rates may apply. Reply STOP to opt out, HELP for help.</p>")

def chips(name, opts, req):
    return (f'<div class="qc-group" data-group="{name}"{" data-required" if req else ""}>' +
            "".join(f'<button type="button" class="qc" data-name="{name}" data-val="{esc(v)}" aria-pressed="false">{esc(l)}</button>' for v, l in opts) + '</div>')

def form_html(c, eager=True):
    s1 = c["step1"]
    tiles = "".join(
        f'<button type="button" class="qt{" pic" if im else ""}" data-name="{s1["name"]}" data-val="{esc(v)}">' +
        (f'<span class="qt-img"><img src="{im}" alt="" width="320" height="220" {"fetchpriority=high" if eager and i < 4 else "loading=lazy"}></span>' if im else f'<span class="qt-ic">{ico}</span>') +
        f'<span class="qt-l">{esc(l)}</span></button>' for i, (v, l, im, ico) in enumerate(s1["opts"]))
    extra = "".join(f'<div class="qf-lbl">{esc(g["q"])}</div>{chips(g["name"], g["opts"], g.get("required", True))}' for g in c["step2_chips"])
    hp = '<input type="text" name="website" tabindex="-1" autocomplete="off" class="qf-hp" aria-hidden="true">'
    if c.get("mode") == "thumbtack":
        step3 = (f'<fieldset class="qf-step" data-step="2" hidden><legend class="qf-q">{esc(c["step3_q"])}</legend>\n <div class="qf-sum" data-sum></div>\n'
                 f' <p class="qf-ttnote">{c["tt_note"]}</p>\n'
                 f' <button type="submit" class="qf-btn block go" data-tt="quote-form">{esc(c["submit"])}</button>\n'
                 f' <p class="qf-secure">{LOCK} <span>Next you&rsquo;ll go to Thumbtack, our partner site, to compare {c["pros"]} near you. Thumbtack&rsquo;s '
                 "<a href='https://www.thumbtack.com/privacy/' target='_blank' rel='noopener'>Privacy Policy</a> and "
                 "<a href='https://www.thumbtack.com/terms/' target='_blank' rel='noopener'>Terms</a> apply.</span></p></fieldset>\n")
        wait = f'<div class="qf-wait" data-wait hidden><span class="qf-spin"></span><h3>Finding {c["pros"]} near you…</h3><p>Opening Thumbtack with {c["trade"]} pros that serve your area.</p></div>'
        hidden = hp
    else:
        step3 = OLD_STEP3.format(q=esc(c["step3_q"]), submit=c["submit"], consent=consent(c), LOCK=LOCK)
        wait = f'<div class="qf-wait" data-wait hidden><span class="qf-spin"></span><h3>Finding local pros near you…</h3><p>Checking {c["trade"]} companies that serve your ZIP code.</p></div>'
        hidden = hp + '<input type="hidden" name="xxTrustedFormCertUrl">'
    form = f'''<form class="qf" id="qf" novalidate>
<div class="qf-steps" aria-hidden="true"><span class="on" data-dot="0">1</span><i></i><span data-dot="1">2</span><i></i><span data-dot="2">3</span></div>
<fieldset class="qf-step" data-step="0"><legend class="qf-q">{esc(s1["q"])}</legend><div class="qt-grid">{tiles}</div><p class="qf-tap">Tap one to start · takes about 30 seconds</p></fieldset>
<fieldset class="qf-step" data-step="1" hidden><legend class="qf-q">{esc(c["step2_q"])}</legend>
 <div class="qf-lbl">ZIP code of the home</div>
 <div class="qf-zip"><span class="qf-zi">{PIN}</span><input class="qf-in big" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="Enter ZIP" aria-label="ZIP code"><span class="qf-zok" data-zok hidden></span></div>
 <div class="qf-lbl">Do you own this home?</div>{chips("homeowner", [("yes", "Yes, I own it"), ("no", "No")], True)}
 {extra}
 <button type="button" class="qf-btn block" data-next disabled>Continue</button><p class="qf-err" data-err hidden>Please enter a valid ZIP and answer each question.</p></fieldset>
{step3}<div class="qf-dq" data-dq hidden><h3>Thanks for checking</h3><p>The {c["trade"]} companies in our network work with homeowners. If you manage the property for an owner, ask them to start the request, or call us at <a href="tel:{c["tel"]}">{c["phone"]}</a>.</p><button type="button" class="qf-link" data-restart>Start over</button></div>
{wait}
{hidden}</form>'''
    return form

def embed(c, check):
    """Section 2 on site pages: same smart form, wrapped in <!--qf--> markers so the site's banned-word check skips the legal consent text.
    Returns (section_html, head_html, end_of_body_html, bottom_band_html)."""
    pts = "".join(f'<li>{CHECK}<span>{b}</span></li>' for b in c["bullets"])
    sec_html = (f'<!--qf--><section class="qsec" id="quote" style="--brand:{c["brand_color"]};--brand2:{c["brand_color2"]};--dark:{c["dark"]}"><div class="qsec-in">'
                f'<div class="qsec-copy"><p class="qsec-k">{c["embed_kicker"]}</p><h2>{c["embed_h2"]}</h2><p>{c["embed_sub"]}</p><ul class="lp-ticks">{pts}</ul>'
                f'<a class="qsec-call" href="tel:{c["tel"]}" data-call="quote-section">{PHONE}<span>Rather talk now? <b>{c["phone"]}</b></span></a></div>'
                f'<div class="lp-card">{form_html(c, eager=False)}</div></div>'
                f'<script type="application/json" id="qf-cfg">{json.dumps({"vertical": c["vertical"], "labels": c["labels"], "trade": c["trade"], "mode": c.get("mode", "leads"), "tt": c.get("tt", "")})}</script></section><!--/qf-->')
    band = (f'<!--qf--><section class="qband" style="--brand:{c["brand_color"]};--dark:{c["dark"]}"><div class="qband-in"><p><b>{c["band_text"]}</b></p>'
            f'<a class="qf-btn" href="#quote">{c["again"]}</a><a class="qband-call" href="tel:{c["tel"]}" data-call="quote-band">{PHONE} {c["phone"]}</a></div></section><!--/qf-->')
    probe = (sec_html + band).replace(consent(c), " ")
    probe = re.sub(r"(?i)\bquotes?\b", " ", probe)
    check(probe.replace("<!--qf-->", "").replace("<!--/qf-->", ""), "embedded quote section")
    head = f'<link rel="stylesheet" href="/assets/quote.css?v={c["v"]}">'
    end = ("" if c.get("mode") == "thumbtack" else TF) + f'<script src="/assets/quote.js?v={c["v"]}" defer></script>'
    return sec_html, head, end, band

def write(out, c, check):
    form = form_html(c)
    bullets = "".join(f'<li>{CHECK}<span>{b}</span></li>' for b in c["bullets"])
    gallery = "".join(f'<figure><img src="{u}" alt="{esc(a)}" loading="lazy" width="480" height="360"><figcaption>{esc(a)}</figcaption></figure>' for u, a in c["gallery"])
    faqs = "".join(f'<details><summary>{esc(q)}</summary><p>{a}</p></details>' for q, a in c["faqs"])
    how = "".join(f'<li><b>{i + 1}</b><h3>{h}</h3><p>{t}</p></li>' for i, (h, t) in enumerate(c["how"]))
    head = lambda title, desc, robots, extra="": f'''<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="{robots}"><link rel="canonical" href="{c["url"]}/get-a-quote/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><meta name="theme-color" content="{c["dark"]}">
<link rel="stylesheet" href="/assets/quote.css?v={c["v"]}"><style>:root{{--brand:{c["brand_color"]};--brand2:{c["brand_color2"]};--dark:{c["dark"]}}}</style>
<script src="/assets/config.js?v={c["v"]}"></script><script src="/assets/site.js?v={c["v"]}" defer></script>{extra}</head>'''
    top = (f'<header class="lp-top"><div class="lp-wrap lp-top-in"><a class="lp-brand" href="/">{c["logo_html"]}</a>'
           f'<a class="lp-call" href="tel:{c["tel"]}" data-call="get-a-quote-top">{PHONE}<span>Rather talk? <b>{c["phone"]}</b></span></a></div></header>')
    plink = "" if c.get("mode") == "thumbtack" else '<a href="/partners/">Marketing Partners</a>'
    foot = (f'<footer class="lp-foot"><div class="lp-wrap"><p>{c["disclaimer"]}</p><nav><a href="/privacy/">Privacy Policy</a><a href="/terms/">Terms</a>'
            f'<a href="{c["ca"]}">California Privacy</a><a href="{c["ca"]}#opt-out">Do Not Sell or Share My Personal Information</a>{plink}'
            f'<a href="/referral-disclosure/">Referral Disclosure</a></nav><p>&copy; 2026 {c["brand"]}</p></div></footer>')
    cfgjs = json.dumps({"vertical": c["vertical"], "labels": c["labels"], "trade": c["trade"], "mode": c.get("mode", "leads"), "tt": c.get("tt", "")})
    page = (head(c["title"], c["desc"], "index, follow", "" if c.get("mode") == "thumbtack" else TF) + '<body class="lp">' + top +
            f'<main><section class="lp-hero"><div class="lp-bg"><img src="{c["hero_img"]}" alt="" width="1800" height="1000"></div><div class="lp-wrap lp-hero-in">'
            f'<div class="lp-copy"><p class="lp-kick">{c["kicker"]}</p><h1>{c["h1"]}</h1><p class="lp-sub">{c["sub"]}</p><ul class="lp-ticks">{bullets}</ul></div>'
            f'<div class="lp-card">{form}</div></div></section>'
            f'<section class="lp-sec"><div class="lp-wrap"><h2>How it works</h2><ol class="lp-how">{how}</ol></div></section>'
            f'<section class="lp-sec soft"><div class="lp-wrap"><h2>{c["gallery_h"]}</h2><div class="lp-gal">{gallery}</div></div></section>'
            f'<section class="lp-sec"><div class="lp-wrap lp-faq"><h2>Questions</h2>{faqs}<p class="lp-again"><a href="#qf" class="qf-btn">{c["again"]}</a></p></div></section></main>'
            + foot + f'<script type="application/json" id="qf-cfg">{cfgjs}</script><script src="/assets/quote.js?v={c["v"]}" defer></script></body></html>')
    # banned-word check: consent + disclaimer are legal text; "quote" is allowed on this page only
    chk = page.replace(consent(c), " ").replace(c["disclaimer"], " ")
    chk = re.sub(r"(?i)\bquotes?\b", " ", chk)
    check(chk, "/get-a-quote/")
    thanks = (head(f"Thanks! | {c['brand']}", "Your request is in.", "noindex, follow") + '<body class="lp">' + top +
              f'<main><section class="lp-sec"><div class="lp-wrap lp-thanks"><span class="lp-ok">{CHECK}</span><h1>You&rsquo;re all set</h1>'
              f'<p class="lp-sub dark">Thanks! Your request is in. Local {c["trade"]} companies that serve your area may call or text you shortly, sometimes from a number you don&rsquo;t recognize, so keep your phone handy.</p>'
              '<ul class="lp-next"><li><b>Pick up the call</b> and tell them about your project.</li><li><b>Compare</b> what each company offers before you decide.</li><li><b>No pressure.</b> You are not obligated to hire anyone.</li></ul>'
              f'<p>Rather talk now? <a class="qf-btn" href="tel:{c["tel"]}" data-call="thanks">{PHONE} Call {c["phone"]}</a></p></div></section></main>' + foot + '</body></html>')
    plist = "".join(f"<li>{esc(p)}</li>" for p in c["partners"])
    partners = (head(f"Marketing Partners | {c['brand']}", "Companies that may contact you about your request.", "noindex, follow") + '<body class="lp">' + top +
                f'<main><section class="lp-sec"><div class="lp-wrap lp-doc"><h1>Marketing Partners</h1><p>When you submit a request on {c["url"].split("//")[1]} and agree to be contacted, '
                f'{c["brand"]} may share your request with the following companies and the {c["trade"]} companies they work with, so they can contact you about your project:</p>'
                f'<ul>{plist}</ul><p>You can ask any of them to stop contacting you at any time. To stop contact from us, see our <a href="/privacy/">Privacy Policy</a> or email <a href="mailto:{c["email"]}">{c["email"]}</a>.</p>'
                '</div></section></main>' + foot + '</body></html>')
    import shutil
    old = os.path.join(out, "get-matched")
    if os.path.isdir(old): shutil.rmtree(old)
    pages = (("get-a-quote", page), ("get-a-quote/thanks", thanks)) + ((("partners", partners),) if c.get("mode") != "thumbtack" else ())
    for path, html in pages:
        d = os.path.join(out, path); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w").write(html)
    for f in ("quote.css", "quote.js", "zip3.json"):
        open(os.path.join(out, "assets", f), "w").write(open(os.path.join(HERE, "qf_assets", f)).read())
    rp = os.path.join(out, "_redirects"); r = open(rp).read() if os.path.exists(rp) else ""
    if "/get-matched" not in r:
        open(rp, "w").write(r.rstrip("\n") + "\n/get-matched /get-a-quote/ 301\n/get-matched/ /get-a-quote/ 301\n/quote /get-a-quote/ 301\n")
    return ["/get-a-quote/"]
