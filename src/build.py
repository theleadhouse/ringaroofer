"""RingaRoofer v2 static site generator -> ../public  (python3 build.py)
Photo-led, call-first roofing referral site for Google/Microsoft paid search (inbound calls). Same URLs as v1 so ads, Search Console and links keep working.
Adds: real photos, app-style mobile bar, roof-problem picker, 60 Roof Questions answers (reviews removed), search-style FAQs, roof inspection + 'roofers near me' pages, Thumbtack backup link."""
import os, re, json, shutil
from html import escape as esc
from content import *
import legal
import faqs as FQ
from questions import Q as QS, CATS as QCATS
QBY = {q[0]: q for q in QS}

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.normpath(os.path.join(ROOT, "..", "public"))
V = "20261003"; UPDATED = "2026-10-03"
GSC_META = "xz9ncKiRn5z77EkCuE-lelMPzNC5h_5giCsF33PhNyk"
for _s in SERVICES: _s["faqs"] = _s["faqs"][:-1] + FQ.EXTRA.get(_s["slug"], []) + _s["faqs"][-1:] if _s["faqs"] and _s["faqs"][-1][0].startswith("Do you do") else _s["faqs"] + FQ.EXTRA.get(_s["slug"], [])
TOPIC = {"roof-repair": "Roof repair", "roof-leak-repair": "Roof leak", "emergency-roof-repair": "Emergency repair or tarp", "roof-tarping": "Emergency repair or tarp",
         "storm-roof-repair": "Storm or wind", "hail-roof-repair": "Hail", "roof-replacement": "Roof replacement or new roof", "new-roof": "Roof replacement or new roof", "roof-inspection": "Roof inspection"}

I = {
 "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>', "arrow": '<path d="M5 12h14M13 5l7 7-7 7"/>',
 "hammer": '<path d="m15 12-8.4 8.4a2.1 2.1 0 0 1-3-3L12 9"/><path d="M17.6 15 22 10.6M20.9 11.7l-1.3-1.3a2 2 0 0 1 0-2.8l.5-.5-3.6-3.6a5 5 0 0 0-7 0L9 4l4 1v2.3l2.4 2.4a2 2 0 0 1 2.8 0l1.3 1.3"/>',
 "drop": '<path d="M12 2.7s-6 6.3-6 11.3a6 6 0 0 0 12 0c0-5-6-11.3-6-11.3z"/>',
 "siren": '<path d="M7 18v-6a5 5 0 0 1 10 0v6"/><path d="M5 21a1 1 0 0 1-1-1v-1a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v1a1 1 0 0 1-1 1zM12 2v2M4.2 5.2l1.4 1.4M19.8 5.2l-1.4 1.4"/>',
 "tarp": '<path d="M3 11 12 4l9 7"/><path d="M5 10.5 12 15l7-4.5"/><path d="M5 10v9h14v-9"/>',
 "storm": '<path d="M19 16.9A5 5 0 0 0 18 7h-1.3a8 8 0 1 0-11.7 9"/><path d="m13 11-4 6h6l-4 6"/>',
 "hail": '<path d="M20 16.6A5 5 0 0 0 18 7h-1.3a8 8 0 1 0-12.7 8.9"/><circle cx="8" cy="19" r="1"/><circle cx="12" cy="21" r="1"/><circle cx="16" cy="19" r="1"/>',
 "house": '<path d="M3 10.5 12 3l9 7.5V21H3z"/><path d="M9 21v-7h6v7"/>',
 "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 12 10 5 10-5M2 17l10 5 10-5"/>',
 "shingle": '<path d="M2 12 12 4l10 8"/><path d="M5 11h14M4 14h16M3 17h18"/>', "metal": '<path d="M2 12 12 4l10 8"/><path d="M7 8v12M12 4v16M17 8v12"/>',
 "flat": '<rect x="3" y="8" width="18" height="12" rx="1"/><path d="M3 8h18l-1-3H4z"/>', "tile": '<path d="M2 12 12 4l10 8"/><path d="M4 15a2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0 2 2 0 0 0 4 0"/>',
 "slate": '<path d="M2 12 12 4l10 8"/><path d="M5 12h4v4H5zM10 12h4v4h-4zM15 12h4v4h-4z"/>', "shake": '<path d="M2 12 12 4l10 8"/><path d="M6 11v7M10 10v9M14 10v9M18 11v7"/>',
 "map": '<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12z"/><circle cx="12" cy="9" r="2.5"/>', "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>', "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>', "chev": '<path d="m6 9 6 6 6-6"/>', "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
 "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>', "ext": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
 "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M9 21v-6h6v6"/>', "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
 "chat": '<path d="M21 12a8 8 0 0 1-11.6 7.1L3 21l1.9-6.4A8 8 0 1 1 21 12z"/>', "help": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
 "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
}
def ic(n, s=22): return f'<svg class="ic" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{I[n]}</svg>'
def call_btn(cls="btn btn-call", label=None, place=""):
    return f'<a class="{cls}" href="tel:{TEL}" data-call="{place}">{ic("phone",19)}<span>{label or "Call " + PHONE}</span></a>'
def tt_link(campaign, label="Rather book online? Compare roofers on Thumbtack, our partner", cls="tt-text"):
    return f'<a class="{cls}" href="{tt(campaign)}" target="_blank" rel="sponsored noopener" data-tt="{campaign}">{label} {ic("ext",14)}</a>'
def pic(key, w=900, h=None, eager=False, cls=""):
    src, alt, _ = P[key]
    ld = 'fetchpriority="high"' if eager else 'loading="lazy"'
    hh = h or int(w * .7)
    return (f'<img class="{cls}" src="{img(src, w, hh)}" srcset="{img(src, w // 2, hh // 2)} {w // 2}w, {img(src, w, hh)} {w}w, {img(src, int(w * 1.5), int(hh * 1.5))} {int(w * 1.5)}w" '
            f'sizes="(max-width: 700px) 100vw, {w}px" width="{w}" height="{hh}" alt="{esc(alt)}" {ld} decoding="async">')

LOGO = ('<svg class="logo-mark" width="42" height="42" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="#13233A"/>'
        '<path d="M8 22 20 12l12 10" fill="none" stroke="#F26B1D" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M12 21v9h16v-9" fill="none" stroke="#fff" stroke-width="2.4" stroke-linejoin="round"/>'
        '<path d="M26.5 7.5a6 6 0 0 1 3.5 3.5M28 4.5a9.5 9.5 0 0 1 5.5 5.5" fill="none" stroke="#F26B1D" stroke-width="2" stroke-linecap="round"/></svg>')
BRANDH = f'{LOGO}<span class="wm"><span>Ringa<em>Roofer</em></span><small>Roofers near you, one call</small></span>'
NAV = [("Services", "/services/", [(s["name"], f"/services/{s['slug']}/") for s in SERVICES]), ("Roof Types", "/roof-types/", [(t["name"], f"/roof-types/{t['slug']}/") for t in TYPES]),
       ("Roof Leak?", "/services/roof-leak-repair/", None), ("Coverage", "/coverage/", None), ("Roof Questions", "/questions/", None)]
SOLO = ("/services/roof-leak-repair/",)

def header(active):
    li = []
    for t, h, sub in NAV:
        cur = ' aria-current="page"' if active == h or (sub and active.startswith(h) and active not in SOLO) else ""
        if sub:
            dd = "".join(f'<a href="{u}">{n}</a>' for n, u in sub)
            li.append(f'<li class="has-dd"><a href="{h}"{cur}>{t}</a><button class="dd-btn" aria-label="{t} menu" aria-expanded="false">{ic("chev",16)}</button><div class="dd">{dd}</div></li>')
        else:
            li.append(f'<li><a href="{h}"{cur}>{t}</a></li>')
    mob = "".join(f'<a href="{h}">{t}</a>' + ("".join(f'<a class="sub" href="{u}">{n}</a>' for n, u in sub) if sub else "") for t, h, sub in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap tb-in"><span>{ic("storm",15)} Leaks, storm-hit roofs, new roofs and re-roofs · Roofers in all 50 states</span><a href="tel:{TEL}" data-call="topbar">Call {PHONE}</a></div></div>
<header class="hdr"><div class="wrap hdr-in">
 <a class="brand" href="/" aria-label="RingaRoofer home">{BRANDH}</a>
 <nav class="nav" aria-label="Main"><ul>{"".join(li)}</ul></nav>
 <div class="hdr-cta">{call_btn("btn btn-call hdr-call", PHONE, "header")}<button class="menu" aria-label="Open menu" aria-expanded="false" aria-controls="mnav">{ic("menu",26)}</button></div>
</div>
<div class="mnav" id="mnav" hidden><nav aria-label="Mobile">{mob}<a href="/roofers-near-me/">Roofers Near Me</a><a href="/library/">Roof Library</a><a href="/community/">Real Roof Problems</a><a href="/how-it-works/">How It Works</a><a href="/contact/">Request a Callback</a></nav>{call_btn("btn btn-call block", None, "mobile-menu")}</div>
</header>'''

DISCLAIMER = ("RingaRoofer.com is a referral service that connects homeowners with independent local roofing contractors. RingaRoofer does not charge homeowners and does not perform roofing work. "
              "All contractors are independent, and RingaRoofer does not warrant or guarantee any work performed. Homeowners should confirm that any contractor they hire holds the credentials and coverage required for the work in their area. "
              "RingaRoofer is a Thumbtack partner and may be paid when you use Thumbtack through links on this site. Thumbtack is a separate company. "
              "Photos are real photographs from Pexels and Unsplash shown for illustration; they do not show specific companies or jobs. Calls may be recorded for quality purposes.")
def footer():
    svc = "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    typ = "".join(f'<li><a href="/roof-types/{t["slug"]}/">{t["name"]}</a></li>' for t in TYPES)
    return f'''<section class="cta-final"><div class="cta-bg">{pic("newroof", 1600, 700)}</div><div class="wrap cta-in"><p class="kick">Roof problem?</p><h2>Talk to a roofer today.</h2><p>One call connects you with an independent roofing company that serves your area: repairs, leaks, new roofs, re-roofs and fast emergency service.</p>
<div class="btns">{call_btn("btn btn-call xl", None, "footer-cta")}<a class="btn btn-ghost light xl" href="/contact/">Request a callback</a></div>{tt_link("footer", cls="tt-text light")}</div></section>
<footer class="ftr"><div class="wrap">
 <div class="f-grid">
  <div class="f-brand"><a class="brand" href="/">{BRANDH}</a><p>Connecting homeowners with independent roofing companies across the United States.</p>
   <p><a class="f-phone" href="tel:{TEL}" data-call="footer">{ic("phone",18)} {PHONE}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p></div>
  <div><h2>Services</h2><ul>{svc}</ul></div>
  <div><h2>Roof Types</h2><ul>{typ}</ul></div>
  <div><h2>RingaRoofer</h2><ul><li><a href="/roofers-near-me/">Roofers Near Me</a></li><li><a href="/questions/">Roof Questions</a></li><li><a href="/how-it-works/">How It Works</a></li><li><a href="/coverage/">Coverage by State</a></li><li><a href="/community/">Real Roof Problems</a></li><li><a href="/library/">Roof Library</a></li><li><a href="/contact/">Request a Callback</a></li><li><a href="/sitemap/">Site Map</a></li></ul></div>
 </div>
 <p class="disc">{DISCLAIMER}</p>
 <div class="f-legal"><nav aria-label="Legal"><a href="/privacy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/referral-disclosure/">Referral Disclosure</a><a href="/california-privacy/">California Privacy</a><a href="/california-privacy/#opt-out">Do Not Sell or Share My Personal Information</a><a href="/do-not-call/">Do Not Call</a><a href="/accessibility/">Accessibility</a></nav>
 <p>&copy; 2026 RingaRoofer.com</p></div>
</div></footer>
<nav class="tabbar" aria-label="Quick actions"><a href="/" class="tb-i">{ic("home",21)}<span>Home</span></a><a href="/services/" class="tb-i">{ic("grid",21)}<span>Services</span></a><a href="tel:{TEL}" class="tb-call" data-call="tabbar" aria-label="Call {PHONE}">{ic("phone",24)}<span>Call</span></a><a href="/questions/" class="tb-i">{ic("help",21)}<span>Questions</span></a><button type="button" class="tb-i tb-menu" aria-controls="mnav">{ic("menu",21)}<span>Menu</span></button></nav>'''

def crumbs(trail):
    if not trail: return ""
    items = [("Home", "/")] + trail
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
        f'<li><a href="{u}">{n}</a></li>' if i < len(items) - 1 else f'<li aria-current="page">{n}</li>' for i, (n, u) in enumerate(items)) + '</ol></nav>'

def schema(p):
    g = [{"@type": "Organization", "@id": URL + "/#org", "name": BRAND, "url": URL + "/", "logo": URL + "/assets/img/logo-512.png", "email": EMAIL, "telephone": TEL,
          "areaServed": {"@type": "Country", "name": "United States"}, "description": "RingaRoofer is a roofing referral service that connects homeowners with independent local roofing companies.",
          "contactPoint": {"@type": "ContactPoint", "telephone": TEL, "contactType": "customer service", "areaServed": "US", "availableLanguage": "en"}},
         {"@type": "WebSite", "@id": URL + "/#site", "url": URL + "/", "name": BRAND, "publisher": {"@id": URL + "/#org"}},
         {"@type": p.get("stype", "WebPage"), "@id": URL + p["url"] + "#page", "url": URL + p["url"], "name": p["title"], "description": p["desc"], "isPartOf": {"@id": URL + "/#site"}, "dateModified": UPDATED, "inLanguage": "en-US"}]
    if p.get("ogimg"): g[-1]["primaryImageOfPage"] = {"@type": "ImageObject", "url": p["ogimg"]}
    if p.get("trail"):
        items = [("Home", "/")] + p["trail"]
        g.append({"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": URL + u} for i, (n, u) in enumerate(items)]})
    if p.get("faqs"):
        g.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": re.sub("<[^>]+>", "", q), "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a)}} for q, a in p["faqs"]]})
    if p.get("service"):
        g.append({"@type": "Service", "name": p["service"], "serviceType": p["service"], "provider": {"@id": URL + "/#org"},
                  "areaServed": {"@type": "State", "name": p["state"]} if p.get("state") else {"@type": "Country", "name": "United States"}, "description": p["desc"]})
    if p.get("article"):
        g.append({"@type": "Article", "headline": p["h1"], "description": p["desc"], "datePublished": UPDATED, "dateModified": UPDATED, "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@id": URL + "/#org"}, "mainEntityOfPage": URL + p["url"]})
    return json.dumps({"@context": "https://schema.org", "@graph": g}, separators=(",", ":"))

def page(p):
    og = p.get("ogimg") or URL + "/assets/img/og.png"
    return f'''<!doctype html>
<html lang="en-US"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(p["title"])}</title>
<meta name="description" content="{esc(p["desc"])}">
<link rel="canonical" href="{URL}{p["url"]}">
<meta name="robots" content="{"noindex, follow" if p.get("noindex") else "index, follow, max-image-preview:large, max-snippet:-1"}">
<meta name="google-site-verification" content="{GSC_META}">
<meta property="og:type" content="{"article" if p.get("article") else "website"}"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{esc(p["title"])}"><meta property="og:description" content="{esc(p["desc"])}"><meta property="og:url" content="{URL}{p["url"]}">
<meta property="og:image" content="{og}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#13233A"><meta name="format-detection" content="telephone=yes">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/img/logo-192.png">
<link rel="preconnect" href="https://images.pexels.com"><link rel="preconnect" href="https://images.unsplash.com">
<link rel="stylesheet" href="/assets/site.css?v={V}">
<script type="application/ld+json">{schema(p)}</script>
<script src="/assets/config.js?v={V}"></script>
<script src="/assets/site.js?v={V}" defer></script>
</head>
<body class="{p.get("cls","")}">
{header(p["url"])}
<main id="main">
{p["hero"]}
{p["body"]}
</main>
{footer()}
{legal.TF_SCRIPT if p.get("form") else ""}
</body></html>
'''

# ---------------------------------------------------------------- blocks
def sec(inner, cls="", title=None, kicker=None, intro=None, id_=None):
    if not inner: return ""
    head = f'<div class="sec-h">{f"<p class=kick>{kicker}</p>" if kicker else ""}<h2>{title}</h2>{f"<p>{intro}</p>" if intro else ""}</div>' if title else ""
    return f'<section class="sec {cls}"{f" id={id_}" if id_ else ""}><div class="wrap">{head}{inner}</div></section>'
def svc_cards(items=SERVICES):
    cta = (f'<div class="pcard card-cta"><p class="kick">Not sure what\'s wrong?</p><h3>Just call and describe it</h3><p>Tell us what your roof is doing. We\'ll connect you with a local roofing company.</p>{call_btn("btn btn-call block", None, "services-grid")}</div>' if len(items) % 3 == 2 else "")
    return '<div class="pgrid">' + "".join(
        f'<a class="pcard" href="/services/{s["slug"]}/"><div class="pc-img">{pic(s["photo"], 640, 440)}<span class="pc-ic">{ic(s["icon"],22)}</span></div><div class="pc-body"><h3>{s["name"]}</h3><p>{s["short"]}</p><span class="more">Get a roofer {ic("arrow",16)}</span></div></a>' for s in items) + cta + '</div>'
def type_cards():
    return '<div class="pgrid">' + "".join(
        f'<a class="pcard" href="/roof-types/{t["slug"]}/"><div class="pc-img">{pic(t["photo"], 640, 440)}<span class="pc-ic">{ic(t["icon"],22)}</span></div><div class="pc-body"><h3>{t["name"]}</h3><p>{t["lead"]}</p><span class="more">Roofers for this {ic("arrow",16)}</span></div></a>' for t in TYPES) + '</div>'
def steps():
    return ('<ol class="steps">'
            f'<li><span>1</span><h3>Call {PHONE}</h3><p>Tell us what\'s going on with your roof and your ZIP code. It takes about a minute.</p></li>'
            '<li><span>2</span><h3>Talk to a local roofer</h3><p>We connect your call to an independent roofing company that serves your area.</p></li>'
            '<li><span>3</span><h3>You decide</h3><p>Talk it through, set up a visit, and choose whether to go ahead. No obligation.</p></li></ol>')
def faq_html(faqs):
    return '<div class="faq">' + "".join(f'<details><summary>{q}{ic("chev",18)}</summary><p>{a}</p></details>' for q, a in faqs) + '</div>'
def tt_btn(campaign, label="See roofers on Thumbtack", cls="btn btn-tt"):
    return f'<a class="{cls}" href="{tt(campaign)}" target="_blank" rel="sponsored noopener" data-tt="{campaign}">{ic("calendar",18)}<span>{label}</span></a>'
def ttbox(campaign):
    return (f'<div class="ttbox"><div><p class="kick">Our partner</p><h3>Rather book online?</h3><p>Compare local roofers, see their reviews and past jobs, and book online through Thumbtack. If the roof is leaking now, calling is quickest.</p></div>'
            f'{tt_btn(campaign)}</div>')
def now_box():
    return (f'<div class="nowbox"><p class="kick">{ic("drop",16)} Roof leaking right now?</p><h3>Do these while you call</h3><ol>'
            '<li><b>Catch the water</b> and move belongings away.</li><li><b>Keep out</b> of rooms with a sagging ceiling.</li>'
            '<li><b>Take photos</b> of the ceiling and the roof from the ground.</li><li><b>Stay off the roof</b>, especially when it\'s wet.</li></ol>'
            f'{call_btn("btn btn-call block", None, "now-box")}</div>')
def phero(h1, lead, trail, campaign, photo, alerts=None):
    al = f'<div class="alerts" data-alerts="{alerts}" hidden></div>' if alerts else ""
    return (f'<section class="phero"><div class="ph-bg">{pic(photo, 1600, 760, eager=True)}</div><div class="wrap phero-in"><div class="ph-txt">{crumbs(trail)}<h1>{h1}</h1><p class="lead">{lead}</p>'
            f'<div class="btns">{call_btn("btn btn-call xl", None, "page-hero")}<a class="btn btn-ghost light xl" href="/contact/">Request a callback</a></div>{tt_link(campaign, cls="tt-text light")}'
            f'<p class="ph-note">{ic("check",16)} Independent local roofing companies · Repairs, new roofs and re-roofs · No obligation</p>{al}</div></div></section>')
def lhero(h1, trail, sub=""):
    return f'<section class="phero lg"><div class="wrap">{crumbs(trail)}<h1>{h1}</h1>{f"<p class=lead>{sub}</p>" if sub else ""}</div></section>'
def st_slug(n): return n.lower().replace(" ", "-").replace(",", "").replace(".", "")
def problems():
    return '<div class="scenes six">' + "".join(f'<a class="scene" href="{u}"><div class="sc-img">{pic(k, 520, 620)}</div><div class="sc-cap"><h3>{t}</h3><span>{ic("arrow",16)}</span></div></a>' for t, k, u in PROBLEMS) + '</div>'
def matcher():
    chips = "".join(f'<button type="button" class="mchip" aria-pressed="false" data-k="{k}" data-route="{r}" data-url="{u}" data-name="{esc(t)}" data-msg="{esc(m)}" data-photo="{img(P[ph][0], 900, 640)}">{ic("check",15)}<span>{t}</span></button>' for k, t, ph, u, r, m in PROJECTS)
    return (f'<div class="match" id="match"><div class="m-left"><p class="kick">Step 1 of 2</p><h2>What\'s going on with your roof?</h2><p class="m-sub">Pick the one that fits and we\'ll show you the quickest way to get it handled.</p><div class="m-chips">{chips}</div></div>'
            f'<div class="m-right" aria-live="polite"><div class="m-img"><img data-mimg src="{img(P["roofer"][0], 900, 640)}" alt="Roofer installing shingles on a home" width="900" height="640" loading="lazy"></div>'
            f'<div class="m-card"><p class="kick">Step 2 of 2</p><h3 data-mtitle>Choose what fits</h3><p data-mtext>Every option is a quick call: we connect you with a local roofing company that handles it.</p>'
            f'<div class="btns m-call">{call_btn("btn btn-call", None, "matcher")}<a class="btn btn-ghost" data-mlink href="/services/">See details</a></div>'
            f'<div class="btns m-tt" hidden>{tt_btn("matcher", "Compare roofers on Thumbtack")}{call_btn("btn btn-ghost", "Or call", "matcher-alt")}</div></div></div></div>')
def pro_strip():
    items = [("roofer2", "Shingle roofs"), ("metal", "Metal roofs"), ("flat", "Flat roofs"), ("tile", "Tile roofs")]
    return '<div class="pros">' + "".join(f'<figure>{pic(k, 520, 620)}<figcaption>{t}</figcaption></figure>' for k, t in items) + '</div><p class="small center">Real photos, shown for illustration. They don\'t show a specific company.</p>'
def straight_talk():
    pts = [("Local roofing companies", "Your call goes to an independent roofing company that works in your area."),
           ("Straight answers", "Describe what your roof is doing. They'll tell you what it likely is and when they can come."),
           ("You're in charge", "No obligation. Agree any work directly with the roofing company."),
           ("Every kind of roof", "Asphalt shingle, metal, flat, tile, slate and cedar shake.")]
    return '<div class="talk">' + "".join(f'<div><span class="pipe-dot"></span><h3>{t}</h3><p>{d}</p></div>' for t, d in pts) + '</div>'
def marquee():
    row = "".join(f'<span>{ic("house",15)} {c}</span>' for c in NEIGHBORHOODS)
    return f'<div class="marq" aria-label="Some of the cities we connect homeowners in"><div class="marq-in">{row}{row}</div></div>'
def seasons():
    return '<div class="seasons">' + "".join(f'<div class="season{" now" if i == 0 else ""}"><h3>{n}</h3><p>{d}</p></div>' for i, (n, d) in enumerate(SEASONS)) + '</div>'
def story_cards(items=STORIES):
    return '<div class="stories">' + "".join(
        f'<article class="story"><div class="st-img">{pic(ph, 560, 360)}</div><div class="st-body"><p class="tag">Common situation</p><h3>{t}</h3><p>{what}</p><p class="tip"><b>What helps:</b> {tip}</p><a class="more" href="{u}">Get help with this {ic("arrow",16)}</a></div></article>'
        for t, ph, what, tip, u in items) + '</div>'
def q_cards(items, more=True):
    return ('<div class="qlist">' + "".join(f'<a class="qcard" href="/questions/{q[0]}/"><span class="qc-ic">{ic("help",20)}</span><span><b>{q[1]}</b><small>{q[5][:118].rsplit(" ", 1)[0].rstrip(".,:;")}…</small></span>{ic("arrow",16)}</a>' for q in items) + '</div>'
            + ('<p class="center"><a class="btn btn-ghost" href="/questions/">All 60 roof questions</a></p>' if more else ""))
def related_q(url, n=4):
    hits = [q for q in QS if q[4] == url]
    return (hits + [q for q in QS if q not in hits])[:n]
def jump(items):
    return '<nav class="jump" aria-label="On this page">' + "".join(f'<a href="#{i}">{t}</a>' for t, i in items) + f'<a class="j-call" href="tel:{TEL}" data-call="jump">{ic("phone",15)} Call</a></nav>'
def trust():
    return ('<div class="trust"><div>' + ic("users") + '<span><b>One call, one roofer</b>A company that serves your area</span></div><div>' + ic("siren") + '<span><b>Fast emergency service</b>Leaks and storm-hit roofs</span></div><div>'
            + ic("house") + '<span><b>Full service roofing</b>Repairs, new roofs, re-roofs</span></div><div>' + ic("map") + '<span><b>Nationwide</b>Roofers in all 50 states</span></div></div>')

PAGES = []
def add(**p): PAGES.append(p)

# ---------------------------------------------------------------- home
home_hero = f'''<section class="hero">
 <div class="hero-bg">{pic("roofer2", 1900, 1100, eager=True)}</div>
 <div class="wrap hero-in">
  <div class="hero-txt">
   <p class="kick live"><span class="dot"></span>Roofers near you · Nationwide</p>
   <h1>Need a roofer near you? <em>Get one on the phone now.</em></h1>
   <p class="lead">Roof leak, storm-hit shingles, hail, or time for a new roof. One call connects you with an independent roofing company that serves your area.</p>
   <div class="btns">{call_btn("btn btn-call xl pulse", None, "home-hero")}<a class="btn btn-ghost light xl" href="#match">{ic("house",18)}<span>What's wrong with my roof?</span></a></div>
   {tt_link("home-hero", cls="tt-text light")}
  </div>
  <div class="hero-side">{now_box()}</div>
 </div>
</section>
{marquee()}
<section class="alertband" id="alerts"><div class="wrap"><div class="alerts" data-alerts="US" hidden></div></div></section>'''
HOME_FAQS = [
 ("What is RingaRoofer?", "A roofing referral service. When you call, we connect you with an independent roofing company that serves your area. We don't do roofing work ourselves."),
 ("Is there a charge to call?", "No. RingaRoofer doesn't charge homeowners. You agree any work and terms directly with the roofing company."),
 ("What roofing work is covered?", "Full service roofing: repairs, leak repairs, inspections, new roofs, re-roofs and fast emergency service, on asphalt shingle, metal, flat, tile, slate and cedar shake roofs."),
 ("Do you cover my area?", "Our network covers all 50 states. Availability can vary by ZIP code and type of work, so call and we'll check for you."),
 ("Are the photos your jobs?", "No. They're real photographs from Pexels and Unsplash. Ask the roofer you speak with about their own work.")] + FQ.HOME
home_body = (
 sec(trust(), "tight trustsec")
 + sec(matcher(), "", None, id_="match-sec")
 + sec(problems(), "soft", "What's your roof doing?", "Recognize it?", "Tap the one that looks like yours.")
 + sec(svc_cards(), "", "Full service roofing", "Services", "From a few missing shingles to a complete re-roof, one call puts you in touch with a roofer who handles it.", id_="help")
 + sec(steps(), "soft", "How it works", "Simple", id_="how-it-works")
 + sec(type_cards(), "", "Every type of roof", "Roof types", "Asphalt shingle, metal, flat, tile, slate and cedar shake.")
 + f'<section class="band"><div class="band-bg">{pic("storm", 1800, 800)}</div><div class="wrap band-in"><p class="kick">Storm season</p><h2>Storm last night? Get the roof checked.</h2><p>High wind lifts shingles and hail bruises them, often without anything visible from the ground. Stay off the roof, photograph what you can see, and call. We\'ll connect you with a local roofer.</p><div class="btns">{call_btn("btn btn-call xl", None, "storm-band")}<a class="btn btn-ghost light" href="/services/storm-roof-repair/">Storm roof repair {ic("arrow",16)}</a></div></div></section>'
 + sec(straight_talk(), "", "Straight talk, local roofers", "Why call us")
 + sec(seasons(), "soft", "Roofing through the year", "Seasonal")
 + sec(pro_strip(), "", "Real roofs, real work", "Photos")
 + sec(story_cards(STORIES[:3]) + '<p class="center"><a class="btn btn-ghost" href="/community/">More real roof problems</a></p>', "soft", "Roof problems homeowners call about", "Sound familiar?", "Typical situations and what helps. These are examples, not reviews.")
 + sec(q_cards([QBY[k] for k in ("why-is-my-roof-leaking", "repair-or-replace-roof", "signs-you-need-a-new-roof", "how-to-tell-if-hail-hit-roof", "asphalt-shingles-vs-metal", "how-to-find-a-roofer-near-me")]), "", "Roof questions homeowners ask", "Roof Questions", "Straight answers to the questions homeowners search most.", id_="questions")
 + sec(ttbox("home"), "tight soft")
 + sec('<div class="states">' + "".join(f'<a href="/coverage/{st_slug(s[1])}/">{s[1]}</a>' for s in STATES) + '</div>', "", "Roofers in all 50 states", "Coverage", "Availability can vary by ZIP code.", id_="coverage")
 + sec(faq_html(HOME_FAQS), "soft", "Common questions", "FAQ", id_="faq"))
add(url="/", title="Roofers Near You | Roof Repair & New Roofs · Call (855) 635-9281 | RingaRoofer", desc="Need a roofer near you? Call (855) 635-9281 to connect with a local roofing company for roof repair, leaks, storm and hail repair, new roofs and re-roofs.",
    h1="Need a roofer near you?", hero=home_hero, body=home_body, faqs=HOME_FAQS, cls="home", ogimg=img(P["roofer2"][0], 1200, 630))

# ---------------------------------------------------------------- roofers near me (head-term ad landing page)
RNM_FAQ = [("How do I find a roofer near me?", f"Call {PHONE}. Tell us your ZIP code and what's going on with your roof, and we'll connect you with an independent roofing company that serves your area."),
           ("What should I ask a roofer before hiring?", "How long they've worked locally, who will be on the roof, what the written scope of work includes, how they protect your property, and the credentials your state requires."),
           ("Can a roofer come out this week?", "Often, yes. It depends on your area and recent weather. After storms, roofers book up quickly, so call early.")]
add(url="/roofers-near-me/", title="Roofers Near Me | Local Roofing Companies · Call (855) 635-9281 | RingaRoofer", desc="Looking for roofers near you? One call to (855) 635-9281 connects you with an independent local roofing company for repairs, leaks, inspections, new roofs and re-roofs.",
    h1="Roofers near you", trail=[("Roofers Near Me", "/roofers-near-me/")], faqs=RNM_FAQ, service="Roofing referral",
    hero=phero("Roofers near you, one call away", "Repairs, leaks, storm and hail, inspections, new roofs and re-roofs. Tell us your ZIP code and we'll connect you with an independent roofing company that serves your area.", [("Roofers Near Me", "/roofers-near-me/")], "roofers-near-me", "aerial", alerts="US"),
    body=sec(trust(), "tight trustsec") + sec(svc_cards(), "", "What local roofers handle", "Services") + sec(steps(), "soft", "How it works", "Simple")
         + sec(q_cards([QBY[k] for k in ("how-to-find-a-roofer-near-me", "questions-to-ask-a-roofer", "how-fast-can-a-roofer-come", "roofer-door-to-door")]), "", "Before you hire", "Roof Questions", id_="questions") + sec(faq_html(RNM_FAQ), "soft", "Questions", "FAQ") + sec(ttbox("roofers-near-me"), "tight"))

# ---------------------------------------------------------------- services
add(url="/services/", title="Roofing Services: Repair, Leaks, Inspection, Replacement & Emergency | RingaRoofer", desc="Full service roofing: roof repair, leak repair, inspections, emergency roofing, storm and hail repair, roof replacement, new roofs and re-roofs. Call (855) 635-9281.",
    h1="Roofing services", trail=[("Services", "/services/")], hero=phero("Full service roofing, one call away", "Repairs, inspections, new roofs, re-roofs and fast emergency service. Choose your problem below, or just call.", [("Services", "/services/")], "services", "roofer"),
    body=sec(svc_cards()) + sec(steps(), "soft", "How it works") + sec(ttbox("services"), "tight"))
GAL = ["roofer", "shingles2", "storm2", "hail", "tearoff", "inspect", "aerial", "flat2", "newroof"]
STORMY = ("storm-roof-repair", "hail-roof-repair", "emergency-roof-repair", "roof-tarping")
for s in SERVICES:
    u = f'/services/{s["slug"]}/'
    rel = [x for x in SERVICES if x is not s][:3]
    gal = [k for k in GAL if k != s["photo"]][(len(s["slug"]) % 5):][:3]
    side = f'<aside class="doc-side"><div class="sticky">{now_box()}</div></aside>'
    body = (sec(jump([("What to know", "about"), ("Photos", "photos"), ("FAQ", "faq"), ("Questions", "questions")]), "jumpsec")
            + sec('<div class="doc">' + "".join(f'<h2>{h}</h2>{b}' for h, b in s["sections"]) + '</div>' + side, "doc-wrap", id_="about")
            + sec('<div class="gal">' + "".join(f'<figure>{pic(k, 600, 440)}<figcaption>{P[k][1]}</figcaption></figure>' for k in gal) + '</div>', "soft", "Real roofs, real problems", "Photos", id_="photos")
            + sec(steps(), "", "How it works", "Simple")
            + sec(faq_html(s["faqs"]), "soft", f'{s["name"]}: common questions', "FAQ", id_="faq")
            + sec(q_cards(related_q(u)), "", "Homeowners also ask", "Roof Questions", id_="questions")
            + sec(ttbox(s["slug"] + "-box"), "tight")
            + sec(svc_cards(rel), "soft", "Related roofing services"))
    add(url=u, title=s["title"], desc=s["desc"], h1=s["h1"], trail=[("Services", "/services/"), (s["name"], u)],
        hero=phero(s["h1"], s["lead"], [("Services", "/services/"), (s["name"], u)], s["slug"], s["photo"], alerts="US" if s["slug"] in STORMY else None),
        body=body, faqs=s["faqs"], service=s["name"], ogimg=img(P[s["photo"]][0], 1200, 630))

# ---------------------------------------------------------------- roof types
add(url="/roof-types/", title="Roof Types: Shingle, Metal, Flat, Tile, Slate & Cedar | RingaRoofer", desc="Asphalt shingle, metal, flat (TPO, EPDM), tile, slate and cedar shake roofs: repairs and replacements from roofers near you. Call (855) 635-9281.",
    h1="Roof types", trail=[("Roof Types", "/roof-types/")], hero=phero("Every type of roof", "Whatever your roof is made of, one call connects you with a roofer who works with it.", [("Roof Types", "/roof-types/")], "roof-types", "shingles"),
    body=sec(type_cards()) + sec('<p class="center"><a class="btn btn-ghost" href="/library/choosing-a-roofing-material/">Compare roofing materials</a></p>', "tight"))
for t in TYPES:
    u = f'/roof-types/{t["slug"]}/'; fq = FQ.TYPES_EXTRA.get(t["slug"], [])
    add(url=u, title=t["title"], desc=t["desc"], h1=t["h1"], trail=[("Roof Types", "/roof-types/"), (t["name"], u)], faqs=fq or None, ogimg=img(P[t["photo"]][0], 1200, 630),
        hero=phero(t["h1"], t["lead"], [("Roof Types", "/roof-types/"), (t["name"], u)], "type-" + t["slug"], t["photo"]),
        body=sec(f'<div class="doc">{t["body"]}</div><aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap")
             + (sec(faq_html(fq), "soft", "Questions", "FAQ") if fq else "") + sec(svc_cards(SERVICES[:3]), "", "Popular services"), service=f'{t["name"]} repair and replacement')

# ---------------------------------------------------------------- coverage
RPHOTO = {"Northeast": "shingles2", "Southeast": "storm2", "Midwest": "hail", "South Central": "storm", "Mountain West": "metal", "West": "tile"}
by_region = {}
for code, name, reg, cities, extra in STATES: by_region.setdefault(reg, []).append(name)
cov = "".join(f'<div class="region"><div class="rg-img">{pic(RPHOTO[r], 520, 340)}</div><div><h3>{r}</h3><p>{REGIONS[r]}</p><div class="states">' + "".join(f'<a href="/coverage/{st_slug(n)}/">{n}</a>' for n in v) + '</div></div></div>' for r, v in by_region.items())
add(url="/coverage/", title="Roofers Near You in All 50 States | RingaRoofer Coverage", desc="RingaRoofer connects homeowners with independent roofing companies in all 50 states and D.C. Find roofing help in your state. Call (855) 635-9281.",
    h1="Coverage", trail=[("Coverage", "/coverage/")], hero=phero("Roofers near you, nationwide", "Our network connects homeowners with independent roofing companies across the country. Availability can vary by ZIP code.", [("Coverage", "/coverage/")], "coverage", "aerial2", alerts="US"),
    body=sec(cov))
for code, name, reg, cities, extra in STATES:
    u = f"/coverage/{st_slug(name)}/"
    fq = [(f"Do you have roofers in {name}?", f"Yes. Our network connects homeowners across {name} with independent roofing companies. Availability can vary by ZIP code and type of work."),
          (f"How fast can a roofer come out in {name}?", "It depends on your location, the season and recent weather. After major storms roofers book up quickly, so call early.")]
    body = (sec(f'<div class="doc"><h2>Roofing in {name}</h2><p>{extra} {REGIONS[reg]}</p><h2>Roofing help we connect {name} homeowners with</h2><ul class="ticks">'
                + "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a>: {s["short"]}</li>' for s in SERVICES) + '</ul>'
                + f'<h2>Areas served in {name}</h2><p>Homeowners across {name} call us, including in and around ' + ", ".join(cities[:-1]) + f' and {cities[-1]}. Call and we\'ll check availability for your ZIP code.</p>'
                + f'<h2>Before you hire a roofer in {name}</h2><ul class="ticks"><li>Ask how long they\'ve worked in {name} and for local references.</li><li>Confirm they hold the credentials and coverage {name} requires for roofing work.</li><li>Get the scope of work in writing before work starts.</li><li>After big storms, be cautious with door-to-door crews.</li></ul></div>'
                f'<aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap")
            + sec(svc_cards(SERVICES[:3]), "soft", f"Popular roofing services in {name}") + sec(ttbox("state-" + code.lower()), "tight") + sec(faq_html(fq), "", "Questions"))
    add(url=u, title=f"Roofers in {name} | Roof Repair & Replacement | RingaRoofer", desc=f"Need a roofer in {name}? Call (855) 635-9281 to connect with a local roofing company for roof repair, leaks, new roofs, re-roofs and emergency service.",
        h1=f"Roofers in {name}", trail=[("Coverage", "/coverage/"), (name, u)],
        hero=phero(f"Need a roofer in {name}?", f"Roof leak, storm-hit roof or a new roof in {name}? One call connects you with an independent roofing company that serves your area.", [("Coverage", "/coverage/"), (name, u)], "state-" + code.lower(), RPHOTO[reg], alerts=code),
        body=body, faqs=fq, service="Roofing referral", state=name)

# ---------------------------------------------------------------- community, library, how it works, contact
add(url="/community/", title="Real Roof Problems Homeowners Call About | RingaRoofer", desc="Common roof problems, from ceiling stains and wind-blown shingles to hail and worn-out roofs, and what helps in each.",
    h1="Real roof problems", trail=[("Real Problems", "/community/")], hero=phero("Real roof problems homeowners call about", "Typical situations and what helps. These are examples to help you recognize your own, not customer reviews.", [("Real Problems", "/community/")], "community", "oldroof"),
    body=sec(story_cards()) + sec(seasons(), "soft", "Roofing through the year", "Seasonal"))
add(url="/how-it-works/", title="How RingaRoofer Works | One Call, One Local Roofer", desc="How RingaRoofer works: call, describe your roof problem and ZIP code, and we connect you with an independent roofing company serving your area.",
    h1="How it works", trail=[("How It Works", "/how-it-works/")], hero=phero("One call, one local roofer", "Here's exactly what happens when you call RingaRoofer.", [("How It Works", "/how-it-works/")], "how-it-works", "edge"),
    body=sec(steps()) + sec(straight_talk(), "soft") + sec('<div class="doc"><h2>What RingaRoofer is</h2><p>A referral service. We don\'t do roofing work, and we don\'t charge homeowners. Roofing companies in our network pay us for connecting them with homeowners who need roofing help.</p>'
        '<h2>Who you\'ll speak with</h2><p>An independent roofing company that serves your area. They discuss the job, set up a visit, and agree any work and terms directly with you.</p>'
        '<h2>Booking online</h2><p>If you\'d rather book online, you can compare roofers on Thumbtack, our partner. RingaRoofer may be paid when you use Thumbtack through our links. Thumbtack is a separate company.</p>'
        '<h2>Your choice, always</h2><p>You\'re never obliged to hire anyone. To stop calls, see our <a href="/do-not-call/">Do Not Call</a> page.</p></div>'), stype="AboutPage")
add(url="/library/", title="Roof Library: Leaks, New Roofs, Materials & Hail | RingaRoofer", desc="Plain-English roofing help: what to do when the roof leaks, signs you need a new roof, how long roofs last, repair or replace, materials and hail checklists.",
    h1="Roof Library", trail=[("Roof Library", "/library/")], hero=phero("Roof Library", "Plain-English roofing help for homeowners.", [("Roof Library", "/library/")], "library", "shingles2"),
    body=sec('<div class="pgrid">' + "".join(f'<a class="pcard" href="/library/{a["slug"]}/"><div class="pc-img">{pic(a["photo"], 640, 440)}</div><div class="pc-body"><h3>{a["h1"]}</h3><p>{a["lead"]}</p><span class="more">Read {ic("arrow",16)}</span></div></a>' for a in ARTICLES) + '</div>'))
for a in ARTICLES:
    u = f'/library/{a["slug"]}/'
    add(url=u, title=a["title"], desc=a["desc"], h1=a["h1"], trail=[("Roof Library", "/library/"), (a["h1"], u)], article=True, ogimg=img(P[a["photo"]][0], 1200, 630),
        hero=phero(a["h1"], a["lead"], [("Roof Library", "/library/"), (a["h1"], u)], "library-" + a["slug"], a["photo"]),
        body=sec(f'<div class="doc">{a["body"]}</div><aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap"))
add(url="/contact/", title="Request a Callback From a Roofer | RingaRoofer", desc="Call (855) 635-9281 or request a callback. RingaRoofer connects you with an independent roofing company serving your area.",
    h1="Request a callback", trail=[("Request a Callback", "/contact/")], form=True,
    hero=lhero("Request a callback", [("Request a Callback", "/contact/")], "The quickest way is to call. Prefer a callback? Fill in the form and a roofing company serving your area will reach out."),
    body=sec(legal.FORM, "soft"))

# ---------------------------------------------------------------- roof questions (our editorial answers)
qhub = "".join(sec(q_cards([q for q in QS if q[2] == k], more=False), "soft" if i % 2 else "", n, None, None, k) for i, (k, n) in enumerate(QCATS))
qnav = '<nav class="jump qjump" aria-label="Topics">' + "".join(f'<a href="#{k}">{n}</a>' for k, n in QCATS) + '</nav>'
add(url="/questions/", title="Roof Questions: Straight Answers for Homeowners | RingaRoofer", desc="Answers to the roofing questions homeowners search most: leaks, repair or replace, new roofs, storms and hail, materials, inspections and hiring a roofer.",
    h1="Roof Questions", trail=[("Roof Questions", "/questions/")], hero=lhero("Roof questions, straight answers", [("Roof Questions", "/questions/")], "60 answers to the questions homeowners search most. Need a roofer now? Call " + PHONE + "."),
    body=sec(qnav, "jumpsec") + qhub)
CATN = dict(QCATS)
for slug, qq, cat, ph, link, short, pts in QS:
    u = f"/questions/{slug}/"
    same = [q for q in QS if q[2] == cat and q[0] != slug][:4]
    svc_name = next((x["name"] for x in SERVICES if f'/services/{x["slug"]}/' == link), None) or next((t["name"] for t in TYPES if f'/roof-types/{t["slug"]}/' == link), None) or ("Roofers near you" if link == "/roofers-near-me/" else "Roof Library")
    body = sec(f'<div class="doc qa"><p class="qa-tag">{ic("chat",16)} Answered by RingaRoofer · {CATN[cat]}</p><p class="qa-short">{short}</p><h2>What to know</h2><ul class="ticks">' + "".join(f"<li>{p}</li>" for p in pts) + '</ul>'
               f'<div class="qa-cta"><div><b>Need a roofer for this?</b><span>One call connects you with an independent roofing company that serves your area.</span></div>{call_btn("btn btn-call", None, "question-" + slug)}</div>'
               f'<p class="small">General information for homeowners, not a substitute for a roofer looking at your roof. More on this: <a href="{link}">{svc_name}</a>.</p></div>'
               f'<aside class="doc-side"><div class="sticky">{now_box()}</div></aside>', "doc-wrap") + sec(q_cards(same, more=True), "soft", f"More about {CATN[cat].lower()}", "Roof Questions")
    add(url=u, title=f"{qq} | RingaRoofer", desc=(short[:155].rsplit(" ", 1)[0] + "…") if len(short) > 155 else short, h1=qq, trail=[("Roof Questions", "/questions/"), (qq, u)], article=True,
        faqs=[(qq, short)], ogimg=img(P[ph][0], 1200, 630),
        hero=phero(qq, short, [("Roof Questions", "/questions/"), (qq, u)], "question-" + slug, ph), body=body)

for lp in legal.PAGES:
    add(url=lp["url"], title=lp["title"] + " | RingaRoofer", desc=lp["desc"], h1=lp["h1"], trail=[(lp["h1"], lp["url"])], legal=True,
        hero=lhero(lp["h1"], [(lp["h1"], lp["url"])], "Last updated October 3, 2026"), body=sec(f'<div class="doc legal">{lp["body"]}</div>'))
def sitemap_page():
    groups = {"Main": [], "Services": [], "Roof Types": [], "Coverage": [], "Roof Library": [], "Legal": []}
    for p in PAGES:
        if p.get("noindex"): continue
        u = p["url"]; k = ("Legal" if p.get("legal") else "Services" if u.startswith("/services") else "Roof Types" if u.startswith("/roof-types") else "Coverage" if u.startswith("/coverage") else "Roof Library" if u.startswith(("/library", "/questions")) else "Main")
        groups[k].append(f'<li><a href="{u}">{p["h1"]}</a></li>')
    return sec('<div class="smap">' + "".join(f'<div><h2>{k}</h2><ul>{"".join(v)}</ul></div>' for k, v in groups.items()) + '</div>')
add(url="/sitemap/", title="Site Map | RingaRoofer", desc="All pages on RingaRoofer.com.", h1="Site map", trail=[("Site Map", "/sitemap/")], hero=lhero("Site map", [("Site Map", "/sitemap/")]), body="__SMAP__")

# ---------------------------------------------------------------- compliance (build fails on any hit)
BANNED = ["free", "estimat", "licens", "insur", "bond", "cheap", "low", "afford", "discount", "budget", "bargain", "inexpensive", "gutter", "window",
          "siding", "deal", "save", "saving", "price", "pricing", "cost", "rate", "rates", "quote", "damage", "warrant", "claim", "financ", "professional",
          "skylight", "chimney", "solar", "fascia", "soffit", "best", "certif", "guarant", "septic"]
ALLOW = {"lowell", "freeze", "freezes", "freezing", "below", "allow", "allowed", "follow", "flow", "yellow", "slow", "shallow", "rather", "separate", "moderate", "accurate",
         "corporate", "generate", "operate", "operated", "operates", "operating", "cooperate"}
LEGAL_OK = ("warrant", "rate", "insur", "claim", "cost", "save", "financ", "licens", "damage", "deal", "bond", "window", "guarant", "certif", "quote", "professional", "wildlife", "pric", "pricing", "price")
def check(html, where, legal_page=False):
    txt = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", html)
    txt = re.sub(r"<[^>]+>", " ", txt).replace("&amp;", "&").replace(DISCLAIMER, " ")
    if "24/7" in txt or "24-7" in txt: raise SystemExit(f"24/7 claim on {where}")
    words = re.findall(r"[a-z]+", txt.lower())
    hits = sorted({w for w in words for b in BANNED if w.startswith(b) and w not in ALLOW and not (legal_page and b in LEGAL_OK)})
    if "rated" in words: hits.append("rated")
    if hits: raise SystemExit(f"Banned wording on {where}: {hits}")

def main():
    for n in (os.listdir(OUT) if os.path.isdir(OUT) else []):
        if n != "assets": (shutil.rmtree if os.path.isdir(os.path.join(OUT, n)) else os.remove)(os.path.join(OUT, n))
    smap = sitemap_page()
    for p in PAGES:
        if p["body"] == "__SMAP__": p["body"] = smap
        html = page(p); check(html, p["url"], p.get("legal"))
        d = os.path.join(OUT, p["url"].strip("/")); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w").write(html)
    nf = dict(url="/404/", title="Page not found | RingaRoofer", desc="Page not found.", h1="Page not found", noindex=True,
              hero=phero("We couldn't find that page", "It may have moved. The quickest way to get roofing help is to call.", [], "404", "house"), body=sec(svc_cards(SERVICES[:3])))
    open(os.path.join(OUT, "404.html"), "w").write(page(nf).replace(f'<link rel="canonical" href="{URL}/404/">', ""))
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(
        f'<url><loc>{URL}{p["url"]}</loc><lastmod>{UPDATED}</lastmod></url>' for p in PAGES if not p.get("noindex")) + "\n</urlset>\n")
    open(os.path.join(OUT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /api/\n\nUser-agent: AhrefsBot\nDisallow: /\nUser-agent: SemrushBot\nDisallow: /\nUser-agent: MJ12bot\nDisallow: /\nUser-agent: DotBot\nDisallow: /\n\nSitemap: {URL}/sitemap.xml\n")
    open(os.path.join(OUT, "llms.txt"), "w").write(f"# {BRAND}\n\n> {BRAND} (ringaroofer.com) is a roofing referral service for U.S. homeowners. Calling {PHONE} connects a homeowner with an independent roofing company that serves their area, for roof repair, leak repair, roof inspections, storm and hail repair, emergency roofing and tarping, roof replacement, new roofs and re-roofs on shingle, metal, flat, tile, slate and cedar shake roofs. It does not do roofing work and does not charge homeowners.\n\n## Pages\n" + "\n".join(f"- [{p['h1']}]({URL}{p['url']}): {p['desc']}" for p in PAGES if not p.get("legal") and not p.get("noindex")) + "\n")
    open(os.path.join(OUT, "google6cdd134560bcda8a.html"), "w").write("google-site-verification: google6cdd134560bcda8a.html")
    open(os.path.join(OUT, "BingSiteAuth.xml"), "w").write('<?xml version="1.0"?>\n<users>\n\t<user>143504FD65C9CD8E8439BFD5BD0E4177</user>\n</users>\n')
    open(os.path.join(OUT, "_redirects"), "w").write(legal.REDIRECTS)
    open(os.path.join(OUT, "_headers"), "w").write(legal.HEADERS)
    shutil.copy(os.path.join(ROOT, "favicon.svg"), os.path.join(OUT, "favicon.svg"))
    import quote_funnel, funnel_cfg
    if not funnel_cfg.PARTNERS: print("WARNING: funnel_cfg.PARTNERS is empty: add your buyer's company name(s) before running ads to /get-matched/")
    quote_funnel.write(OUT, funnel_cfg.cfg(V, DISCLAIMER), check)
    print(f"Built {len(PAGES)} pages")

if __name__ == "__main__": main()
