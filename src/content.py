"""RingaRoofer v2 content: RingaRoofer's approved roofing copy (rr_content.py) + real photos, matcher, scenes, stories and a Thumbtack backup link.
Buyer wording rules (build.py blocks the build): never free, estimate(s), licensed, insured, bonded, cheap/low rates, affordable, discount, price/cost,
deal, save, quote, damage, claim, warranty, financing, professional, and never gutters, windows, siding, skylights, chimneys, solar, fascia, soffit
or any service outside roofing."""
from rr_content import *

BRAND = "RingaRoofer"
SOCIAL = []
# Thumbtack partner near-me link (category checked live: thumbtack.com/k/roofing-contractors/near-me/). utm_source=cma-leadhouse is our CMA tag.
TT_BASE = "https://www.thumbtack.com/k/roofing-contractors/near-me/?utm_medium=partnership&utm_source=cma-leadhouse&utm_campaign=ringaroofer-"
def tt(campaign): return TT_BASE + (campaign or "site")

def img(src, w=1200, h=None):
    kind, pid = src
    if kind == "px":
        return f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&fit=crop&w={w}{f'&h={h}' if h else ''}"
    return f"https://images.unsplash.com/{pid}?auto=format&fit=crop&w={w}{f'&h={h}' if h else ''}&q=78"

# Real photographs (Pexels / Unsplash licenses), each checked on its photo page (camera photo, not AI) and checked that the image file loads.
P = {
 "roofer":    (("px", 33404248), "Roofer using a nail gun to install shingles on a home", "Ryan Stephens / Pexels"),
 "roofer2":   (("px", 38028508), "Roofers installing asphalt shingles on a Texas home", "Ryan Stephens / Pexels"),
 "shingles":  (("px", 37677394), "Roofer installing asphalt shingles on a house", "Ryan Stephens / Pexels"),
 "shingles2": (("px", 38629153), "Close-up of black textured asphalt shingles", "Ann H / Pexels"),
 "metal":     (("px", 11767927), "Modern house with a metal roof", "Matilda Iglesias / Pexels"),
 "tile":      (("px", 39494031), "New home with a tile roof in California", "D Goug / Pexels"),
 "flat":      (("px", 39238311), "Roofers installing membrane on a flat roof", "Bulat843 / Pexels"),
 "flat2":     (("px", 38510748), "Roofer working on a flat roof in the sun", "Bulat843 / Pexels"),
 "shake":     (("px", 28954789), "Historic building with a wood shingle roof and dormers", "Alex Moliski / Pexels"),
 "storm":     (("px", 12515221), "Lightning striking over suburban houses", "Lance Stephenson / Pexels"),
 "storm2":    (("px", 39264566), "Storm clouds at twilight over suburban houses", "Andreas Ebner / Pexels"),
 "hail":      (("px", 8804585),  "Hailstones melting on green grass", "Dmitry Zuev / Pexels"),
 "hail2":     (("px", 34429004), "Hailstones scattered on a wet deck after a storm", "Kristina Kutleša / Pexels"),
 "newroof":   (("px", 5071130),  "Two-story suburban home with a gable roof", "Curtis Adams / Pexels"),
 "newroof2":  (("px", 39151678), "Crew roofing a newly built home", "D Goug / Pexels"),
 "aerial":    (("px", 5587963),  "Aerial view of a suburban neighborhood's rooftops", "Michael Gault / Pexels"),
 "aerial2":   (("px", 11467685), "Drone view of suburban rooftops in California", "Kelly / Pexels"),
 "inspect":   (("px", 38346725), "Roofer in a safety harness climbing a ladder to the roof", "Daniel & Hannah Snipes / Pexels"),
 "tearoff":   (("us", "photo-1633759593085-1eaeb724fc88"), "Roofer removing old shingles from a house roof", "Zohair Mirza / Unsplash"),
 "oldroof":   (("px", 6931459),  "Old roof with missing shingles and exposed boards", "Mathias Reding / Pexels"),
 "edge":      (("px", 38524253), "Roofer working at the roof edge of a house", "Bulat843 / Pexels"),
 "ceiling":   (("px", 30499666), "Room with a collapsed ceiling after a leak", "Halil İbrahim Çetin / Pexels"),
 "house":     (("px", 4832530),  "Two-story suburban house under a blue sky", "Curtis Adams / Pexels"),
}

PHOTO = {"roof-repair": "roofer", "roof-leak-repair": "ceiling", "emergency-roof-repair": "oldroof", "roof-tarping": "edge", "storm-roof-repair": "storm",
         "hail-roof-repair": "hail", "roof-replacement": "tearoff", "new-roof": "newroof2", "roof-inspection": "inspect",
         "asphalt-shingle": "shingles", "metal": "metal", "flat": "flat", "tile": "tile", "slate": "shingles2", "cedar-shake": "shake"}

# New high-search service: roof inspections (people search "roof inspection near me" before most repairs and re-roofs)
SERVICES.insert(1, dict(slug="roof-inspection", name="Roof Inspection", icon="shield", short="A roofer checks shingles, flashing, vents and the attic.",
  title="Roof Inspection Near You | Call a Local Roofer | RingaRoofer",
  desc="Roof inspection after a storm, before buying or selling, or when the roof is getting older. Call (855) 635-9281 to connect with a local roofer.",
  h1="Roof inspection from a local roofer",
  lead="After a storm, before a sale, or because the roof is getting older. Call and we'll connect you with a roofer who can look the roof over and tell you where it stands.",
  sections=[
   ("What a roof inspection covers", "<ul class='ticks'><li><b>Shingles or roofing:</b> missing, lifted, cracked or worn pieces.</li><li><b>Flashing</b> at walls, valleys and vents.</li><li><b>Vent boots and pipe collars.</b></li><li><b>Ridge caps</b> and edges.</li><li><b>Attic:</b> stains, daylight, ventilation and wet insulation.</li><li><b>Decking:</b> soft or sagging spots.</li></ul>"),
   ("When to get one", "<ul class='ticks'><li>After hail, high wind or a hurricane.</li><li>When the roof is 15 years old or more.</li><li>Before buying or selling a home.</li><li>When you see a new ceiling stain.</li></ul>"),
   ("What you get", "<p>Ask the roofer for photos of anything they find and a plain explanation of what needs attention now and what can wait. You decide what to do next.</p>")],
  faqs=[("How long does a roof inspection take?", "Usually under an hour for a typical home, a little longer if the roofer also checks the attic."),
        ("Do you do the inspection yourselves?", "No. RingaRoofer is a referral service. The roofing company you speak with does the inspection and agrees the details with you directly.")],
  group="Roof Repair"))
for s in SERVICES: s["photo"] = PHOTO.get(s["slug"], "roofer")
for t in TYPES: t["photo"] = PHOTO.get(t["slug"], "shingles")

ARTICLES += [
 dict(slug="how-long-does-a-roof-last", title="How Long Does a Roof Last? By Roofing Type | RingaRoofer",
  h1="How long does a roof last?", desc="Typical lifespans for asphalt shingle, metal, tile, slate, cedar shake and flat roofs, and what shortens or stretches them.",
  lead="Typical lifespans by material, and what makes the difference.", photo="aerial",
  body="<div class='tbl'><table><thead><tr><th>Roof</th><th>Typical life</th></tr></thead><tbody><tr><td>Asphalt shingle</td><td>20–30 years</td></tr><tr><td>Metal</td><td>40+ years</td></tr><tr><td>Clay or concrete tile</td><td>50+ years (underlayment sooner)</td></tr><tr><td>Slate</td><td>75+ years</td></tr><tr><td>Cedar shake</td><td>20–40 years</td></tr><tr><td>Flat (TPO, EPDM)</td><td>15–30 years</td></tr></tbody></table></div><h2>What shortens a roof's life</h2><ul class='ticks'><li>Hail and high wind.</li><li>Poor attic ventilation.</li><li>Intense sun and heat.</li><li>Small leaks left too long.</li></ul><h2>What helps</h2><ul class='ticks'><li>An inspection after big storms.</li><li>Fixing small problems early.</li><li>Keeping branches off the roof.</li></ul>"),
 dict(slug="roof-repair-or-replace", title="Repair or Replace Your Roof? How to Decide | RingaRoofer",
  h1="Repair or replace your roof?", desc="Age, how widespread the problem is, and repeat leaks: how to decide between a roof repair and a new roof.",
  lead="Three questions that usually settle it.", photo="tearoff",
  body="<ol class='big'><li><b>How old is the roof?</b> Shingles past about 20 years with widespread wear usually point to replacement.</li><li><b>Is the problem in one spot or everywhere?</b> One leak or a few missing shingles is a repair. Curling and bald patches across slopes is a re-roof.</li><li><b>Does it keep coming back?</b> Repeat leaks in different places often mean the roof is at the end of its life.</li></ol><p>A roofer who looks at the roof in person can show you photos and explain both options.</p>"),
]
for a, ph in zip(ARTICLES, ["ceiling", "oldroof", "shingles2", "hail2"]): a.setdefault("photo", ph)

# matcher chips: (key, label, photo, url, route, message)
PROJECTS = [
 ("leak", "Roof leaking", "ceiling", "/services/roof-leak-repair/", "call", "Leaks get worse the longer they run. Call and we'll connect you with a roofer near you."),
 ("storm", "Storm or wind hit", "storm", "/services/storm-roof-repair/", "call", "Lifted or missing shingles let water in with the next rain. Call to get the roof checked."),
 ("hail", "Hail on the roof", "hail", "/services/hail-roof-repair/", "call", "Hail marks are hard to see from the ground. Call and a roofer can check the roof up close."),
 ("emergency", "Roof opened up", "oldroof", "/services/emergency-roof-repair/", "call", "Water coming in now? Call and we'll connect you with a roofer taking emergency calls."),
 ("new", "New roof / re-roof", "tearoff", "/services/roof-replacement/", "call", "Worn, curling or leaking in several places? Call to talk through a new roof."),
 ("inspect", "Roof inspection", "inspect", "/services/roof-inspection/", "call", "After a storm or before a sale, a roofer can look it over and tell you where it stands."),
]
PROBLEMS = [
 ("Water stain on the ceiling", "ceiling", "/services/roof-leak-repair/"),
 ("Shingles blown off", "oldroof", "/services/storm-roof-repair/"),
 ("Hail last night", "hail2", "/services/hail-roof-repair/"),
 ("Roof looks worn out", "tearoff", "/services/roof-replacement/"),
 ("Flat roof ponding", "flat2", "/roof-types/flat/"),
 ("Storm on the way", "storm2", "/services/roof-tarping/"),
]
STORIES = [
 ("Ceiling stain after a week of rain", "ceiling", "A brown ring appeared on the bedroom ceiling and grew after every storm.", "Catch the water, photograph it, and call. The leak often starts a few feet from the stain.", "/services/roof-leak-repair/"),
 ("Shingles in the yard after high wind", "oldroof", "After a windy night, shingles were scattered across the lawn and the felt was showing.", "Don't climb up. A roofer can tarp it the same day or next, then plan the repair.", "/services/storm-roof-repair/"),
 ("Hail the size of quarters", "hail", "A short, loud hailstorm. Nothing looked wrong from the ground.", "Write down the date and call for an inspection; hail marks are only visible up close.", "/services/hail-roof-repair/"),
 ("Twenty-five-year-old roof, leaking in two places", "tearoff", "Two new leaks in one season and curling shingles on the south side.", "Time to compare a repair with a full re-roof. A roofer can show you photos of both slopes.", "/services/roof-replacement/"),
 ("Selling the house next spring", "inspect", "The buyer's inspector will look at the roof, so the owners wanted to know first.", "A roof inspection now gives you time to fix small things.", "/services/roof-inspection/"),
 ("Flat roof over the porch keeps pooling", "flat", "Water sat on the porch roof for days after each rain.", "Ponding wears membranes fast. A flat-roof specialist can fix the slope or drain.", "/roof-types/flat/"),
]
SEASONS = [
 ("Fall (now)", "The last good weeks for repairs and re-roofs before winter. Fix small leaks and lifted shingles before snow and ice arrive."),
 ("Winter", "Ice dams, heavy snow and winter storms in the North; emergency leak repairs and tarping year-round."),
 ("Spring", "Hail and severe storm season across the middle of the country. Inspections and storm repairs peak."),
 ("Summer", "Hurricane season on the coasts, heat and sun, and the busiest months for new roofs."),
]
NEIGHBORHOODS = ["Dallas","Houston","San Antonio","Austin","Oklahoma City","Denver","Omaha","Wichita","Kansas City","Atlanta","Tampa","Orlando","Miami","Charlotte","Nashville","Chicago","Minneapolis","St. Louis","Indianapolis","Columbus","Phoenix","Las Vegas","New Orleans","Birmingham","Raleigh","Philadelphia"]
