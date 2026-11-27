"""Paid-search landing pages: /call/<slug>/  (noindex, not in the sitemap or menus). Shared by all call sites; per-site text lives in lp_cfg.py.
One job per page: get the caller on the phone (and, where the site sells web leads, take the request in the same first view).
No navigation. One message per ad group. Call button in every screen."""
import os
from html import escape as esc
import lp_cfg as C

CSS = """
.cl-hdr{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:40}.cl-hdr .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;height:72px}
.cl-hdr .btn{white-space:nowrap}
.cl-hero{position:relative;color:#fff;background:#0E1C30;overflow:hidden}.cl-bg,.cl-bg img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cl-hero:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,22,38,.95),rgba(10,22,38,.82) 50%,rgba(10,22,38,.45))}
.cl-in{position:relative;z-index:1;padding:64px 0 70px;max-width:720px}
.cl-grid{position:relative;z-index:1;display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center;padding-top:52px;padding-bottom:60px}.cl-grid .cl-in{padding:0}
.cl-hero .kick{color:#F5B43A}
.cl-hero h1{color:#fff;font-size:clamp(36px,4.8vw,58px);line-height:1.04;letter-spacing:-.025em;margin:10px 0 16px}.cl-hero h1 em{display:block;font-style:normal;color:#F5B43A}
.cl-sub{font-size:19px;line-height:1.5;color:#DCE6F2;margin:0 0 24px}
.cl-bul{list-style:none;padding:0;margin:0 0 26px;display:flex;flex-wrap:wrap;gap:10px 24px}.cl-bul li{display:flex;gap:8px;align-items:center;font-weight:600}.cl-bul .ic{color:#F5B43A}
.cl-call{font-size:22px!important;padding:18px 28px!important}.cl-note{color:#B7C5D6;font-size:14px;margin:12px 0 0}
.cl-form{color:var(--ink,#13253F)}
.cl-chips{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.cl-chip{display:flex;align-items:center;gap:10px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px;font-weight:600;color:var(--navy);text-decoration:none}
.cl-chip:hover{border-color:var(--navy)}.cl-chip .ic{color:#F06A2C}
.cl-3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.cl-3>div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px}.cl-3 b{display:block;font-size:17px;margin:10px 0 4px}.cl-3 p{margin:0;color:#4a5b70}
.cl-n{width:36px;height:36px;border-radius:50%;background:#F06A2C;color:#fff;display:grid;place-items:center;font-weight:800}
.cl-two{display:grid;grid-template-columns:1.2fr .8fr;gap:20px;align-items:start}.cl-box{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px 24px}
.cl-box ol{margin:8px 0 0;padding-left:20px}.cl-box li{margin:6px 0}.cl-warn{background:#FFF6F0;border-color:#F6C9AC}
.cl-end{background:#0E1C30;color:#fff;text-align:center;padding:56px 0}.cl-end h2{color:#fff;margin:0 0 8px}.cl-end p{color:#B7C5D6}
.cl-ftr{background:#0A1524;color:#8EA0B6;font-size:12.5px;padding:28px 0 100px}.cl-ftr a{color:#C9D5E3;margin-right:14px}.cl-ftr p{margin:10px 0 0;line-height:1.6}
@media(max-width:430px){.cl-hdr .wm>span{font-size:15.5px}.cl-hdr .logo-mark,.cl-hdr svg.logo-mark{width:32px;height:32px}.cl-hdr .btn{padding:9px 10px;font-size:13.5px;gap:5px}.cl-hdr .wrap{gap:8px}}
@media(max-width:900px){.cl-grid{grid-template-columns:1fr;gap:26px;padding-top:30px;padding-bottom:36px}}
@media(max-width:760px){.cl-hdr .wrap{height:62px}.cl-hdr .btn{padding:10px 12px;font-size:14.5px}.cl-hdr .wm small{display:none}.cl-in{padding:34px 0 40px}.cl-sub{font-size:17px}
 .cl-bul{flex-direction:column;gap:8px}.cl-call{width:100%;justify-content:center}.cl-chips{grid-template-columns:1fr 1fr}.cl-chip{padding:13px;font-size:14.5px}
 .cl-3,.cl-two{grid-template-columns:1fr}.cl-hero:after{background:linear-gradient(180deg,rgba(10,22,38,.8),rgba(10,22,38,.93))}}
"""

def write(OUT, g, form=None):
    """form: optional (head_html, card_html, end_html) to put the site's lead form in the first view."""
    ic, pic, call_btn, faq_html, BRANDH, PHONE, TEL, DISCLAIMER, V, check = (g[k] for k in ("ic", "pic", "call_btn", "faq_html", "BRANDH", "PHONE", "TEL", "DISCLAIMER", "V", "check"))
    open(os.path.join(OUT, "assets", "lp.css"), "w").write(CSS)
    legal = "".join(f'<a href="{u}">{t}</a>' for t, u in C.LEGAL)
    for p in C.PAGES:
        place = "lp-" + p["slug"]
        chips = "".join(f'<a class="cl-chip" href="tel:{TEL}" data-call="{place}-chip">{ic("phone",18)}{esc(c)}</a>' for c in p["chips"])
        steps = "".join(f'<div><span class="cl-n">{i+1}</span><b>{a.replace("{PHONE}", PHONE)}</b><p>{b}</p></div>' for i, (a, b) in enumerate(C.STEPS))
        bul = "".join(f'<li>{ic("check",18)} {b}</li>' for b in p.get("bullets", C.BULLETS))
        txt = (f'<div class="cl-in"><p class="kick">{p["kick"]}</p><h1>{p["h1a"]} <em>{p["h1b"]}</em></h1><p class="cl-sub">{p["sub"]}</p><ul class="cl-bul">{bul}</ul>'
               f'{call_btn("btn btn-call xl cl-call", "Call " + PHONE, place + "-hero")}<p class="cl-note">{C.CALL_NOTE}</p></div>')
        inner = f'<div class="wrap cl-grid">{txt}<div class="cl-form">{form[1]}</div></div>' if form else f'<div class="wrap">{txt}</div>'
        safety = f'<div class="cl-box cl-warn"><h3>{C.SAFETY[0]}</h3><p>{C.SAFETY[1]}</p></div>' if C.SAFETY else ""
        body = f'''<header class="cl-hdr"><div class="wrap"><span class="brand">{BRANDH}</span>{call_btn("btn btn-call", PHONE, place + "-header")}</div></header>
<main id="main">
<section class="cl-hero"><div class="cl-bg">{pic(p["photo"], 1800, 1000, eager=True)}</div>{inner}</section>
<section class="sec soft"><div class="wrap"><h2>Sounds like yours? Call and describe it.</h2><p class="lead">Pros hear these every day. Tap one to call.</p><div class="cl-chips">{chips}</div></div></section>
<section class="sec"><div class="wrap"><h2>What happens when you call</h2><div class="cl-3">{steps}</div></div></section>
<section class="sec soft"><div class="wrap cl-two"><div class="cl-box"><h3>Quick checks before you call</h3><ol>{"".join(f"<li>{c}</li>" for c in p["checks"])}</ol><p style="margin:12px 0 0">Still not right? Call {PHONE}.</p></div>{safety}</div></section>
<section class="sec"><div class="wrap" style="max-width:860px"><h2>Questions</h2>{faq_html(C.COMMON_FAQ)}</div></section>
<section class="cl-end"><div class="wrap"><h2>{C.END[0]}</h2><p>{C.END[1]}</p><div class="btns" style="justify-content:center">{call_btn("btn btn-call xl cl-call", "Call " + PHONE, place + "-footer")}</div></div></section>
</main>
<footer class="cl-ftr"><div class="wrap"><nav>{legal}</nav><p>{DISCLAIMER}</p></div></footer>
<div class="callbar">{call_btn("callbar-btn", "Call Now · " + PHONE, place + "-sticky")}</div>'''
        html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(p["title"])}</title>'
                f'<meta name="description" content="{esc(p["sub"])}"><meta name="robots" content="noindex,follow"><meta name="theme-color" content="#0E1C30">'
                f'<link rel="icon" href="/favicon.svg"><link rel="preconnect" href="https://images.pexels.com"><link rel="stylesheet" href="/assets/site.css?v={V}"><link rel="stylesheet" href="/assets/lp.css?v={V}">'
                + (form[0] if form else "") + f'<script src="/assets/config.js?v={V}"></script></head><body class="clp">{body}'
                + f'<script src="/assets/site.js?v={V}" defer></script>' + (form[2] if form else "") + "</body></html>")
        check(html, "/call/" + p["slug"] + "/")
        d = os.path.join(OUT, "call", p["slug"]); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w").write(html)
    return [p["slug"] for p in C.PAGES]
