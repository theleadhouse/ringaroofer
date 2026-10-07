"""RingaRoofer smart quote form (/get-a-quote/). PARTNERS = companies named in the consent (from your buyer / ping tree)."""
import os
from content import P, img, PHONE, TEL, EMAIL, URL, BRAND
PARTNERS = []   # e.g. ["Buyer Company LLC"] — exact legal names your buyer gives you. Required before running ads.
def pic(k, w=420, h=290): return img(P[k][0], w, h)
def cfg(v, disclaimer):
    logo = open(os.path.join(os.path.dirname(__file__), "favicon.svg")).read() + f"<span>{BRAND}</span>"
    return dict(brand=BRAND, url=URL, phone=PHONE, tel=TEL, email=EMAIL, trade="roofing", vertical="roofing", v=v, ca="/california-privacy/",
        brand_color="#F26B1D", brand_color2="#D85A12", dark="#0B1729", logo_html=logo, disclaimer=disclaimer, partners=[BRAND] + PARTNERS,
        title="Roofing Quotes From Local Roofers | RingaRoofer", desc="Get roofing quotes from local roofers in about 30 seconds. Roof replacement, repairs and storm or hail repairs for homeowners.",
        kicker="Roof replacement &amp; repair · For homeowners", h1="Get roofing quotes from <em>local roofers</em> in 30 seconds",
        sub="Tap your roof type, add your ZIP, and we'll connect you with roofing companies that serve your area.",
        bullets=["3 quick taps, no long forms", "Local roofing companies near you", "No obligation to hire anyone"], submit="Get my quote", embed_kicker="Rather not call?", embed_h2="Get roofing quotes online in 30 seconds", embed_sub="Tap your roof type and add your ZIP. Local roofing companies that serve your area will reach out.", band_text="Rather not call? Get matched with local roofers online.", again="Get my roofing quote",
        hero_img=img(P["roofer2"][0], 1800, 1000),
        step1=dict(name="material", q="What type of roof do you need help with?", opts=[
            ("Asphalt shingle", "Asphalt shingles", pic("shingles2"), ""), ("Metal", "Metal roof", pic("metal"), ""), ("Tile", "Tile roof", pic("tile"), ""),
            ("Flat", "Flat roof", pic("flat"), ""), ("Wood shake", "Wood shake", pic("shake"), ""), ("Not sure", "Not sure", pic("aerial"), "")]),
        step2_q="Great! A few quick details",
        step2_chips=[dict(name="project", q="What do you need?", opts=[("Roof replacement", "Replace my roof"), ("Roof repair", "Repair a leak"), ("Storm or hail repair", "Storm or hail repair"), ("New roof", "New roof")])],
        step3_q="Last step: where should local roofers reach you?",
        labels={"material": "Roof type", "project": "Project"},
        how=[("Tap your roof", "Pick your roof type, add your ZIP and what you need."), ("We find local roofers", "We match your request with roofing companies that serve your area."),
             ("Compare and choose", "Talk to the companies, compare what each one offers, and pick the one you like.")],
        gallery_h="Roofing work our network handles", gallery=[(pic("tearoff"), "Full roof replacement"), (pic("metal"), "Metal roofs"), (pic("flat"), "Flat roofs"), (pic("hail2"), "Storm and hail repairs")],
        faqs=[("Is there a charge to use RingaRoofer?", "No. RingaRoofer doesn't charge homeowners. Roofing companies in our network pay us for introductions."),
              ("Who will contact me?", "A few local roofing companies, or the partners listed on our <a href='/partners/'>Marketing Partners</a> page, may call, text or email you about your project."),
              ("Do I have to hire anyone?", "No. You're never obligated to hire a company you talk to."),
              ("Can I call instead?", f"Yes. Call <a href='tel:{TEL}'>{PHONE}</a> to talk to a roofing company now.")])
