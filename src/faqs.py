"""Extra roofing FAQs written the way people search Google and Bing. Buyer wording rules apply (build blocks banned words:
no price/cost, free, estimate, insurance, claim, damage, warranty, financing, professional, gutters, windows, siding, skylights, chimneys, solar)."""
from rr_content import PHONE
EXTRA = {
 "roof-repair": [
  ("How do I know if my roof needs repair?", "Missing or lifted shingles, a new ceiling stain, granules collecting at downspouts, daylight in the attic or a soft spot underfoot are all signs to call a roofer."),
  ("Can a roof be repaired instead of replaced?", "Often, yes. If the problem is in one area and the rest of the roof is sound, a repair is usually the sensible first step."),
  ("How long does a roof repair take?", "Most repairs take a few hours to a day once the roofer is on site, depending on the size of the area and the weather."),
  ("Can roofers repair a roof in the rain?", "Roofers avoid repairs on wet roofs for safety, but they can tarp a leaking roof in bad weather and come back to repair it when it's dry."),
 ],
 "roof-inspection": [
  ("Should I get my roof inspected after a storm?", "Yes, after hail or strong wind. Many problems, like bruised or lifted shingles, can't be seen from the ground."),
  ("How often should a roof be inspected?", "Once a year is a good habit, plus after major storms. Older roofs benefit from more frequent checks."),
  ("What does a roofer look for during an inspection?", "Shingles, flashing, vent boots, ridge caps, signs of leaks in the attic, ventilation and the condition of the decking."),
 ],
 "roof-leak-repair": [
  ("What should I do first when my roof is leaking?", "Catch the water, move belongings, keep out of rooms with a bulging ceiling, take photos, and call a roofer. Don't go up on the roof."),
  ("How do roofers find where a leak is coming from?", "They trace the water from the stain back through the attic to where it enters, usually at flashing, a vent boot or missing shingles."),
  ("Can a leaking roof cause mold?", "Yes. Wet insulation and wood can grow mold within a couple of days, which is why fixing leaks quickly matters."),
  ("Why is my roof leaking only in heavy rain?", "Wind-driven rain gets into spots normal rain doesn't, like lifted shingle edges and flashing joints."),
 ],
 "emergency-roof-repair": [
  ("Who do I call for an emergency roof leak?", f"Call a roofer that takes emergency calls. Call {PHONE} and we'll connect you with one serving your area."),
  ("What counts as a roofing emergency?", "Water coming into the living space, part of the roof open to the sky, a sagging ceiling, or a tree limb through the roof."),
  ("Is it safe to stay in the house with a roof leak?", "Usually, as long as you stay out of rooms with sagging ceilings and keep water away from outlets. If in doubt, leave the room and call."),
 ],
 "roof-tarping": [
  ("How long can a tarp stay on a roof?", "A tarp is a short-term fix, usually meant to last a few weeks until the permanent repair."),
  ("Should I tarp my own roof?", "It's safer to let a roofer do it. Wet, storm-hit roofs are slippery, and a tarp must be anchored properly to hold in wind."),
 ],
 "storm-roof-repair": [
  ("How do I know if wind hurt my roof?", "Look from the ground for missing shingles, shingles on the lawn, bent flashing or lifted edges, and check the attic for new light or stains."),
  ("What wind speed can tear off shingles?", "Gusts around 50 to 60 mph can lift older or poorly sealed shingles; newer wind-resistant shingles hold up better."),
  ("How do I avoid storm chasers?", "Take your time, ask for a local address and references, get the scope of work in writing, and don't sign anything on the doorstep."),
 ],
 "hail-roof-repair": [
  ("What size hail hurts a roof?", "Hail about one inch across and larger can bruise asphalt shingles. Bigger stones can crack tile and dent metal."),
  ("How long after a hailstorm should I get my roof checked?", "As soon as you can. Bruised shingles may not leak right away but can fail months later."),
  ("What do hail marks on shingles look like?", "Dark spots where granules were knocked off, soft or bruised areas, and cracks. Dented vents and flashing are another clue."),
 ],
 "roof-replacement": [
  ("How do I know if I need a new roof?", "Curling or cracked shingles across the roof, bald spots, repeat leaks in different places, sagging, or a roof past about 20 to 25 years."),
  ("When is a good time of year to replace a roof?", "Late spring through fall is ideal in most places, but roofers replace roofs year-round when the weather allows."),
  ("Do I need to be home during a roof replacement?", "Not necessarily, but expect noise and a busy driveway. Move cars and fragile items away from the house."),
 ],
 "new-roof": [
  ("Which roofing material lasts longest?", "Slate and tile can last 50 years or more, metal 40 or more, and asphalt shingles 20 to 30. See our roof types pages."),
  ("Can I switch from shingles to metal?", "Yes. Many homeowners re-roof in metal. A roofer will check the structure and talk through the options."),
 ],
}
TYPES_EXTRA = {
 "asphalt-shingle": [("How long do asphalt shingles last?", "Commonly 20 to 30 years. Architectural shingles usually outlast three-tab shingles.")],
 "metal": [("Is a metal roof noisy in the rain?", "Not usually. Over solid decking and underlayment, a metal roof sounds much like any other roof.")],
 "flat": [("Why does water pool on my flat roof?", "Clogged drains, sagging decking or a poor slope. Water standing for more than a couple of days wears the membrane faster.")],
 "tile": [("Can you walk on a tile roof?", "Tiles can crack underfoot, so leave it to a roofer who knows where to step.")],
 "slate": [("Can a slate roof be repaired?", "Yes. Slate roofs are usually repaired one slate at a time by a roofer who works with slate.")],
 "cedar-shake": [("How do you keep a cedar roof lasting?", "Keep it clear of debris and moss, keep branches trimmed back, and fix split shakes early.")],
}
HOME = [
 ("How do I find a good roofer near me?", "Ask how long they've worked in your area, ask for local references, confirm the credentials your state requires, and get the scope of work in writing. Or call us and we'll connect you with a local roofing company."),
 ("How fast can a roofer come out?", "Often within a few days, and sooner for active leaks. After big storms, roofers book up quickly, so call early."),
 ("Do roofers work in winter?", "Yes. Roofers repair leaks and do emergency work year-round, and many replace roofs in winter when the weather allows."),
 ("Can I leave a review after my roofing job?", "Yes. If you called through RingaRoofer, you can leave a review on our <a href='/reviews/'>reviews page</a>. We publish genuine reviews, good or bad."),
]
