"""RingARoofer ad landing pages (/call/): the lead form and the call button share the first view. Generator: landing.py (shared across sites).
Roofing word list is strict (no damage, claim, professional, gutters, windows, siding, chimney, solar, skylight, cost/price/quote...)."""
COMMON_FAQ = [
 ("Is there a charge to call or send a request?", "No. RingaRoofer doesn't charge homeowners. You agree any work and terms directly with the roofing company."),
 ("Who will contact me?", "An independent roofing company that serves your area. They'll ask about the roof and set up a time to look at it."),
 ("How soon can a roofer come out?", "It depends on your area and recent weather. After storms, roofers book up quickly, so it helps to reach out early."),
 ("Do you do the roofing work yourselves?", "No. RingaRoofer is a referral service. The roofing company does the work and agrees the details with you directly."),
]
SAFETY = ("Leaking right now?", "Move belongings away, put a bucket under the drip and keep clear of a sagging ceiling. Don't go up on a wet or storm-hit roof yourself.")
BULLETS = ["No charge to request", "Local roofing companies", "No obligation"]
CALL_NOTE = "Prefer to talk? Tap to call a local roofing company."
STEPS = [("Tell us about your roof", "Use the form or call {PHONE}. It takes under a minute."),
         ("Get matched", "We connect you with an independent roofing company that serves your ZIP code."),
         ("You decide", "They look at the roof and explain the options. No obligation to go ahead.")]
END = ("Talk to a local roofer now.", "One call. No charge. No obligation.")
LEGAL = [("RingaRoofer.com", "/"), ("Privacy", "/privacy/"), ("Terms", "/terms/"), ("Referral Disclosure", "/referral-disclosure/"), ("California Privacy", "/ca-privacy/"), ("Do Not Call", "/dnc/")]

PAGES = [
 dict(slug="roof-repair", photo="roofer", kick="Roof repair",
      h1a="Need a roof repair?", h1b="Get matched with a local roofer.",
      sub="Leaks, missing shingles, flashing and storm repairs from independent roofing companies that serve your area.",
      chips=["Roof leaking", "Missing shingles", "Water stain on the ceiling", "Flashing coming loose", "Sagging spot", "Shingles curling"],
      checks=["Look at the roof from the ground for missing or lifted shingles", "Check the attic with a flashlight for drips or wet insulation", "Take photos of any stains or spots inside"],
      title="Roof Repair Near You | Local Roofers · (888) 261-1486 | RingaRoofer"),
 dict(slug="roof-replacement", photo="newroof2", kick="New roof",
      h1a="Time for a new roof?", h1b="Talk to a local roofing company.",
      sub="Re-roofs and full replacements on shingle, metal, flat and tile roofs, from roofing companies near you.",
      chips=["Roof is 20+ years old", "Shingles curling or bald", "Leaks keep coming back", "Granules in the yard", "Moss or rot", "Buying or selling a home"],
      checks=["Find out the roof's age (home records or the last inspection)", "Look for curling, cracked or missing shingles from the ground", "Note any leaks over the past year"],
      title="Roof Replacement Near You | New Roofs · (888) 261-1486 | RingaRoofer"),
 dict(slug="roof-leak", photo="ceiling", kick="Roof leak",
      h1a="Roof leaking?", h1b="Get a roofer on it.",
      sub="Drips, ceiling stains or water in the attic. Get matched with an independent roofing company that serves your area.",
      chips=["Dripping from the ceiling", "Stain getting bigger", "Water in the attic", "Leak only in heavy rain", "Leak near a vent", "Bubbling paint"],
      checks=["Put a bucket under the drip and move belongings away", "If the ceiling bulges, poke a small hole to drain it into the bucket", "Take photos for your records"],
      title="Roof Leak Repair Near You | (888) 261-1486 | RingaRoofer"),
 dict(slug="storm-hail", photo="hail2", kick="Storm and hail",
      h1a="Storm or hail hit your roof?", h1b="Get it checked by a local roofer.",
      sub="High wind lifts shingles and hail bruises them, often without anything visible from the ground. Get matched with a roofing company near you.",
      chips=["Shingles blown off", "Hail last night", "Dents on vents", "Tree branch on the roof", "New leak after a storm", "Neighbors getting new roofs"],
      checks=["Look from the ground for missing shingles or debris", "Check vents, the AC unit and the car for hail dents", "Take dated photos before anything is repaired"],
      title="Storm & Hail Roof Repair Near You | (888) 261-1486 | RingaRoofer"),
 dict(slug="roofer", photo="roofer2", kick="Roofers near you",
      h1a="Need a roofer?", h1b="Get matched with one near you.",
      sub="Repairs, leaks, storm and hail, inspections, new roofs and re-roofs from independent roofing companies that serve your area.",
      chips=["Roof repair", "Roof leak", "New roof", "Storm or hail", "Roof inspection", "Not sure what's wrong"],
      checks=["Note what you're seeing and where", "Take a few photos from the ground", "Know roughly how old the roof is"],
      title="Roofers Near You | (888) 261-1486 | RingaRoofer"),
 dict(slug="roof-inspection", photo="inspect", kick="Roof inspection",
      h1a="Need your roof checked?", h1b="Book a local roofer.",
      sub="After a storm, before buying or selling, or when the roof is getting older. Get matched with a roofing company near you.",
      chips=["After a storm", "Buying a home", "Selling a home", "Roof over 15 years", "Recent leak", "Moss or algae"],
      checks=["Have the home's age and any roofing records handy", "Note any leaks or stains inside", "Clear access to the attic hatch"],
      title="Roof Inspection Near You | (888) 261-1486 | RingaRoofer"),
]
