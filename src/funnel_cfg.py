"""RingaRoofer 'Get matched' web-lead funnel settings. PARTNERS = companies named in the consent (from your buyer / ping tree)."""
from content import P, img, PHONE, TEL, EMAIL, URL, BRAND
PARTNERS = []   # e.g. ["Buyer Company LLC"] — exact legal names your buyer gives you. Required before running ads.
def pic(k, w=480, h=330): return img(P[k][0], w, h)
def cfg(v, disclaimer, check_unused=None):
    logo = open(__import__("os").path.join(__import__("os").path.dirname(__file__), "favicon.svg")).read() + f"<span>{BRAND}</span>"
    return dict(brand=BRAND, url=URL, phone=PHONE, tel=TEL, email=EMAIL, trade="roofing", vertical="roofing", v=v, ca="/california-privacy/",
        brand_color="#F26B1D", brand_color2="#D85A12", dark="#0B1729", logo_html=logo, disclaimer=disclaimer, partners=[BRAND] + PARTNERS,
        title="Get Matched With Local Roofers | RingaRoofer", desc="Need a new roof or a roof repair? Answer a few quick questions and get matched with local roofing companies that serve your area.",
        kicker="Roof replacement &amp; repair · Homeowners", h1="Need a new roof or a repair? <em>Get matched with local roofers.</em>",
        sub="Answer a few quick questions about your home. We'll connect you with roofing companies that serve your ZIP code.",
        bullets=["Takes about 60 seconds", "Local roofing companies near you", "No obligation to hire anyone"], submit="Get matched now",
        hero_img=img(P["roofer2"][0], 1800, 1000),
        steps=[dict(kind="zip", q="What's the ZIP code of the home?", hint="We'll look for roofing companies that serve your area."),
               dict(kind="tiles", name="project", q="What do you need?", opts=[("Roof replacement", "Replace my roof", pic("tearoff")), ("Roof repair", "Repair a leak or problem", pic("oldroof")),
                    ("Storm or hail repair", "Storm or hail repair", pic("hail")), ("New roof", "New roof (new build or addition)", pic("newroof2"))]),
               dict(kind="tiles", name="material", q="What's on your roof now?", opts=[("Asphalt shingle", "Asphalt shingles", pic("shingles2")), ("Metal", "Metal", pic("metal")),
                    ("Tile", "Tile", pic("tile")), ("Flat", "Flat roof", pic("flat")), ("Wood shake", "Wood shake", pic("shake")), ("Not sure", "Not sure", None, "🤔")]),
               dict(kind="tiles", name="homeowner", q="Do you own the home?", opts=[("yes", "Yes, I own it", None, "🏠"), ("no", "No", None, "🔑")]),
               dict(kind="tiles", name="timeframe", q="When do you want the work done?", opts=[("ASAP", "As soon as possible", None, "⚡"), ("1-3 months", "In the next 1–3 months", None, "📅"),
                    ("3-6 months", "In 3–6 months", None, "🗓️"), ("Researching", "Just researching", None, "🔎")]),
               dict(kind="tiles", name="property_type", q="What type of home is it?", opts=[("Single family", "Single-family house", None, "🏡"), ("Townhouse", "Townhouse", None, "🏘️"),
                    ("Condo", "Condo", None, "🏢"), ("Mobile home", "Mobile / manufactured", None, "🚚")]),
               dict(kind="address", q="What's the property address?"),
               dict(kind="name", q="Who should the roofers ask for?"),
               dict(kind="phone", q="Last step: where can they reach you?", hint="Local roofing companies will call or text this number about your project.")],
        how=[("Tell us about your roof", "A few taps: what you need, your roof type and how soon."), ("We find local roofers", "We match your request with roofing companies that serve your area."),
             ("Compare and choose", "Talk to the companies, compare what each one offers, and pick the one you like.")],
        gallery_h="Roofing work our network handles", gallery=[(pic("tearoff"), "Full roof replacement"), (pic("metal"), "Metal roofs"), (pic("flat"), "Flat roofs"), (pic("hail2"), "Storm and hail repairs")],
        faqs=[("Is there a charge to use RingaRoofer?", "No. RingaRoofer doesn't charge homeowners. Roofing companies in our network pay us for introductions."),
              ("Who will contact me?", "A few local roofing companies, or the partners listed on our <a href='/partners/'>Marketing Partners</a> page, may call, text or email you about your project."),
              ("Do I have to hire anyone?", "No. You're never obligated to hire a company you talk to."),
              ("Can I call instead?", f"Yes. Call <a href='tel:{TEL}'>{PHONE}</a> to talk to a roofing company now.")])
