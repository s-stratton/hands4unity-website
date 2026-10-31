#!/usr/bin/env python3
"""Builds the Hands 4 Unity static site.

Run from anywhere:  python3 _build/build.py
Pages are written into the repository root, one folder per page,
so the old WordPress URLs (/about-us/, /projects/africa-day-2025/ ...) keep working.

Edit content in content.py and projects.py, the shared layout here,
then re-run the script. Uses the Python standard library only.
"""
from __future__ import annotations

import datetime as _dt
import html
import os
from pathlib import Path

from content import (
    FINANCIALS_2022, GET_INVOLVED_BENEFITS, MISSION, OBJECTIVE, SERVICES, SITE,
    SUPPORTERS, TEAM_BOARD, TEAM_REPS, VISION,
)
from icons import icon, shamrock
from projects import BY_SLUG, PROJECTS

ROOT = Path(__file__).resolve().parent.parent
YEAR = _dt.date.today().year
ASSET_VERSION = _dt.date.today().strftime("%Y%m%d")
# Cloudflare Web Analytics: counts visits without cookies. The token is public by design.
CF_ANALYTICS_TOKEN = "8e46b1fcd0484569975259df725713fb"
# Private admin dashboard (google-apps-script/dashboard). Only hands4unity.org Google accounts can open it.
ADMIN_DASHBOARD_URL = "https://script.google.com/a/macros/hands4unity.org/s/AKfycbyFJANmK3M2iaxzub2dnSivZkAi8sYktb1j94BLJF_fq7NNq1V_bB0I0tcXhXUt_qJq-g/exec"

NAV = [
    ("", "Home"),
    ("about-us/", "About Us"),
    ("projects/", "Projects"),
    ("get-involved/", "Get Involved"),
    ("contact-us/", "Contact Us"),
]

e = html.escape
_written: list[str] = []


# --------------------------------------------------------------------------- helpers

def link(R: str, href: str) -> str:
    """Turn a site-relative href ('contact-us/') into one relative to the current page."""
    if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
        return href
    return R + href if href else (R or "./")


def img(R: str, path: str, alt: str = "", cls: str = "", eager: bool = False, sizes: str = "") -> str:
    loading = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<img src="{R}assets/img/{path}" alt="{e(alt)}"{c} {loading}>'


def logo(R: str) -> str:
    # The organisation's own logo, taken from the old WordPress site (only available at 235x80).
    return f'<img class="logo" src="{R}assets/img/logo-original.png" alt="Hands 4 Unity" width="235" height="80">'


def footer_logo(R: str) -> str:
    # The logo image is too low-res for the dark footer, so pair its hands icon with the name as text.
    return (
        '<span class="footer-logo">'
        f'<img src="{R}assets/img/logo-icon.png" alt="" width="70" height="70">'
        '<span class="footer-logo-word">Hands <span class="footer-logo-4">4</span> Unity</span>'
        '</span>'
    )


def socials(cls: str = "socials") -> str:
    items = "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener" aria-label="{e(label)}">{icon(ic)}</a></li>'
        for ic, label, url in SITE["social"]
    )
    return f'<ul class="{cls}">{items}</ul>'


def address_html(sep: str = "<br>") -> str:
    return sep.join(e(line) for line in SITE["address"])


def btn(R: str, label: str, href: str, kind: str = "primary", ic: str | None = "arrow-right", external: bool = False) -> str:
    ext = ' target="_blank" rel="noopener"' if external else ""
    i = icon(ic) if ic else ""
    return f'<a class="btn btn-{kind}" href="{link(R, href)}"{ext}><span>{e(label)}</span>{i}</a>'


def section_head(eyebrow: str, title: str, intro: str = "", center: bool = False) -> str:
    c = " section-head--center" if center else ""
    intro_html = f'<p class="lead">{intro}</p>' if intro else ""
    return f'<div class="section-head{c}"><p class="eyebrow">{e(eyebrow)}</p><h2>{title}</h2>{intro_html}</div>'


def project_card(R: str, p: dict, heading: str = "h3") -> str:
    kind = p["kind"].lower()
    return f"""
<article class="card" data-kind="{kind}">
  <a class="card-link" href="{R}projects/{p['slug']}/">
    <div class="card-media">{img(R, p['card'], '')}</div>
    <div class="card-body">
      <p class="meta"><span class="tag tag-{kind}">{e(p['kind'])}</span><span>{e(p['when'])}</span></p>
      <{heading} class="card-title">{e(p['title'])}</{heading}>
      <p>{e(p['excerpt'])}</p>
      <span class="link-arrow">Read more {icon('arrow-right')}</span>
    </div>
  </a>
</article>"""


def page_hero(R: str, title: str, crumbs: list[tuple[str, str]], intro: str = "", eyebrow: str = "") -> str:
    trail = "".join(f'<li><a href="{link(R, h)}">{e(t)}</a></li>' for h, t in crumbs)
    eb = f'<p class="eyebrow">{e(eyebrow)}</p>' if eyebrow else ""
    intro_html = f'<p class="lead">{intro}</p>' if intro else ""
    return f"""
<section class="page-hero">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="{link(R, '')}">Home</a></li>{trail}<li aria-current="page">{e(title)}</li></ol></nav>
    {eb}<h1>{e(title)}</h1>{intro_html}
  </div>
  {shamrock('hero-shamrock')}
</section>"""


def donate_band(R: str) -> str:
    return f"""
<section class="donate-band">
  <div class="container donate-inner">
    <div>
      <h2>We need your help</h2>
      <p>Hands 4 Unity relies on the generosity of individuals to do our work. If you would like to support our causes, please consider donating.</p>
    </div>
    <div class="donate-actions">
      {btn(R, 'Donate', SITE['donate'], 'primary', 'heart', external=True)}
      {btn(R, 'Get involved', 'get-involved/', 'ghost-dark')}
    </div>
  </div>
</section>"""


def consent_html(R: str) -> str:
    return (
        '<label class="check consent"><input type="checkbox" name="consent" required>'
        f'<span>I consent to Hands 4 Unity using this information to contact me. Your details will only be used to respond '
        f'to you. See our <a href="{R}privacy-policy/">Privacy Policy</a>.</span></label>'
    )


def form_tail(label: str) -> str:
    return f"""
  <p class="hp" aria-hidden="true"><label>Leave this field empty <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
  <button class="btn btn-primary" type="submit"><span>{e(label)}</span>{icon('arrow-right')}</button>
  <p class="form-status" role="status" aria-live="polite"></p>"""


# --------------------------------------------------------------------------- layout

def layout(path: str, title: str, description: str, body: str, active: str = "", og_image: str = "general/dancers-stage.jpg", body_class: str = "") -> None:
    depth = path.count("/")
    R = "../" * depth
    canonical = SITE["url"] + "/" + (path[: -len("index.html")] if path.endswith("index.html") else path)
    full_title = f"{title} | {SITE['name']}" if title != SITE["name"] else f"{SITE['name']} | Empowering women in Drogheda"

    current = ' aria-current="page"'
    nav_items = "".join(
        f'<li><a href="{link(R, h)}"{current if h == active else ""}>{e(t)}</a></li>'
        for h, t in NAV
    )
    footer_links = "".join(f'<li><a href="{link(R, h)}">{e(t)}</a></li>' for h, t in NAV[1:])

    doc = f"""<!doctype html>
<html lang="en-IE">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(full_title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{canonical}">
  <meta name="theme-color" content="#1f1a17">
  <link rel="icon" href="{R}assets/favicon.png" type="image/png">
  <link rel="apple-touch-icon" href="{R}assets/apple-touch-icon.png">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE['name']}">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE['url']}/assets/img/{og_image}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{R}css/styles.css?v={ASSET_VERSION}">
  <script defer src="{R}js/main.js?v={ASSET_VERSION}"></script>
  <script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "{CF_ANALYTICS_TOKEN}"}}'></script>
</head>
<body class="{body_class}">
<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar">
  <div class="container topbar-inner">
    <p><a href="tel:{SITE['phone_tel']}">{icon('phone')}{SITE['phone_display']}</a><a href="mailto:{SITE['email']}">{icon('mail')}{SITE['email']}</a></p>
    {socials('socials socials--small')}
  </div>
</div>
<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="{link(R, '')}" aria-label="Hands 4 Unity home">{logo(R)}</a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <span class="nav-toggle-open">{icon('menu')}</span><span class="nav-toggle-close">{icon('x')}</span><span class="sr-only">Menu</span>
    </button>
    <nav id="site-nav" class="site-nav" aria-label="Main">
      <ul>{nav_items}</ul>
      <a class="btn btn-primary btn-sm" href="{SITE['donate']}" target="_blank" rel="noopener"><span>Donate</span>{icon('heart')}</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-brand">
      <a class="brand brand--light" href="{link(R, '')}" aria-label="Hands 4 Unity home">{footer_logo(R)}</a>
      <p>A support network for women and families of all backgrounds, in Drogheda, across Ireland and abroad.</p>
      {socials()}
    </div>
    <div>
      <h2 class="footer-title">Explore</h2>
      <ul class="footer-links">{footer_links}<li><a href="{SITE['donate']}" target="_blank" rel="noopener">Donate</a></li></ul>
    </div>
    <div>
      <h2 class="footer-title">Contact</h2>
      <address>{SITE['legal']}<br>{address_html()}</address>
      <p class="footer-contact"><a href="tel:{SITE['phone_tel']}">{SITE['phone_display']}</a><br><a href="mailto:{SITE['email']}">{SITE['email']}</a></p>
    </div>
    <div>
      <h2 class="footer-title">Newsletter</h2>
      <p>Keep up to date with our latest news, events and opportunities, straight to your inbox.</p>
      <form class="newsletter" data-form="newsletter" novalidate>
        <label class="sr-only" for="nl-email">Email address</label>
        <input id="nl-email" type="email" name="email" placeholder="Your email address" autocomplete="email" required>
        <input type="hidden" name="subject" value="Newsletter sign-up">
        <p class="hp" aria-hidden="true"><label>Leave this field empty <input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></p>
        <button class="btn btn-primary btn-sm" type="submit"><span>Sign up</span></button>
        <p class="form-status" role="status" aria-live="polite"></p>
      </form>
    </div>
  </div>
  <div class="container footer-bottom">
    <p>&copy; {YEAR} {SITE['legal']} &middot; Registered company no. {SITE['company_no']}</p>
    <ul>
      <li><a href="{R}privacy-policy/">Privacy Policy</a></li>
      <li><a href="{R}cookies-policy/">Cookies Policy</a></li>
      <li><a href="{R}financial-information/">Financial Information</a></li>
    </ul>
  </div>
</footer>
<dialog class="lightbox" aria-label="Photo viewer">
  <button class="lightbox-close" type="button" aria-label="Close">{icon('x')}</button>
  <button class="lightbox-nav lightbox-prev" type="button" aria-label="Previous photo">{icon('arrow-left')}</button>
  <img alt="">
  <button class="lightbox-nav lightbox-next" type="button" aria-label="Next photo">{icon('arrow-right')}</button>
</dialog>
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    _written.append(path)


# --------------------------------------------------------------------------- pages

def build_home() -> None:
    R = ""
    current = [BY_SLUG[s] for s in ("coaching-and-mentoring-for-job-seekers", "tuesdays-sewing-workshop-in-english", "kids-can-code-summer-camp-2025")]
    recent = [BY_SLUG[s] for s in ("taste-of-all-nations-2025", "africa-day-2025", "inaugural-taste-of-all-nations")]
    services = "".join(
        f'<li class="feature">{icon(ic)}<h3>{e(t)}</h3><p>{e(d)}</p></li>' for ic, t, d in SERVICES
    )
    founder = TEAM_BOARD[0]
    supporters = "".join(f"<li>{e(s)}</li>" for s in SUPPORTERS)

    body = f"""
<section class="hero">
  <div class="container hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Drogheda &middot; Co. Louth &middot; Ireland</p>
      <h1>Empowering women, <em>uniting</em> communities.</h1>
      <p class="lead">Hands 4 Unity is a support network for women and families of all backgrounds, in Ireland and abroad. We help women find work, learn new skills and build a sense of belonging.</p>
      <div class="hero-actions">
        {btn(R, 'Learn about us', 'about-us/')}
        {btn(R, 'See our projects', 'projects/', 'ghost', None)}
      </div>
    </div>
    <div class="hero-media">
      <figure class="hero-photo hero-photo--main">{img(R, 'projects/toan-2025/dancers.jpg', 'Dancers in traditional dress performing at Taste of All Nations 2025', eager=True)}</figure>
      <figure class="hero-photo hero-photo--small">{img(R, 'projects/sewing/cover.jpg', 'Two women at a sewing machine during the Sewing Workshop in English', eager=True)}</figure>
      <div class="hero-badge">{shamrock()}<span>Care knows<br>no borders</span></div>
    </div>
  </div>
</section>

<section class="section section--peach">
  <div class="container split">
    <figure class="split-media">{img(R, 'projects/coaching/cover.jpg', 'A mentor and a job seeker working through a CV together')}</figure>
    <div class="split-copy">
      <p class="eyebrow">Coaching &amp; mentoring</p>
      <h2>Looking for a job in Ireland and not sure where to start?</h2>
      <p class="lead">You don't have to do it alone.</p>
      <p>We support migrant and Irish women who want to enter the workforce, return to employment or change careers, with real, practical guidance every step of the way.</p>
      <ul class="ticks">
        <li>One-to-one coaching to build your confidence</li>
        <li>CV clinics and interview preparation</li>
        <li>Mentors who know the Irish job market</li>
      </ul>
      <div class="actions">
        {btn(R, 'Book a free session', 'contact-us/?subject=Coaching%20appointment')}
        {btn(R, 'Find out more', 'projects/coaching-and-mentoring-for-job-seekers/', 'ghost', None)}
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head('What we do', 'Networking, education, job access and social support', e(OBJECTIVE), center=True)}
    <ul class="features">{services}</ul>
  </div>
</section>

<section class="section section--cream">
  <div class="container">
    <div class="section-head-row">
      {section_head('Running now', 'Current programmes', 'Hands 4 Unity works with Drogheda-based women from diverse backgrounds to improve their experience of community integration.')}
    </div>
    <div class="cards">{''.join(project_card(R, p) for p in current)}</div>
  </div>
</section>

<section class="quote-band">
  <div class="container">
    {shamrock('quote-mark')}
    <blockquote>
      <p>We bring women and families of all races together in an environment where care knows no borders, love has no divides, and help has no differentiation.</p>
      <footer>Our mission</footer>
    </blockquote>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head-row">
      {section_head('Community events', 'Celebrating the cultures that make our community')}
      {btn(R, 'View all projects', 'projects/', 'ghost')}
    </div>
    <div class="cards">{''.join(project_card(R, p) for p in recent)}</div>
  </div>
</section>

<section class="section section--cream">
  <div class="container split split--reverse">
    <figure class="split-media split-media--portrait">{img(R, founder['photo'], founder['name'])}</figure>
    <div class="split-copy">
      <p class="eyebrow">Meet our founder</p>
      <h2>{e(founder['name'])}</h2>
      <p class="role">{e(founder['role'])}</p>
      <p>{e(founder['bio'][0])}</p>
      <p>Ejiro leads a board and committee of volunteers from across Drogheda's communities, including Ireland, Nigeria, India and the Philippines.</p>
      <div class="actions">{btn(R, 'Meet the team', 'about-us/#team')}</div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <p class="supporters-title">With thanks to our funders, sponsors and partners</p>
    <ul class="supporters">{supporters}</ul>
  </div>
</section>

{donate_band(R)}
"""
    layout(
        "index.html", SITE["name"],
        "Hands 4 Unity is a Drogheda-based support network empowering migrant and Irish women through coaching, skills workshops and community events.",
        body, active="", og_image="projects/toan-2025/cover.jpg", body_class="home",
    )


def team_card(R: str, m: dict, idx: str, featured: bool = False) -> str:
    bio = "".join(f"<p>{e(p)}</p>" for p in m["bio"])
    cls = "member member--featured" if featured else "member"
    teaser = f'<p class="member-teaser">{e(m["bio"][0])}</p>' if featured else ""
    return f"""
<li class="{cls}">
  <div class="member-photo">{img(R, m['photo'], m['name'])}</div>
  <div class="member-body">
    <h3>{e(m['name'])}</h3>
    <p class="role">{e(m['role'])}</p>
    {teaser}
    <div class="member-actions">
      <button class="text-btn" type="button" data-dialog="bio-{idx}">Read bio {icon('arrow-right')}</button>
      <a class="icon-btn" href="{m['linkedin']}" target="_blank" rel="noopener" aria-label="{e(m['name'])} on LinkedIn">{icon('linkedin')}</a>
    </div>
  </div>
  <dialog class="bio-dialog" id="bio-{idx}" aria-labelledby="bio-{idx}-name">
    <button class="dialog-close" type="button" aria-label="Close">{icon('x')}</button>
    <div class="bio-head">{img(R, m['photo'], '')}<div><h3 id="bio-{idx}-name">{e(m['name'])}</h3><p class="role">{e(m['role'])}</p></div></div>
    <div class="prose">{bio}</div>
  </dialog>
</li>"""


def build_about() -> None:
    R = "../"
    services = "".join(f'<li class="feature">{icon(ic)}<h3>{e(t)}</h3><p>{e(d)}</p></li>' for ic, t, d in SERVICES)
    mission = "".join(f"<p>{e(p)}</p>" for p in MISSION)
    founder = team_card(R, TEAM_BOARD[0], "0", featured=True)
    board = "".join(team_card(R, m, f"b{i}") for i, m in enumerate(TEAM_BOARD[1:], 1))
    reps = "".join(team_card(R, m, f"r{i}") for i, m in enumerate(TEAM_REPS))
    body = f"""
{page_hero(R, 'About Us', [], 'A support network uniting women and families of all races, in Drogheda and beyond.', 'Who we are')}

<section class="section">
  <div class="container split">
    <div class="split-copy">
      <p class="eyebrow">Our vision</p>
      <h2>A community where care knows no borders</h2>
      <p class="lead">{e(VISION.split('. ')[0])}.</p>
      <p>{e('. '.join(VISION.split('. ')[1:]))}</p>
    </div>
    <div class="photo-pair">
      <figure>{img(R, 'general/art-exhibition.jpg', 'Women in colourful dress at a Hands 4 Unity art exhibition')}</figure>
      <figure>{img(R, 'general/culture-night.jpg', 'A woman in a floral crown at Culture Night')}</figure>
    </div>
  </div>
</section>

<section class="section section--ink">
  <div class="container split split--top">
    <div>
      <p class="eyebrow eyebrow--light">Our mission</p>
      <h2>Empowering women to become change-makers and leaders</h2>
    </div>
    <div class="prose prose--light">{mission}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    {section_head('Our objective', 'What we do', e(OBJECTIVE), center=True)}
    <ul class="features">{services}</ul>
  </div>
</section>

<section class="section section--cream" id="team">
  <div class="container">
    {section_head('Meet our team', 'The people behind Hands 4 Unity', 'Our board and committee members come from many of the communities we serve, and give their time as volunteers.', center=True)}
    <ul class="team team--featured">{founder}</ul>
    <h3 class="team-group">Board of directors &amp; officers</h3>
    <ul class="team">{board}</ul>
    <h3 class="team-group">Ambassadors &amp; committee representatives</h3>
    <ul class="team">{reps}</ul>
  </div>
</section>

{donate_band(R)}
"""
    layout("about-us/index.html", "About Us",
           "Our vision, mission and the team behind Hands 4 Unity, a Drogheda support network for women and families of all backgrounds.",
           body, active="about-us/", og_image="general/art-exhibition.jpg")


def build_projects_index() -> None:
    R = "../"
    cards = "".join(project_card(R, p, "h2") for p in PROJECTS)
    body = f"""
{page_hero(R, 'Our Projects', [], 'Programmes and events that help women build skills, find work and celebrate the cultures of our community.', 'What we do')}
<section class="section">
  <div class="container">
    <div class="filters" role="group" aria-label="Filter projects">
      <button type="button" class="chip is-active" data-filter="all" aria-pressed="true">All</button>
      <button type="button" class="chip" data-filter="programme" aria-pressed="false">Programmes</button>
      <button type="button" class="chip" data-filter="event" aria-pressed="false">Events</button>
    </div>
    <div class="cards" data-filterable>{cards}</div>
  </div>
</section>
{donate_band(R)}
"""
    layout("projects/index.html", "Projects",
           "Hands 4 Unity programmes and community events, from coaching for job seekers and sewing workshops to Taste of All Nations and Africa Day.",
           body, active="projects/", og_image="projects/toan-2025/cover.jpg")


def build_project(p: dict) -> None:
    R = "../../"
    sections = []
    for i, s in enumerate(p["sections"]):
        rev = " split--reverse" if i % 2 else ""
        sections.append(f"""
<section class="section{' section--cream' if i % 2 else ''}">
  <div class="container split{rev}">
    <figure class="split-media">{img(R, s['image'], s['heading'])}</figure>
    <div class="split-copy prose">
      <h2>{e(s['heading'])}</h2>
      {s['body']}
    </div>
  </div>
</section>""")

    facts = ""
    if p.get("details"):
        items = "".join(
            f'<div class="fact">{icon(ic)}<dt>{e(label)}</dt><dd>{e(val)}</dd></div>' for ic, label, val in p["details"]
        )
        facts = f"""
<section class="section section--tight">
  <div class="container">
    <div class="facts-card">
      <h2>{e(p.get('details_title', 'Details'))}</h2>
      <dl class="facts">{items}</dl>
    </div>
  </div>
</section>"""

    gallery = ""
    if p.get("gallery"):
        shots = "".join(
            f'<li><button type="button" class="gallery-item" data-full="{R}assets/img/{g}" aria-label="Open photo {n} of {len(p["gallery"])}">{img(R, g, "")}</button></li>'
            for n, g in enumerate(p["gallery"], 1)
        )
        gallery = f"""
<section class="section">
  <div class="container">
    {section_head('Gallery', 'Photos from the day')}
    <ul class="gallery" data-gallery>{shots}</ul>
  </div>
</section>"""

    cta = ""
    if p.get("cta"):
        c = p["cta"]
        second = btn(R, c["secondary"][0], c["secondary"][1], "ghost-dark", "phone") if c.get("secondary") else ""
        cta = f"""
<section class="cta-band">
  <div class="container cta-inner">
    <div><h2>{e(c['title'])}</h2><p>{e(c['text'])}</p></div>
    <div class="donate-actions">{btn(R, c['label'], c['href'], 'primary')}{second}</div>
  </div>
</section>"""

    others = [o for o in PROJECTS if o["slug"] != p["slug"] and o["kind"] == p["kind"]][:3]
    if len(others) < 3:
        others += [o for o in PROJECTS if o["slug"] != p["slug"] and o not in others][: 3 - len(others)]
    more = "".join(project_card(R, o) for o in others)

    meta = (
        f'<p class="project-meta"><span class="tag tag-{p["kind"].lower()}">{e(p["kind"])}</span>'
        f'<span>{icon("calendar")}{e(p["when"])}</span><span>{icon("pin")}{e(p["where"])}</span></p>'
    )
    hero = f"""
<section class="page-hero page-hero--project">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><ol><li><a href="{R}">Home</a></li><li><a href="{R}projects/">Projects</a></li><li aria-current="page">{e(p['title'])}</li></ol></nav>
    <h1>{e(p['title'])}</h1>
    {meta}
    <p class="lead">{e(p['excerpt'])}</p>
  </div>
  {shamrock('hero-shamrock')}
</section>
<div class="container project-cover">{img(R, p['cover'], p['title'], eager=True)}</div>"""

    body = f"""
{hero}
{''.join(sections[:1])}
{facts}
{''.join(sections[1:])}
{gallery}
{cta}
<section class="section section--cream">
  <div class="container">
    <div class="section-head-row">
      {section_head('Keep exploring', 'More projects')}
      {btn(R, 'All projects', 'projects/', 'ghost')}
    </div>
    <div class="cards">{more}</div>
  </div>
</section>
"""
    layout(f"projects/{p['slug']}/index.html", p["title"], p["excerpt"], body, active="projects/", og_image=p["cover"])


def build_get_involved() -> None:
    R = "../"
    benefits = "".join(f'<li class="feature">{icon(ic)}<h3>{e(t)}</h3><p>{e(d)}</p></li>' for ic, t, d in GET_INVOLVED_BENEFITS)
    body = f"""
{page_hero(R, 'Get Involved', [], 'Join our network, volunteer your time or support our work. There is a place for everyone at Hands 4 Unity.', 'Make a difference')}

<section class="section">
  <div class="container">
    {section_head('Why join us', 'What our network offers', center=True)}
    <ul class="features features--five">{benefits}</ul>
  </div>
</section>

<section class="section section--cream">
  <div class="container">
    {section_head('Ways to help', 'Three ways to support our community', center=True)}
    <div class="ways">
      <article class="way">
        <span class="way-icon">{icon('users')}</span>
        <h3>Volunteer</h3>
        <p>Help out at events like Taste of All Nations, or share your skills as a sewing tutor, language mentor or career mentor.</p>
        <a class="link-arrow" href="#join">Sign up below {icon('arrow-right')}</a>
      </article>
      <article class="way way--accent">
        <span class="way-icon">{icon('heart')}</span>
        <h3>Donate</h3>
        <p>We rely on the generosity of individuals. Every donation helps us run free coaching, workshops and community events.</p>
        <a class="link-arrow" href="{SITE['donate']}" target="_blank" rel="noopener">Donate on GivenGain {icon('external')}</a>
      </article>
      <article class="way">
        <span class="way-icon">{icon('globe')}</span>
        <h3>Partner with us</h3>
        <p>Community groups, businesses and public bodies can sponsor an event, host a workshop or work with us on new projects.</p>
        <a class="link-arrow" href="{R}contact-us/?subject=Partnership">Talk to us {icon('arrow-right')}</a>
      </article>
    </div>
  </div>
</section>

<section class="section" id="join">
  <div class="container form-layout">
    <div class="form-intro">
      <p class="eyebrow">Join our network</p>
      <h2>Get involved</h2>
      <p>Tell us a little about yourself and how you would like to take part. A member of our team will be in touch.</p>
      <figure class="form-photo">{img(R, 'projects/toan-2025/volunteers.jpg', 'Hands 4 Unity volunteers at Taste of All Nations 2025')}</figure>
    </div>
    <form class="form card-surface" data-form="involve" novalidate>
      <input type="hidden" name="subject" value="Get involved enquiry">
      <div class="field-row">
        <div class="field"><label for="gi-name">Full name</label><input id="gi-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="gi-email">Email</label><input id="gi-email" type="email" name="email" autocomplete="email" required></div>
      </div>
      <div class="field"><label for="gi-phone">Phone <span class="optional">(optional)</span></label><input id="gi-phone" type="tel" name="phone" autocomplete="tel"></div>
      <fieldset class="field">
        <legend>I'm interested in</legend>
        <div class="checks">
          <label class="check"><input type="checkbox" name="interest" value="Joining the network"><span>Joining the network</span></label>
          <label class="check"><input type="checkbox" name="interest" value="Volunteering"><span>Volunteering</span></label>
          <label class="check"><input type="checkbox" name="interest" value="Job seekers support"><span>Job seekers support</span></label>
          <label class="check"><input type="checkbox" name="interest" value="Partnering or sponsoring"><span>Partnering or sponsoring</span></label>
          <label class="check"><input type="checkbox" name="interest" value="The newsletter"><span>The newsletter</span></label>
        </div>
      </fieldset>
      <div class="field"><label for="gi-msg">Message <span class="optional">(optional)</span></label><textarea id="gi-msg" name="message" rows="4"></textarea></div>
      {consent_html(R)}
      {form_tail('Send')}
    </form>
  </div>
</section>
"""
    layout("get-involved/index.html", "Get Involved",
           "Volunteer, join our network, partner with us or donate. Find out how you can get involved with Hands 4 Unity in Drogheda.",
           body, active="get-involved/", og_image="projects/toan-2025/volunteers.jpg")


def build_contact() -> None:
    R = "../"
    body = f"""
{page_hero(R, 'Contact Us', [], 'We would love to hear from you. Get in touch by phone, email or the form below.', 'Get in touch')}

<section class="section section--tight">
  <div class="container contact-cards">
    <a class="contact-card" href="{SITE['maps']}" target="_blank" rel="noopener">{icon('pin')}<h2>Address</h2><p>{address_html()}</p><span class="link-arrow">Open in Google Maps {icon('external')}</span></a>
    <a class="contact-card" href="tel:{SITE['phone_tel']}">{icon('phone')}<h2>Phone</h2><p>{SITE['phone_display']}</p><span class="link-arrow">Call us {icon('arrow-right')}</span></a>
    <a class="contact-card" href="mailto:{SITE['email']}">{icon('mail')}<h2>Email</h2><p>{SITE['email']}</p><span class="link-arrow">Send an email {icon('arrow-right')}</span></a>
  </div>
</section>

<section class="section">
  <div class="container form-layout">
    <div class="form-intro">
      <p class="eyebrow">Contact form</p>
      <h2>Send us a message</h2>
      <p>Whether you want to book a coaching session, join a workshop, volunteer or partner with us, send us a message and we'll get back to you.</p>
      <div class="find-us">
        <h3>Find us</h3>
        <p>We are based at The Mill Enterprise Hub in Greenhills, Drogheda. Our workshops take place at the Barbican Centre, William Street, Drogheda.</p>
        {socials()}
      </div>
    </div>
    <form class="form card-surface" data-form="contact" novalidate>
      <div class="field-row">
        <div class="field"><label for="c-name">Full name</label><input id="c-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="c-email">Email</label><input id="c-email" type="email" name="email" autocomplete="email" required></div>
      </div>
      <div class="field-row">
        <div class="field"><label for="c-phone">Phone <span class="optional">(optional)</span></label><input id="c-phone" type="tel" name="phone" autocomplete="tel"></div>
        <div class="field"><label for="c-subject">Subject</label><input id="c-subject" name="subject" required></div>
      </div>
      <div class="field"><label for="c-msg">Message</label><textarea id="c-msg" name="message" rows="6" required></textarea></div>
      {consent_html(R)}
      {form_tail('Send message')}
    </form>
  </div>
</section>
"""
    layout("contact-us/index.html", "Contact Us",
           "Contact Hands 4 Unity at The Mill Enterprise Hub, Drogheda. Call +353 87 003 0568 or email info@hands4unity.org.",
           body, active="contact-us/")


def build_financial() -> None:
    R = "../"
    rows = "".join(f"<tr><th scope=\"row\">{e(a)}</th><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in FINANCIALS_2022)
    body = f"""
{page_hero(R, 'Financial Information', [], 'We are committed to being open about how we are funded and how we use our resources.', 'Transparency')}
<section class="section">
  <div class="container split split--top">
    <div class="prose">
      <h2>About the organisation</h2>
      <p>{SITE['legal']} is a company limited by guarantee, registered in Ireland. Its main object is to provide a support network for women in our community, and to help with education, health and issues in their families.</p>
      <dl class="org-facts">
        <div><dt>Legal name</dt><dd>Hands 4 Unity Company Limited by Guarantee</dd></div>
        <div><dt>Company number</dt><dd>{SITE['company_no']}</dd></div>
        <div><dt>Registered office</dt><dd>{address_html(', ')}</dd></div>
      </dl>
    </div>
    <div>
      <div class="card-surface">
        <h2 class="h3">Annual Report 2022</h2>
        <p class="muted">Directors' report and financial statements for the year ended 31 December 2022.</p>
        <table class="fin-table">
          <thead><tr><th scope="col">Summary</th><th scope="col">2022</th><th scope="col">2021</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        <a class="btn btn-primary" href="{R}assets/docs/H4U-Annual-Report-2022.pdf" download><span>Download report (PDF)</span>{icon('download')}</a>
      </div>
    </div>
  </div>
</section>
"""
    layout("financial-information/index.html", "Financial Information",
           "Annual reports and financial statements for Hands 4 Unity CLG.", body)


def build_privacy() -> None:
    R = "../"
    body = f"""
{page_hero(R, 'Privacy Policy', [], 'How we collect, use and protect your personal information.')}
<section class="section">
  <div class="container prose prose--page">
    <p class="muted">Last updated: {_dt.date.today().strftime('%-d %B %Y')}</p>
    <p>This policy explains how {SITE['legal']} ("we", "us") collects and uses your personal data when you use this website or contact us, and the rights you have under the General Data Protection Regulation (GDPR) and the Data Protection Acts 1988 to 2018.</p>

    <h2>Who we are</h2>
    <p>The data controller is {SITE['legal']}, {address_html(', ')}. You can contact us about this policy at <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>

    <h2>What we collect</h2>
    <p>We only collect the personal data you choose to give us, for example when you send a message through our contact or get involved forms, sign up to our newsletter, email or phone us. This may include:</p>
    <ul>
      <li>Your name</li>
      <li>Your email address</li>
      <li>Your phone number</li>
      <li>Anything you tell us in your message, such as the support you are looking for or how you would like to get involved</li>
    </ul>
    <p>To understand how many people visit our website, we use Cloudflare Web Analytics. It counts page visits without cookies and without identifying you, and it does not track you across other websites. We do not use advertising trackers.</p>

    <h2>How we use your data</h2>
    <ul>
      <li>To respond to your enquiry and provide the support you have asked for.</li>
      <li>To arrange coaching appointments, workshops and events you sign up for.</li>
      <li>To send you our newsletter, if you have asked to receive it. You can unsubscribe at any time.</li>
      <li>To meet our legal obligations.</li>
    </ul>
    <p>We rely on your consent, which you give when you submit a form, and on our legitimate interest in responding to people who contact us. We never sell your personal data.</p>

    <h2>Who we share it with</h2>
    <p>We only share your data with service providers who help us run our work, and only as far as needed. When you send a form on this website, your details are stored in our Google Workspace account (Google Sheets and Gmail), which Google runs on our behalf. We may disclose data where the law requires it, for example in response to a valid request from a public authority.</p>
    <p>This website loads fonts from Google Fonts, which means your browser connects to Google's servers and shares your IP address with them. Our Donate button takes you to GivenGain, which has its own privacy policy.</p>

    <h2>How long we keep it</h2>
    <p>We keep your personal data only for as long as we need it for the purpose you gave it to us, or as long as the law requires. Enquiries are normally deleted within two years of our last contact with you.</p>

    <h2>Your rights</h2>
    <p>You have the right to access, correct or delete the personal data we hold about you, to restrict or object to how we use it, to data portability, and to withdraw your consent at any time. To make a request, email <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>
    <p>If you are unhappy with how we have handled your data, you can complain to the Data Protection Commission at <a href="https://www.dataprotection.ie" target="_blank" rel="noopener">dataprotection.ie</a>.</p>

    <h2>Children's privacy</h2>
    <p>Our website is not aimed at children under 13 and we do not knowingly collect their data online. Bookings for children's programmes such as Kids Can Code are made by a parent or guardian. If you believe a child has given us personal data, please contact us and we will remove it.</p>

    <h2>Links to other websites</h2>
    <p>Our website links to other sites that we do not operate. We are not responsible for their content or privacy practices, and we encourage you to read their privacy policies.</p>

    <h2>Changes to this policy</h2>
    <p>We may update this policy from time to time. Changes take effect when they are posted on this page.</p>
  </div>
</section>
"""
    layout("privacy-policy/index.html", "Privacy Policy", "How Hands 4 Unity collects, uses and protects your personal information.", body)


def build_cookies() -> None:
    R = "../"
    body = f"""
{page_hero(R, 'Cookies Policy', [], 'What cookies are and how this website uses them.')}
<section class="section">
  <div class="container prose prose--page">
    <p class="muted">Last updated: {_dt.date.today().strftime('%-d %B %Y')}</p>
    <h2>What are cookies?</h2>
    <p>Cookies are small text files that websites place on your device to remember information about your visit.</p>

    <h2>How we use cookies</h2>
    <p>This website does not set any cookies, and it does not use advertising or social media tracking. That is why you will not see a cookie banner here.</p>

    <h2>Third-party services</h2>
    <p>Some pages connect to services run by other organisations:</p>
    <ul>
      <li><strong>Cloudflare Web Analytics</strong> counts how many people visit our pages. It does not use cookies and does not identify individual visitors.</li>
      <li><strong>Google Fonts</strong> provides the typefaces used on this site. Your browser requests the fonts from Google's servers. Google Fonts does not set cookies.</li>
      <li><strong>GivenGain</strong>, <strong>Eventbrite</strong>, <strong>Google Maps</strong> and our social media pages may set their own cookies when you follow a link to them. Their own cookie policies apply.</li>
    </ul>

    <h2>Managing cookies</h2>
    <p>You can block or delete cookies at any time in your browser settings.</p>

    <h2>Questions</h2>
    <p>If you have any questions about this policy, email <a href="mailto:{SITE['email']}">{SITE['email']}</a>. You can read more about how we handle personal data in our <a href="{R}privacy-policy/">Privacy Policy</a>.</p>
  </div>
</section>
"""
    layout("cookies-policy/index.html", "Cookies Policy", "How the Hands 4 Unity website uses cookies.", body)


def build_404() -> None:
    # Served at any missing URL, so it uses absolute paths.
    R = "/"
    body = f"""
<section class="page-hero page-hero--center">
  <div class="container">
    <p class="eyebrow">Error 404</p>
    <h1>We can't find that page</h1>
    <p class="lead">The page may have moved when we rebuilt our website.</p>
    <div class="hero-actions hero-actions--center">{btn(R, 'Go to the homepage', '/')}{btn(R, 'See our projects', '/projects/', 'ghost', None)}</div>
  </div>
  {shamrock('hero-shamrock')}
</section>
"""
    layout("404.html", "Page not found", "This page could not be found.", body)
    # layout() computes a relative prefix; rewrite to absolute for the 404 page.
    p = ROOT / "404.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace('href="./"', 'href="/"').replace('href="css/', 'href="/css/').replace('src="js/', 'src="/js/')
    t = t.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    for h, _ in NAV[1:]:
        t = t.replace(f'href="{h}"', f'href="/{h}"')
    for h in ("privacy-policy/", "cookies-policy/", "financial-information/"):
        t = t.replace(f'href="{h}"', f'href="/{h}"')
    t = t.replace('href="//', 'href="/')
    p.write_text(t, encoding="utf-8")


def build_meta_files() -> None:
    today = _dt.date.today().isoformat()
    urls = [p for p in _written if p.endswith("index.html")]
    entries = "".join(
        f"  <url><loc>{SITE['url']}/{u[: -len('index.html')]}</loc><lastmod>{today}</lastmod></url>\n" for u in sorted(urls)
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n',
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n", encoding="utf-8")


def build_admin_redirect() -> None:
    # /admin forwards to the dashboard, passing on ?open=... from the notification emails.
    # Kept out of the sitemap and search results.
    out = ROOT / "admin" / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(
        f"""<!doctype html>
<html lang="en-IE">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex">
  <title>Hands 4 Unity dashboard</title>
  <meta http-equiv="refresh" content="1; url={ADMIN_DASHBOARD_URL}">
  <script>location.replace("{ADMIN_DASHBOARD_URL}" + location.search);</script>
</head>
<body>
  <p><a href="{ADMIN_DASHBOARD_URL}">Open the Hands 4 Unity dashboard</a></p>
</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    os.chdir(ROOT)
    build_home()
    build_about()
    build_projects_index()
    for p in PROJECTS:
        build_project(p)
    build_get_involved()
    build_contact()
    build_financial()
    build_privacy()
    build_cookies()
    build_404()
    build_admin_redirect()
    build_meta_files()
    print(f"Built {len(_written)} pages into {ROOT}")


if __name__ == "__main__":
    main()
