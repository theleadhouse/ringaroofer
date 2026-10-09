"""
AI search visibility — shared by every TLH site build (copied into each repo's src/).
Called at the end of build.py:  import ai_visibility; ai_visibility.apply(OUT)

1. robots.txt: welcomes search engines AND AI answer engines (ChatGPT search, Copilot/Bing, Perplexity, Claude,
   Gemini, Apple Intelligence, DuckDuckGo) by name, keeps any Disallow rules the build already wrote, and keeps
   blocking heavy SEO scrapers.
2. IndexNow key file: lets Bing (which powers Copilot and much of ChatGPT search), Yandex, Seznam and Naver
   index new pages within minutes. The key is public by design (it only proves we own the site).
"""
import os, re

INDEXNOW_KEY = "0bec995cd87a1631b75c6b32dcd6afe8"

AI_AGENTS = [
    "OAI-SearchBot", "ChatGPT-User", "GPTBot",            # OpenAI: ChatGPT search, browsing, model knowledge
    "bingbot", "msnbot",                                   # Microsoft Bing / Copilot
    "PerplexityBot", "Perplexity-User",                    # Perplexity
    "Claude-SearchBot", "Claude-User", "ClaudeBot",        # Anthropic Claude
    "Googlebot", "Google-Extended",                        # Google Search, Gemini / AI Overviews
    "Applebot", "Applebot-Extended",                       # Apple Siri / Apple Intelligence
    "DuckAssistBot",                                       # DuckDuckGo AI answers
    "Amazonbot", "MistralAI-User", "meta-externalagent",   # Alexa, Le Chat, Meta AI
]
SCRAPERS = ["AhrefsBot", "SemrushBot", "MJ12bot", "DotBot"]


def apply(out_dir):
    path = os.path.join(out_dir, "robots.txt")
    old = open(path).read() if os.path.exists(path) else ""
    sitemap = re.search(r"(?im)^Sitemap:\s*(\S+)", old)
    sitemap = sitemap.group(1) if sitemap else ""
    # Disallow rules that applied to everyone (first "User-agent: *" group), e.g. /api/
    star = re.search(r"(?is)User-agent:\s*\*\s*\n(.*?)(?:\n\s*\n|\Z)", old)
    rules = [l.strip() for l in (star.group(1).splitlines() if star else []) if l.strip().lower().startswith("disallow:")]
    rules_txt = "".join(r + "\n" for r in rules)
    txt = ("# Search engines and AI assistants are welcome to read and cite our public pages.\n"
           "User-agent: *\nAllow: /\n" + rules_txt + "\n"
           "# AI search and answer engines, named explicitly so they are never caught by a blanket block\n"
           + "".join(f"User-agent: {a}\n" for a in AI_AGENTS) + "Allow: /\n" + rules_txt + "\n"
           "# Heavy SEO scrapers that add load but send no visitors\n"
           + "".join(f"User-agent: {a}\n" for a in SCRAPERS) + "Disallow: /\n"
           + (f"\nSitemap: {sitemap}\n" if sitemap else ""))
    with open(path, "w") as f:
        f.write(txt)
    with open(os.path.join(out_dir, INDEXNOW_KEY + ".txt"), "w") as f:
        f.write(INDEXNOW_KEY)
