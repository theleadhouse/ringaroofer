"""Per-state roof detail for RingaRoofer coverage pages: the main weather risks for roofs in each state,
when they hit, what homeowners can check from the ground, and state-specific questions.
Wording follows the site's banned list (no 'damage', 'cost', 'low…', 'rated', 'window', 'gutter', 'chimney', 'skylight')."""

# risk code: (title, what it does to roofs, when, what to check, (question, answer))
RISK = {
 "H": ("Hail", "Hail can bruise asphalt shingles, knock off the protective granules and dent vents and metal trim, often without a leak showing for weeks.",
       "spring and early summer storm season",
       "After a hailstorm, look from the ground for dented vents and metal trim, and for loose granules collecting where water runs off the roof.",
       ("Does hail hurt roofs in {name}?", "It can. Hail is one of the main roof risks in {name}. Bruised shingles are hard to spot from the ground, so after a big storm many homeowners have a roofer look up close before small problems turn into leaks.")),
 "W": ("High wind and tornadoes", "Severe thunderstorms and tornado-season winds lift and tear shingles, most often along edges, ridges and corners.",
       "spring storm season",
       "After high wind, walk around the house and look for missing or lifted shingles, bare patches and shingle pieces in the yard.",
       ("What wind blows shingles off a roof?", "Older or poorly sealed shingles can lift in gusts around 50 to 60 mph, while newer wind-resistant shingles hold on in much stronger gusts. Shingle pieces in the yard after a storm are the sign to get the roof checked.")),
 "U": ("Hurricanes and tropical storms", "Hurricanes and tropical storms bring hours of wind and sideways rain that get under shingles, flashing and ridge caps.",
       "hurricane season, June through November",
       "Before hurricane season, trim branches that hang over the roof and know who you'd call for an emergency tarp.",
       ("How do I get my roof ready for hurricane season in {name}?", "Trim overhanging branches, fix loose or missing shingles early, and keep a roofer's number handy for an emergency tarp. After a storm passes, check top-floor ceilings for new stains.")),
 "S": ("Heavy snow and ice dams", "Heavy snow adds weight, and ice dams at the eaves push melt water back up under the shingles.",
       "winter",
       "In winter, watch for thick icicles and ridges of ice along the roof edge, and for new stains on top-floor ceilings and walls.",
       ("Why does my roof leak when the snow melts?", "Usually an ice dam: heat from the house melts snow higher up, the water refreezes at the cold roof edge, and the trapped water backs up under the shingles. Attic insulation and ventilation, plus an ice barrier at the eaves, are the long-term fixes a roofer will look at.")),
 "T": ("Freeze and thaw", "Repeated freezing and thawing opens small gaps around flashing, vents and pipes, and turns small leaks into bigger ones.",
       "late fall through early spring",
       "In fall, have the flashing and seals around vents and pipes checked before the first hard freeze.",
       ("Can a roof be fixed in winter in {name}?", "Often, yes. Small repairs and emergency tarping happen year-round on dry days, while full replacements are easier to schedule in milder months.")),
 "X": ("Strong sun and heat", "Strong sun and summer heat dry out asphalt shingles and sealants faster, so roofs age sooner than in milder climates.",
       "summer",
       "Look for curling, cracking or faded shingles on the sunniest slopes, usually the south and west sides.",
       ("How long does a roof last in {name}'s heat?", "Heat and strong sun can take several years off an asphalt shingle roof compared with milder climates. Tile and metal roofs handle sun and heat well, which is why they're common in hot areas.")),
 "F": ("Wildfire embers", "During wildfires, wind-blown embers land on roofs and collect in roof valleys and dry debris.",
       "late summer and fall fire season",
       "During fire season, keep the roof and its valleys clear of leaves and pine needles.",
       ("Which roofs hold up better in wildfire areas?", "Fire-resistant roof coverings such as metal, tile and many asphalt shingles hold up far better than untreated wood shakes. Many wildfire-area towns have their own roofing requirements, so a local roofer will know what applies to your home.")),
 "R": ("Long rainy stretches and moss", "Long wet seasons and humidity feed moss and algae and find any weak spot in flashing or worn shingles.",
       "the rainy season",
       "Watch for moss growing on shady slopes, and check the attic for damp spots after long rains.",
       ("Is moss bad for a roof?", "Over time, yes. Moss holds water against the shingles and can lift their edges. A roofer can remove it gently and suggest ways to keep it from coming back.")),
 "N": ("Nor'easters and coastal storms", "Nor'easters and coastal storms drive rain sideways under shingles and flashing for hours at a time.",
       "fall through early spring",
       "After a coastal storm, check top-floor ceilings and walls for new stains and the attic for wet insulation.",
       ("Why does my roof only leak in big storms?", "Wind-driven rain can get in where normal rain doesn't: under lifted shingle edges, worn flashing or ridge caps. A roofer can find the entry point even when the roof looks fine from the ground.")),
 "M": ("Monsoon storms", "Monsoon storms bring sudden wind, heavy rain and sometimes hail after months of dry heat.",
       "July through September",
       "Before monsoon season, check that flat-roof drains are clear and look for cracked tiles or split seams.",
       ("Do flat roofs leak in monsoon season?", "They can, mostly where water pools or drains are blocked. Keeping drains clear and fixing sagging spots and split seams before July helps flat roofs get through the season.")),
}

FLAGS = {
 "AL": "HWUR", "AK": "STW", "AZ": "XMF", "AR": "HWR", "CA": "FXR", "CO": "HSXW", "CT": "STN", "DE": "NU", "FL": "URX", "GA": "WHRU",
 "HI": "RUX", "ID": "SXF", "IL": "HWS", "IN": "HWS", "IA": "HWS", "KS": "HWX", "KY": "HWT", "LA": "URX", "ME": "STN", "MD": "NUWT",
 "MA": "STN", "MI": "SWT", "MN": "HST", "MS": "WUR", "MO": "HWT", "MT": "HSW", "NE": "HW", "NV": "XSW", "NH": "STN", "NJ": "NUW",
 "NM": "XMH", "NY": "STN", "NC": "URW", "ND": "HS", "OH": "WST", "OK": "HWX", "OR": "RW", "PA": "STW", "RI": "NU", "SC": "URW",
 "SD": "HSW", "TN": "WHR", "TX": "HUWX", "UT": "SXW", "VT": "ST", "VA": "NUS", "WA": "RSF", "WV": "STW", "WI": "HWS", "WY": "HSW", "DC": "NWT",
}

def detail(code, name, cities):
    fl = [RISK[f] for f in FLAGS.get(code, "")]
    if not fl: return "", []
    risks = "".join(f"<li><b>{t}:</b> {w}</li>" for t, w, _, _, _ in fl)
    seasons = "".join(f"<li><b>{t}:</b> {s}</li>" for t, _, s, _, _ in fl)
    checks = "".join(f"<li>{c}</li>" for _, _, _, c, _ in fl)
    html = (f'<h2 id="risks">Main roof risks in {name}</h2><ul class="ticks">{risks}</ul>'
            f'<h2>When roofs in {name} take the most wear</h2><ul class="ticks">{seasons}</ul>'
            f'<h2 id="check-ground">What {name} homeowners can check from the ground</h2><ul class="ticks">{checks}'
            f'<li>Never climb onto a wet, icy or steep roof. A roofer can check it safely.</li></ul>'
            f'<p>Calls come in from across {name}, from {cities[0]} and {cities[1]} to smaller towns. Call and we\'ll check which roofing companies serve your ZIP code.</p>')
    faqs = [(q.format(name=name), a.format(name=name)) for _, _, _, _, (q, a) in fl]
    return html, faqs
