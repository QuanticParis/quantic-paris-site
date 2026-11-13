#!/usr/bin/env python3
"""Generate samuel.html from Samuel Deléglise's CV data files (Google Drive, CV/data/).

Usage: python3 tools/build_samuel.py [path/to/CV/data]
Re-run after updating the CV data; the page is fully regenerated.
Sources used: identity, grants, supervision, valorisation, teaching,
presentations, publications, distinctions. responsibilities.md is
confidential and never read.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / (
    "Library/CloudStorage/GoogleDrive-samuel.deleglise.2002@polytechnique.org/Mon Drive/CV/data")

SCHOLAR = "https://scholar.google.com/citations?user=zb_xnPMAAAAJ"
ARXIV = "https://arxiv.org/search/?searchtype=author&query=Del%C3%A9glise%2C+S"
LKB = "https://www.lkb.fr/optomechanics/people/samuel-deleglise/"
EMAIL_DISPLAY = "samuel.deleglise [at] cnrs.fr"

e = html.escape


def parse_blocks(text):
    """Parse '- key: value' YAML-ish entries, keeping the current ## / ### headings."""
    items, cur, h2, h3 = [], None, None, None
    for line in text.splitlines():
        if line.startswith("## "):
            h2, h3 = line[3:].strip(), None
            continue
        if line.startswith("### "):
            h3 = line[4:].strip()
            continue
        m = re.match(r"^- (\w+): ?(.*)$", line)
        if m:
            cur = {"_h2": h2, "_h3": h3, m.group(1): m.group(2).strip()}
            items.append(cur)
            continue
        m = re.match(r"^  (\w+): ?(.*)$", line)
        if m and cur is not None:
            cur[m.group(1)] = m.group(2).strip()
    return items


def load(name):
    return parse_blocks((DATA / f"{name}.md").read_text(encoding="utf-8"))


def year_of(item):
    for k in ("date", "period", "year"):
        if k in item:
            m = re.findall(r"(\d{4})", item[k])
            if m:
                return int(m[-1]) if k == "date" else int(m[0])
    return 0


# ---------------------------------------------------------------- data
identity = load("identity")
grants = load("grants")
supervision = load("supervision")
valor = load("valorisation")
teaching = load("teaching")
talks = load("presentations")
pubs = load("publications")
distinctions = load("distinctions")

own_pubs = [p for p in pubs if p["_h2"] and "hors grandes" in p["_h2"]]
collab_pubs = [p for p in pubs if p["_h2"] and "grandes collaborations" in p["_h2"]]
pub_text = (DATA / "publications.md").read_text(encoding="utf-8")
m = re.search(r"h-index[^:]*:\s*(\d+)", pub_text)
h_index = m.group(1) if m else None

phds = [s for s in supervision if s.get("type") == "phd" and int(s.get("supervision_level", "0")) >= 3]
postdocs = [s for s in supervision if s.get("type") == "postdoc"]
invited_all = [t for t in talks if t.get("type") == "invited" and t["_h2"] and "invités" in t["_h2"]]
invited = [t for t in invited_all if t.get("status") != "upcoming"]
upcoming = [t for t in invited_all if t.get("status") == "upcoming"]
INVITED_SINCE = 2016
invited_recent = [t for t in invited if year_of(t) >= INVITED_SINCE]

FR_EN = {
    "Séminaire": "Seminar", "Congrès général de la Société Française d'Optique": "General congress of the Société Française d'Optique",
    "Symposium des 40 ans de l'optique quantique": "Symposium '40 years of quantum optics'",
    "GDR de physique mésoscopique": "GDR Mesoscopic Physics", "Kick-off du CNRS/UArizona IRC": "CNRS / U. Arizona IRC kick-off",
    "Congrès annuel de la Société Française de Physique": "Annual congress of the Société Française de Physique",
    "Congrès National de la Société Française de Physique": "National congress of the Société Française de Physique",
    "Espagne": "Spain", "Autriche": "Austria", "Suisse": "Switzerland", "Allemagne": "Germany", "Italie": "Italy", "États-Unis": "USA",
}


def tr(s):
    for k, v in FR_EN.items():
        s = s.replace(k, v)
    return s


# ---------------------------------------------------------------- sections
def hero():
    stats = [
        (str(len(own_pubs)), "publications<br>(+ Virgo collaboration)"),
        (h_index or "–", "h-index<br>(excl. Virgo)"),
        (str(len(phds)), "PhD students<br>supervised"),
        (str(len(invited)), "invited talks"),
    ]
    stat_html = "".join(f'<div class="sd-stat"><b>{v}</b><span>{l}</span></div>' for v, l in stats)
    return f'''
<header class="sd-hero">
  <div class="sd-hero-inner">
    <img class="sd-photo" src="images/samuel.jpg" alt="Portrait of Samuel Deléglise">
    <div>
      <h1>Samuel Deléglise</h1>
      <p class="sd-role">CNRS researcher &middot; QUANTIC team, Laboratoire de Physique de l'ENS, Paris</p>
      <p class="sd-tagline">Hybrid quantum systems: macroscopic mechanical resonators driven into the quantum regime by superconducting circuits.</p>
      <div class="sd-links">
        <span class="sd-chip">✉ {EMAIL_DISPLAY}</span>
        <a class="sd-chip sd-chip-strong" href="files/Samuel_Deleglise_CV.pdf">⬇ CV (PDF)</a>
        <a class="sd-chip" href="{SCHOLAR}">Google Scholar</a>
        <a class="sd-chip" href="{ARXIV}">arXiv</a>
        <a class="sd-chip" href="https://github.com/pyrpl-fpga/pyrpl">PyRPL</a>
      </div>
    </div>
  </div>
</header>'''


NAV = [("research", "Research"), ("career", "Career"), ("grants", "Grants"), ("team", "Supervision"),
       ("talks", "Invited talks"), ("teaching", "Teaching"), ("ip", "Patents & software"), ("publications", "Publications")]


def nav():
    return '<nav class="sd-nav">' + "".join(f'<a href="#{a}">{l}</a>' for a, l in NAV) + "</nav>"


def research():
    return '''
<section id="research">
  <h2>Research</h2>
  <p>Mechanical resonators can now be fabricated with quality factors above a billion and lifetimes of seconds. I couple such
  massive, ultra-coherent oscillators to superconducting qubits in order to prepare, control and measure their quantum states,
  with applications to quantum sensing, quantum memories and fundamental tests of quantum mechanics with massive objects.</p>
  <figure class="sd-banner">
    <img src="images/samuel/mecaflux_render.jpg" alt="3D rendering of the MecaFlux device: a metallized membrane chip flipped over a fluxonium circuit">
    <figcaption><b>MecaFlux.</b> A suspended Si<sub>3</sub>N<sub>4</sub> membrane chip is flip-chipped above a superconducting
    “heavy” fluxonium; the membrane motion modulates the qubit charge, enabling resonant qubit–phonon exchange
    (<a href="https://arxiv.org/abs/2505.21481">arXiv:2505.21481</a>).</figcaption>
  </figure>
  <div class="sd-figs">
    <figure>
      <img src="images/samuel/chip_false_color.jpg" alt="False-color optical micrograph of the fluxonium chip">
      <figcaption><b>The circuit.</b> False-color micrograph of the fluxonium chip: superinductance, junction, coupling electrodes and readout.</figcaption>
    </figure>
    <figure>
      <img src="images/samuel/membrane_coin.jpg" alt="Silicon nitride membrane chip next to a one-cent coin">
      <figcaption><b>The mechanics.</b> Phononic-crystal Si<sub>3</sub>N<sub>4</sub> membranes on a silicon chip, next to a 1-cent coin.</figcaption>
    </figure>
  </div>
  <div class="sd-cards">
    <div class="sd-card"><h3>Hybrid circuits</h3><p>Fluxonium and high-impedance circuits coupled to ultra-coherent membranes and drums.</p></div>
    <div class="sd-card"><h3>Quantum sensing</h3><p>AC-charge detection, rf-to-microwave transduction, microwave photon counting.</p></div>
    <div class="sd-card"><h3>Bosonic codes</h3><p>Dissipative stabilization, squeezed cat qubits, mechanical modes as quantum memories.</p></div>
    <div class="sd-card"><h3>Fundamental tests</h3><p>Massive quantum oscillators to probe gravity-related wavefunction collapse.</p></div>
  </div>
</section>'''


def career():
    rows = [
        ("2026 –", "CNRS researcher, QUANTIC team", "Laboratoire de Physique de l'ENS, Paris"),
        ("2012 – 2025", "CNRS researcher, Optomechanics & Quantum Measurements group",
         "Laboratoire Kastler Brossel, Paris &mdash; quantum optomechanics, hybrid qubit–mechanics platform; member of the Virgo collaboration"),
        ("2009 – 2012", "Marie Curie postdoctoral fellow", "EPFL, Lausanne &mdash; group of Tobias Kippenberg, optomechanics with microresonators"),
        ("2006 – 2009", "PhD in physics", "Laboratoire Kastler Brossel (ENS / UPMC) &mdash; advisor Serge Haroche. "
         "<i>Reconstruction of non-classical field states in cavity quantum electrodynamics</i>"),
        ("2005 – 2006", "Master in quantum physics", "École Normale Supérieure, Paris"),
        ("2002 – 2005", "Engineering degree", "École Polytechnique"),
    ]
    items = "".join(f'<li><span class="sd-when">{w}</span><div><b>{t}</b><br><span class="sd-muted">{d}</span></div></li>' for w, t, d in rows)
    aw = "".join(f'<li><b>{e(a["name"])}</b> ({a.get("year","")}){" &mdash; " + e(a["funder"]) if a.get("funder") else ""}'
                 f'{" &mdash; awarded to the LIGO–Virgo collaboration" if "LIGO" in a.get("awarded_to","") else ""}</li>'
                 for a in distinctions)
    aw = aw.replace("Prix Gustave Ribaud", "Gustave Ribaud Prize").replace("Académie des sciences", "French Academy of Sciences")
    return f'''
<section id="career">
  <h2>Career</h2>
  <ul class="sd-timeline">{items}</ul>
  <h3 class="sd-sub">Distinctions</h3>
  <ul class="sd-list">{aw}</ul>
</section>'''


def grants_sec():
    role_en = {"coordinateur principal": "PI", "partenaire": "partner"}
    cards = []
    for g in grants:
        role = g.get("role", "")
        role = next((v for k, v in role_en.items() if role.startswith(k)), role)
        amount = g.get("amount_total") or g.get("amount_lkb") or ""
        amount = amount.replace(" 000 €", " k€").replace("000 €", "k€")
        active = g.get("status") == "active"
        funder = g.get("funder", "").replace("Émergences Sorbonne Université", "Sorbonne Université")
        gtype = g.get("type", "").replace("programme mi-lourd", "equipment programme")
        name = g["name"].replace("Plateforme cryogénique pour les technologies quantiques", "Cryogenic platform for quantum technologies")
        cards.append(f'''<div class="sd-card{' sd-active' if active else ''}">
  <div class="sd-card-top"><span class="sd-tag">{e(g.get("acronym",""))}</span><span class="sd-muted">{g.get("period","").replace("--"," – ")}</span></div>
  <h3>{e(name)}</h3>
  <p class="sd-muted">{e(funder)} {e(gtype)} &middot; {e(role)}{" &middot; " + e(amount) if amount else ""}</p></div>''')
    return f'<section id="grants"><h2>Grants <small>(since 2014)</small></h2><div class="sd-cards sd-cards-3">{"".join(cards)}</div></section>'


def team():
    rows = []
    for s in phds:
        period = s.get("period", "").replace("--", " – ")
        title = s.get("thesis_title", "")
        prize = s.get("prize", "")
        prize = (prize.replace("Lauréat du prix de thèse de la Société française d'optique (SFO)", "SFO PhD thesis prize")
                 .replace("Premier accessit du prix de thèse Dylan Cattiaux", "Dylan Cattiaux PhD prize, first runner-up"))
        link = s.get("hal")
        t = f'<a href="{link}">{e(title)}</a>' if link and title else e(title)
        cur = s.get("status") == "ongoing"
        co = s.get("co_supervisor")
        cifre = " &middot; CIFRE with Alice &amp; Bob" if "CIFRE" in s.get("notes", "") else ""
        rows.append(f'<li><span class="sd-when">{period}</span><div><b>{e(s["name"])}</b>'
                    f'{" <span class=sd-tag>ongoing</span>" if cur else ""}'
                    f'{"<br><span class=sd-muted>co-supervised with " + e(co) + cifre + "</span>" if co else ""}'
                    f'{"<br><span class=sd-muted>" + t + "</span>" if title else ""}'
                    f'{"<br><span class=sd-prize>🏆 " + e(prize) + "</span>" if prize else ""}</div></li>')
    pd = ", ".join(f'{e(p["name"])} ({p.get("period","").replace("--"," – ")})' for p in postdocs)
    return f'''
<section id="team">
  <h2>Supervision</h2>
  <h3 class="sd-sub">PhD students</h3>
  <ul class="sd-timeline">{"".join(rows)}</ul>
  <h3 class="sd-sub">Postdocs</h3><p>{pd}</p>
</section>'''


def talks_sec():
    rows = []
    def ym(t):
        mm = re.match(r"(\d{2})/(\d{4})", t.get("date", ""))
        return (int(mm.group(2)), int(mm.group(1))) if mm else (year_of(t), 0)
    for t in sorted(upcoming + invited_recent, key=lambda t: ym(t), reverse=True):
        d = t.get("date", "")
        title = t.get("title", "")
        title = "" if title.startswith("(") else title
        badge = ' <span class="sd-tag">upcoming</span>' if t.get("status") == "upcoming" else ""
        rows.append(f'<li><span class="sd-when">{d}</span><div><b>{e(tr(t.get("event","")))}</b>, {e(tr(t.get("location","")))}{badge}'
                    + (f'<br><span class="sd-muted">{e(title)}</span>' if title else "") + '</div></li>')
    return f'''<section id="talks"><h2>Invited talks <small>(since {INVITED_SINCE}; {len(invited)} in total)</small></h2>
<ul class="sd-timeline sd-compact">{"".join(rows)}</ul></section>'''


def teaching_sec():
    rows = [
        ("2017 – 2024", "<b>Quantum Machines</b> &mdash; quantum physics with electrical circuits and mechanical resonators, M2 ICFP, ENS Paris"),
        ("2016 – 2017", "<b>Quantum optomechanics and nanomechanics</b>, M2 ICFP, ENS Paris"),
        ("2024", "<b>From gravitational-wave detection to quantum optomechanics</b>, Mesoscopic physics school, Cargèse"),
        ("2022", "<b>The New Mechanics</b>, Les Houches school of physics"),
        ("2019 – 2020", "<b>Optomechanics MOOC</b>, European OMT network"),
        ("2017 – 2018", "<b>Introductory quantum physics SPOC</b> (L3), Sorbonne Université"),
        ("2016 – 2020", "<b>Python programming projects</b>, M2 LUMI, Sorbonne Université"),
    ]
    items = "".join(f'<li><span class="sd-when">{w}</span><div>{t}</div></li>' for w, t in rows)
    return f'<section id="teaching"><h2>Teaching</h2><ul class="sd-timeline sd-compact">{items}</ul></section>'


def ip_sec():
    pats = [v for v in valor if v.get("reference") and v.get("role") == "inventeur"]
    soft = [v for v in valor if v.get("url")]
    p = "".join(f'<div class="sd-card"><div class="sd-card-top"><span class="sd-tag">Patent</span><span class="sd-muted">{e(x["reference"])}</span></div>'
                f'<h3>{e(x["title"])}</h3><p class="sd-muted">{e(x.get("inventors",""))}</p></div>' for x in pats)
    s = "".join(f'<div class="sd-card"><div class="sd-card-top"><span class="sd-tag">Open source</span></div>'
                f'<h3><a href="{x["url"]}">{e(x["name"])}</a></h3><p class="sd-muted">FPGA-based digital feedback control for quantum-optics '
                f'experiments on the Red Pitaya board. {e(x.get("publication",""))}</p></div>' for x in soft)
    return f'<section id="ip"><h2>Patents &amp; software</h2><div class="sd-cards sd-cards-2">{p}{s}</div></section>'


def fmt_authors(a):
    names = [n.strip() for n in a.split(";") if n.strip()]
    out = []
    for n in names:
        parts = n.split()
        short = " ".join([p[0] + "." if not p.endswith(".") else p for p in parts[:-1]] + parts[-1:]) if len(parts) > 1 else n
        if "Del" in n and "glise" in n:
            short = "<b>S. Deléglise</b>"
        out.append(short)
    if len(out) > 12:
        idx = next((i for i, x in enumerate(out) if "Deléglise" in x), None)
        head = out[:3]
        tail = ["…", out[idx]] if idx is not None and idx >= 3 else []
        out = head + tail + ["et al."]
    return ", ".join(out)


def pubs_sec():
    by_year = {}
    for p in own_pubs:
        by_year.setdefault(p["_h3"], []).append(p)
    blocks = []
    for y in sorted(by_year, reverse=True):
        lis = []
        for p in by_year[y]:
            j = p.get("journal", "")
            j = "" if j in ("UNDEFINED", "") else j
            links = []
            if p.get("doi") and "arXiv" not in p["doi"]:
                links.append(f'<a href="{p["doi"]}">{e(j) or "DOI"}</a>')
            elif j:
                links.append(e(j))
            else:
                links.append("Preprint")
            if p.get("arxiv"):
                links.append(f'<a href="{p["arxiv"].replace("/pdf/", "/abs/")}">arXiv</a>')
            lis.append(f'<li><span class="sd-ptitle">{e(p["title"])}</span><br>'
                       f'<span class="sd-muted">{fmt_authors(p.get("authors",""))}</span> &middot; {" &middot; ".join(links)}</li>')
        blocks.append(f'<h3 class="sd-year">{y}</h3><ul class="sd-pubs">{"".join(lis)}</ul>')
    return f'''<section id="publications"><h2>Publications</h2>
<p class="sd-muted">{len(own_pubs)} articles excluding large collaborations, plus {len(collab_pubs)} papers as a member of the Virgo collaboration
(first detections of gravitational waves). Citation data: <a href="{SCHOLAR}">Google Scholar</a>.</p>
{"".join(blocks)}</section>'''


CSS = '''
<style>
:root{--sd-accent:#2a6f97;--sd-accent2:#7b4fa3;--sd-ink:#1d2433;--sd-muted:#5b6475;--sd-card:#ffffff;--sd-line:#dfe4ec;--sd-bg:#f6f8fb}
body{background:var(--sd-bg)}
.sd-wrap{max-width:1040px;margin:0 auto;padding:0 16px 48px;color:var(--sd-ink);font-size:16px;line-height:1.55}
.sd-wrap a{color:var(--sd-accent);text-decoration:none}.sd-wrap a:hover{text-decoration:underline}
.sd-hero{margin:24px 0 8px;padding:32px;border-radius:20px;color:#fff;background:linear-gradient(120deg,#1f4e79 0%,#2a6f97 45%,#7b4fa3 100%);box-shadow:0 10px 30px rgba(31,78,121,.25)}
.sd-hero-inner{display:flex;gap:28px;align-items:center;flex-wrap:wrap}
.sd-photo{width:168px;height:168px;border-radius:50%;object-fit:cover;border:4px solid rgba(255,255,255,.85)}
.sd-hero h1{margin:0;font-size:2.4rem;font-weight:700;color:#fff}
.sd-role{margin:.2rem 0;font-size:1.05rem;opacity:.95}
.sd-tagline{margin:.6rem 0 1rem;max-width:620px;opacity:.9}
.sd-links{display:flex;gap:8px;flex-wrap:wrap}
.sd-chip{display:inline-block;padding:4px 12px;border-radius:999px;background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.35);color:#fff!important;font-size:.9rem}
a.sd-chip-strong{background:#fff;color:#1f4e79!important;font-weight:600}
a.sd-chip:hover{background:rgba(255,255,255,.3);text-decoration:none!important}
.sd-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:28px}
.sd-stat{background:rgba(255,255,255,.12);border-radius:14px;padding:12px;text-align:center}
.sd-stat b{display:block;font-size:1.9rem;line-height:1.1}.sd-stat span{font-size:.8rem;opacity:.9}
.sd-nav{position:sticky;top:0;z-index:10;display:flex;gap:4px;flex-wrap:wrap;padding:10px 0;margin-bottom:8px;background:var(--sd-bg);border-bottom:1px solid var(--sd-line)}
.sd-nav a{padding:4px 12px;border-radius:999px;color:var(--sd-ink)!important;font-size:.92rem}
.sd-nav a:hover{background:#e6edf5;text-decoration:none!important}
.sd-wrap section{padding-top:28px;scroll-margin-top:56px}
.sd-wrap h2{font-size:1.6rem;font-weight:700;margin-bottom:14px;padding-left:12px;border-left:5px solid var(--sd-accent)}
.sd-wrap h2 small{font-size:.9rem;font-weight:400;color:var(--sd-muted)}
.sd-sub{font-size:1.15rem;font-weight:600;margin:22px 0 10px}
.sd-muted{color:var(--sd-muted)}
.sd-figs{display:grid;grid-template-columns:1.5fr 1fr;gap:18px;margin:18px 0}
.sd-banner{margin:18px 0 0;background:var(--sd-card);border-radius:16px;padding:10px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.sd-banner img{width:100%;border-radius:12px;display:block}
.sd-banner figcaption{font-size:.88rem;color:var(--sd-muted);margin:8px 4px 2px}
.sd-figs figure{margin:0;background:var(--sd-card);border-radius:16px;padding:14px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
.sd-figs img{width:100%;border-radius:10px}
.sd-figs figcaption{font-size:.88rem;color:var(--sd-muted);margin-top:8px}
.sd-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.sd-cards-3{grid-template-columns:repeat(3,1fr)}.sd-cards-2{grid-template-columns:repeat(2,1fr)}
.sd-card{background:var(--sd-card);border-radius:14px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,.06);border-top:4px solid var(--sd-line)}
.sd-card h3{font-size:1.02rem;font-weight:650;margin:.4rem 0}
.sd-card p{margin:0;font-size:.9rem}
.sd-active{border-top-color:var(--sd-accent2)}
.sd-card-top{display:flex;justify-content:space-between;align-items:center;font-size:.85rem}
.sd-tag{display:inline-block;padding:1px 9px;border-radius:999px;background:#e9e1f3;color:var(--sd-accent2);font-weight:600;font-size:.78rem}
.sd-timeline{list-style:none;padding:0;margin:0;border-left:2px solid var(--sd-line);margin-left:6px}
.sd-timeline li{position:relative;display:grid;grid-template-columns:120px 1fr;gap:16px;padding:8px 0 10px 18px}
.sd-timeline li:before{content:"";position:absolute;left:-7px;top:15px;width:12px;height:12px;border-radius:50%;background:var(--sd-accent);border:2px solid var(--sd-bg)}
.sd-compact li{padding:4px 0 6px 18px}
.sd-when{color:var(--sd-accent);font-weight:600;font-variant-numeric:tabular-nums;white-space:nowrap}
.sd-prize{font-size:.9rem;color:#8a5a00}
.sd-list{padding-left:20px}
.sd-year{font-size:1.1rem;font-weight:700;color:var(--sd-accent);margin:18px 0 6px}
.sd-pubs{list-style:none;padding:0;margin:0}
.sd-pubs li{padding:8px 12px;margin-bottom:6px;background:var(--sd-card);border-radius:10px;font-size:.93rem}
.sd-ptitle{font-weight:600}
@media (max-width:820px){.sd-cards,.sd-cards-3{grid-template-columns:1fr 1fr}.sd-figs{grid-template-columns:1fr}.sd-stats{grid-template-columns:1fr 1fr}}
@media (max-width:520px){.sd-cards,.sd-cards-3,.sd-cards-2{grid-template-columns:1fr}.sd-timeline li{grid-template-columns:1fr;gap:2px}.sd-hero{padding:20px}.sd-hero h1{font-size:1.9rem}}
</style>'''


def main():
    people = (ROOT / "people.html").read_text(encoding="utf-8")
    head = people[: people.index('<div class="list">')]
    head = head.replace("<title>Quantic - People</title>", "<title>Samuel Deléglise – Quantic</title>")
    head = head.replace("</head>", CSS + "\n    </head>")
    foot = people[people.index("<footer"):]
    # personal page: drop the team-funders logo block, keep addresses
    foot = re.sub(r'<h6 class="text-uppercase font-weight-bold">Made possible by</h6>.*?(?=<div class="row" style="margin-top)',
                  "", foot, flags=re.S)
    body = ('<div class="sd-wrap">' + hero() + nav() + research() + career() + grants_sec() + team()
            + talks_sec() + teaching_sec() + ip_sec() + pubs_sec() + "</div>\n\n        ")
    (ROOT / "samuel.html").write_text(head + body + foot, encoding="utf-8")
    print(f"samuel.html: {len(own_pubs)} pubs, {len(collab_pubs)} collab, {len(phds)} PhDs, {len(invited_recent)}/{len(invited)} invited talks")


if __name__ == "__main__":
    main()
