#!/usr/bin/env python3
"""
Anotherwise SEO build script.

Safe to re-run: every change sits between markers and is replaced, not duplicated.

When you buy a custom domain:
  1. Change SITE below (one line).
  2. From the project folder run:  python3 tools/seo_build.py
  3. Re-upload the site.

Needs: Python 3, Node.js (to read case study data), Pillow (for images, optional).
"""
import html, json, pathlib, re, subprocess, sys, tempfile, datetime

# ============ SETTINGS (edit here) ============
SITE = "https://anotherwise.netlify.app"      # no trailing slash
EMAIL = "ajaygoli17@gmail.com"
PHONE = "+919347435990"
PHONE_PRETTY = "+91 93474 35990"
LINKEDIN = "https://www.linkedin.com/in/ajay-goli-35182640b/"
BRAND = "Anotherwise"
TAGLINE = "Finding another way."
LASTMOD = datetime.date.today().isoformat()
# ==============================================

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = {
    "index.html": dict(
        url="/", kind="home",
        title="Anotherwise · White-Label Web, Automation & AI Studio, India",
        desc="Independent software studio in India. Websites, custom software, automation and AI for agencies, startups and growing businesses. White-label or direct.",
    ),
    "contact.html": dict(
        url="/contact.html", kind="contact", crumb="Contact",
        title="Contact Anotherwise · Start a Software or Automation Project",
        desc="Agency needing a technical delivery partner, or a business with a problem to solve? Tell Anotherwise what you need. We reply within 24 hours.",
    ),
    "casestudy1.html": dict(
        url="/casestudy1.html", kind="case", crumb="Chaitanya Bharath School",
        title="School Website for Admissions · Case Study | Anotherwise",
        desc="A parent-first school website for Nursery to Grade 7 that builds trust fast and makes an admission enquiry one tap away. Designed and built by Anotherwise.",
    ),
    "casestudy2.html": dict(
        url="/casestudy2.html", kind="case", crumb="Question Paper Generator",
        title="Exam Paper Automation with n8n · Case Study | Anotherwise",
        desc="Four connected n8n workflows turn typed or photographed questions into print-ready PDF question papers, with the teacher's original wording kept intact.",
    ),
    "casestudy3.html": dict(
        url="/casestudy3.html", kind="case", crumb="Hospital Queue Management System",
        title="Hospital Queue Management System · Concept Build",
        desc="Concept build: real-time hospital queue management with patient tokens, a reception dashboard, a waiting-room display and live phone tracking. Demo data.",
    ),
    "casestudy4.html": dict(
        url="/casestudy4.html", kind="case", crumb="Gym Trainer Platform",
        title="Gym Trainer App: Workout & Diet Plans · Concept Build",
        desc="Concept build: a gym trainer platform to create workout and diet plans, assign each to one client and see what they actually did. Demo data.",
    ),
    "casestudy5.html": dict(
        url="/casestudy5.html", kind="case", crumb="VK Photography",
        title="Photography Ecommerce Website · VK Photography Case Study",
        desc="How Anotherwise built a custom website with a live ecommerce shop and a quotation flow for VK Photography, a photo studio in Hyderabad.",
    ),
}

SERVICES = [
    ("Websites", "Fast, clear websites and landing pages built to bring in enquiries."),
    ("Custom software", "Custom web apps, portals, dashboards and business systems."),
    ("Workflow automation", "Automations that connect your tools, qualify leads and remove manual work."),
    ("AI assistants", "AI chat and voice assistants that answer from approved business information."),
    ("Build Partner for agencies", "White-label or collaborative technical delivery for marketing, web, automation and social agencies."),
    ("LeadFlow", "One connected system that answers every enquiry, follows up and books the appointment."),
]

S, E = "<!--SEO:start-->", "<!--SEO:end-->"
CS_S, CS_E = "<!--SEO-STATIC:start-->", "<!--SEO-STATIC:end-->"
e = html.escape


def abs_url(path):
    return SITE + path


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"


def breadcrumb(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def schema_for(fn, p):
    org_id, site_id = SITE + "/#org", SITE + "/#website"
    if p["kind"] == "home":
        graph = [
            {"@type": "Organization", "@id": org_id, "name": BRAND, "url": SITE + "/", "slogan": TAGLINE,
             "logo": {"@type": "ImageObject", "url": abs_url("/icon-512.png"), "width": 512, "height": 512},
             "telephone": PHONE, "sameAs": [LINKEDIN],
             "contactPoint": [{"@type": "ContactPoint", "contactType": "sales", "telephone": PHONE,
                               "availableLanguage": "English", "areaServed": "Worldwide"}]},
            {"@type": "WebSite", "@id": site_id, "url": SITE + "/", "name": BRAND, "inLanguage": "en-IN",
             "publisher": {"@id": org_id}},
            {"@type": "ProfessionalService", "@id": SITE + "/#service", "name": BRAND, "url": SITE + "/",
             "image": abs_url("/og-image.png?v=202611230016"), "description": p["desc"], "telephone": PHONE,
             "parentOrganization": {"@id": org_id},
             "areaServed": [{"@type": "Country", "name": "India"}, "Worldwide"],
             "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services", "itemListElement": [
                 {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": d,
                                                    "provider": {"@id": org_id}}} for n, d in SERVICES]}},
            {"@type": "ItemList", "name": "Case studies", "itemListElement": [
                {"@type": "ListItem", "position": i, "url": abs_url(PAGES[f"casestudy{i}.html"]["url"]),
                 "name": PAGES[f"casestudy{i}.html"]["crumb"]} for i in range(1, 6)]},
        ]
        return {"@context": "https://schema.org", "@graph": graph}
    crumbs = [("Home", SITE + "/")]
    if p["kind"] == "case":
        crumbs.append(("Case studies", SITE + "/#work"))
    crumbs.append((p["crumb"], abs_url(p["url"])))
    page = {"@type": "ContactPage" if p["kind"] == "contact" else "WebPage", "@id": abs_url(p["url"]) + "#page",
            "url": abs_url(p["url"]), "name": p["title"], "description": p["desc"], "inLanguage": "en-IN",
            "isPartOf": {"@id": site_id}, "primaryImageOfPage": {"@type": "ImageObject", "url": abs_url("/og-image.png?v=202611230016")},
            "breadcrumb": {"@id": abs_url(p["url"]) + "#crumbs"}}
    if p["kind"] == "case":
        page["about"] = p["crumb"]
        page["author"] = {"@id": org_id}
    crumb = breadcrumb(crumbs)
    crumb["@id"] = abs_url(p["url"]) + "#crumbs"
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": org_id, "name": BRAND, "url": SITE + "/"},
        {"@type": "WebSite", "@id": site_id, "url": SITE + "/", "name": BRAND, "publisher": {"@id": org_id}},
        page, crumb]}


def head_block(fn, p):
    u = abs_url(p["url"])
    og_type = "website"
    lines = [
        S,
        f"<title>{e(p['title'])}</title>",
        f'<meta name="description" content="{e(p["desc"], quote=True)}">',
        f'<link rel="canonical" href="{u}">',
        '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">',
        '<meta name="theme-color" content="#050505">',
        f'<meta name="application-name" content="{BRAND}">',
        f'<meta property="og:site_name" content="{BRAND}">',
        f'<meta property="og:type" content="{og_type}">',
        '<meta property="og:locale" content="en_IN">',
        f'<meta property="og:title" content="{e(p["title"], quote=True)}">',
        f'<meta property="og:description" content="{e(p["desc"], quote=True)}">',
        f'<meta property="og:url" content="{u}">',
        f'<meta property="og:image" content="{abs_url("/og-image.png?v=202611230016")}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{BRAND}: {TAGLINE}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{e(p["title"], quote=True)}">',
        f'<meta name="twitter:description" content="{e(p["desc"], quote=True)}">',
        f'<meta name="twitter:image" content="{abs_url("/og-image.png?v=202611230016")}">',
        '<link rel="icon" href="/favicon.ico" sizes="any">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/icon-32.png">',
        '<link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        ld(schema_for(fn, p)),
        E,
    ]
    return "\n".join(lines)


def clean_head(head):
    head = re.sub(re.escape(S) + r".*?" + re.escape(E) + r"\s*", "", head, flags=re.S)
    head = re.sub(r"<title>.*?</title>\s*", "", head, count=1, flags=re.S)
    for pat in (r'<meta\s+name="description"[^>]*>', r'<meta\s+property="og:[^"]*"[^>]*>',
                r'<meta\s+name="twitter:[^"]*"[^>]*>', r'<meta\s+name="theme-color"[^>]*>',
                r'<link\s+rel="(?:icon|apple-touch-icon|manifest|canonical)"[^>]*>'):
        head = re.sub(pat + r"\s*", "", head)
    return head


# ---------- case study data -> crawlable static HTML ----------
def read_cases(text):
    a = text.find("const M=(h,r)")
    b = text.find("/* ============ visuals", a)
    if a < 0 or b < 0:
        return None
    js = text[a:b] + "\nconsole.log(JSON.stringify(CASES));"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(js)
        path = f.name
    r = subprocess.run(["node", path], capture_output=True, text=True)
    if r.returncode:
        print("  ! could not read case data:", r.stderr[:200])
        return None
    d = json.loads(r.stdout)
    return list(d.values())[0]


def static_html(c, current):
    o = ['<article class="seo-static">']
    o.append(f'<p class="seo-kicker">{e(c.get("brand",""))} · Case study</p>')
    o.append(f'<h1>{e(c.get("title",""))}</h1><p>{e(c.get("intro",""))}</p>')
    if c.get("meta"):
        o.append("<dl>" + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in c["meta"].items()) + "</dl>")
    if c.get("live"):
        o.append(f'<p>Live site: <a href="{e(c["live"])}" rel="noopener">{e(c["live"])}</a></p>')
    ov = c.get("overview") or {}
    for key, label in (("challenge", "The challenge"), ("approach", "Our approach"), ("outcome", "The outcome")):
        if ov.get(key):
            o.append(f"<h2>{label}</h2><p>{e(ov[key])}</p>")
    fr = c.get("friction")
    if isinstance(fr, dict) and fr.get("items"):
        o.append(f"<h2>{e(fr.get('title',''))}</h2><ul>" + "".join(
            f"<li><strong>{e(i[0])}</strong>: {e(i[1])}</li>" for i in fr["items"]) + "</ul>")
    if c.get("steps"):
        o.append(f"<h2>{e(c.get('stTitle') or 'How we built it')}</h2><ol>" + "".join(
            f"<li><strong>{e(s[0])}</strong>: {e(s[1])}</li>" for s in c["steps"]) + "</ol>")
    fl = c.get("flow")
    if isinstance(fl, dict) and fl.get("n"):
        o.append(f"<h2>{e(fl.get('title',''))}</h2><p>{e(fl.get('text',''))}</p><ol>" + "".join(
            f"<li>{e(' · '.join(str(x) for x in n))}</li>" for n in fl["n"]) + "</ol>")
    if c.get("results"):
        o.append("<h2>Results</h2><ul>" + "".join(f"<li><strong>{e(r[0])}</strong> {e(r[1])}</li>" for r in c["results"]) + "</ul>")
    elif c.get("kpis"):
        o.append("<h2>Key figures</h2><ul>" + "".join(f"<li><strong>{e(k['v'])}</strong> {e(k['l'])}</li>" for k in c["kpis"]) + "</ul>")
    if c.get("refl"):
        o.append("<h2>What we learned</h2><ul>" + "".join(f"<li><strong>{e(r[0])}</strong>: {e(r[1])}</li>" for r in c["refl"]) + "</ul>")
    if c.get("stack"):
        o.append("<h2>Built with</h2><ul>" + "".join(f"<li>{e(s)}</li>" for s in c["stack"]) + "</ul>")
    if c.get("tags"):
        o.append("<p>" + e(" · ".join(c["tags"])) + "</p>")
    others = [(f, q) for f, q in PAGES.items() if q["kind"] == "case" and f != current]
    o.append("<h2>More case studies</h2><ul>" + "".join(f'<li><a href="{f}">{e(q["crumb"])}</a></li>' for f, q in others) + "</ul>")
    o.append(f'<p><a href="index.html">{BRAND} home</a> · <a href="contact.html">Start a project</a></p>')
    o.append("</article>")
    css = ("<style>.seo-static{max-width:46rem;margin:0 auto;padding:7rem 6vw 4rem;line-height:1.7;color:#d6d6d6}"
           ".seo-static h1,.seo-static h2{color:#fff;line-height:1.15}.seo-static a{color:#B8FF00}"
           ".seo-kicker{color:#B8FF00;letter-spacing:.2em;text-transform:uppercase;font-size:.75rem}</style>")
    return css + "\n".join(o)


def process_page(fn, p):
    path = ROOT / fn
    text = path.read_text(encoding="utf-8")
    i = text.find("</head>")
    head, rest = text[:i], text[i:]
    head = clean_head(head)
    m = re.search(r'<meta\s+name="viewport"[^>]*>', head)
    block = head_block(fn, p)
    head = head[:m.end()] + "\n" + block + head[m.end():] if m else head + block
    text = head + rest

    if p["kind"] == "case":
        # keep the SEO title instead of the JS override
        text = text.replace("document.title=`${c.title} · Case study`;", "")
        c = read_cases(text)
        if c:
            payload = f'{CS_S}{static_html(c, fn)}{CS_E}'
            if CS_S in text:
                text = re.sub(re.escape(CS_S) + r".*?" + re.escape(CS_E), lambda _m: payload, text, flags=re.S)
            else:
                text = re.sub(r'<(div|main) id="app"></\1>', lambda m: f'<{m.group(1)} id="app">{payload}</{m.group(1)}>', text, count=1)
    # one public email across the site
    text = text.replace("ajaygoli9347@gmail.com", EMAIL).replace("ajaygoli17@gmail.com", EMAIL)
    path.write_text(text, encoding="utf-8")
    print("  ok", fn)


# ---------- files ----------
def write_files():
    urls = "".join(f"  <url><loc>{abs_url(p['url'])}</loc><lastmod>{LASTMOD}</lastmod></url>\n" for p in PAGES.values())
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "site.webmanifest").write_text(json.dumps({
        "name": BRAND, "short_name": BRAND, "description": PAGES["index.html"]["desc"], "start_url": "/",
        "display": "standalone", "background_color": "#050505", "theme_color": "#050505",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=2), encoding="utf-8")
    (ROOT / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  X-Frame-Options: SAMEORIGIN\n  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n\n"
        "/*.png\n  Cache-Control: public, max-age=2592000\n\n/*.ico\n  Cache-Control: public, max-age=2592000\n", encoding="utf-8")
    (ROOT / "404.html").write_text(f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found · {BRAND}</title><meta name="robots" content="noindex">
<link rel="icon" href="/favicon.ico" sizes="any"><meta name="theme-color" content="#050505">
<style>html,body{{height:100%;margin:0;background:#050505;color:#fff;font-family:Inter,system-ui,sans-serif}}
main{{min-height:100%;display:grid;place-content:center;text-align:center;padding:2rem;gap:1rem}}
h1{{font-size:clamp(2rem,6vw,3.5rem);margin:0}}p{{color:#a8a8a8;margin:0}}a{{color:#050505;background:#B8FF00;padding:.7rem 1.4rem;border-radius:99px;text-decoration:none;font-weight:600;justify-self:center}}</style>
</head><body><main><h1>Page not found</h1><p>That page doesn't exist. {TAGLINE}</p><a href="/">Back to {BRAND}</a></main></body></html>
""", encoding="utf-8")


def make_images():
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
    except ImportError:
        print("  ! Pillow missing: skipped icons and share image (pip install pillow)")
        return
    src = ROOT / "anotherwise-app-icon-2.png"
    if not src.exists():
        print("  ! anotherwise-app-icon-2.png not found: skipped images")
        return
    icon = Image.open(src).convert("RGBA")
    for name, size in (("icon-32.png", 32), ("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)):
        icon.resize((size, size), Image.LANCZOS).save(ROOT / name, optimize=True)
    icon.resize((48, 48), Image.LANCZOS).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (5, 5, 5))
    glow = Image.new("RGB", (W, H), (5, 5, 5))
    ImageDraw.Draw(glow).ellipse((-260, -200, 620, 520), fill=(60, 95, 0))
    img = Image.blend(img, glow.filter(ImageFilter.GaussianBlur(120)), 0.9)
    d = ImageDraw.Draw(img)

    def font(size, bold=True):
        for f in ("/usr/share/fonts/opentype/inter/Inter-%s.otf" % ("Bold" if bold else "Regular"),
                  "/Library/Fonts/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
                  "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                continue
        return ImageFont.load_default()

    d.text((72, 72), "ANOTHERWISE", font=font(30), fill=(184, 255, 0))
    y = 190
    for line in ("Websites, automation", "& AI for agencies", "and growing businesses."):
        d.text((72, y), line, font=font(66), fill=(255, 255, 255))
        y += 84
    d.text((72, 520), TAGLINE + "  ·  Software studio, India", font=font(30, False), fill=(168, 168, 168))
    big = icon.resize((300, 300), Image.LANCZOS)
    img.paste(big, (W - 300 - 80, 80), big)
    # img.save(ROOT / "og-image.png", optimize=True)


def main():
    print(f"Site: {SITE}\nRoot: {ROOT}")
    for fn, p in PAGES.items():
        if not (ROOT / fn).exists():
            print("  ! missing", fn)
            continue
        process_page(fn, p)
    write_files()
    make_images()
    print("Done.")


if __name__ == "__main__":
    sys.exit(main())
