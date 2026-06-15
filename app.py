"""
ReLoop — keep it in the loop
Pure-Python Streamlit app. Minimalist green/white redesign.
Run:   pip install streamlit  &&  streamlit run app.py
Host:  push to GitHub, deploy on https://share.streamlit.io
"""

import os
import base64
import streamlit as st

st.set_page_config(page_title="ReLoop — keep it in the loop",
                   page_icon="🌱", layout="wide")

# Real photos: drop files named <category>.jpg in an "images/" folder
# (e.g. images/clothes.jpg). If a file is missing, a clean drawn icon
# is shown instead, so the app always works.
def cat_image_path(cid):
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", cid + ext)
        if os.path.exists(p):
            return p
    return None

def slug_image_path(slug):
    """Per-item photo, e.g. images/clothes_toddler.jpg. Falls back if missing."""
    if not slug:
        return None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", slug + ext)
        if os.path.exists(p):
            return p
    return None

COND_COLOR = {
    "Like new": "#0f7d44", "Good": "#169d57", "Good, fully usable": "#169d57",
    "Clean & sorted": "#0f7d44", "Worn but works": "#c98a16", "Mixed": "#c98a16",
}
def cond_badge(c):
    if not c:
        return ""
    color = COND_COLOR.get(c, "#5d6b63")
    return (f"<span style='display:inline-block;font-size:11px;font-weight:700;"
            f"padding:2px 9px;border-radius:999px;color:#fff;background:{color}'>{c}</span>")

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------
LANES = {
    "reuse": {"label": "Reuse", "cats": [
        ("clothes",   "Clothes & footwear", "Lots & bundles", "Outgrown lots, age-banded — for families, resellers & NGOs."),
        ("toys",      "Toys & games",       "Bulk buyers",    "Bundles for daycares, NGOs & event hosts."),
        ("furniture", "Furniture",          "Single or lots", "Usable or restore-able — for homes & refurbishers."),
        ("books",     "Books & stationery", "Lots",           "Bundles for schools, libraries & NGOs."),
        ("kitchen",   "Kitchen & household","Reuse",          "Utensils, jars, containers still going strong."),
        ("tools",     "Tools & hardware",   "Reuse",          "For makers, repairers & small workshops."),
    ]},
    "recycle": {"label": "Recycle", "cats": [
        ("plastic", "Plastic",           "By weight", "Bottles, containers, packaging, broken plastic & toys."),
        ("paper",   "Paper & cardboard", "By weight", "Cartons, newspaper, office paper — clean & dry."),
        ("metal",   "Metal",             "By weight", "Cans, scrap steel, spent utensils — pays best per kg."),
        ("glass",   "Glass",             "By weight", "Bottles & jars, sorted by colour for cullet."),
        ("textile", "Textile scrap",     "By weight", "Worn-out clothes & off-cuts → shredded for fibre."),
        ("wood",    "Wood",              "By weight", "Off-cuts, pallets & broken furniture wood."),
    ]},
}

SEED = {
    "clothes": [("Toddler clothes lot — 25 pcs", "Ages 2–4", "₹450 / lot", "Families & resellers", "Good", "clothes_toddler"),
                ("School uniforms ×12", "Lightly used", "₹600 / lot", "Schools & NGOs", "Good", "clothes_uniforms"),
                ("Footwear bundle ×8", "Sizes 3–6", "₹500 / lot", None, "Worn but works", "clothes_footwear")],
    "toys":    [("Mixed toy bundle — 30 pcs", "Cleaned & sorted", "₹700 / lot", "Daycares & NGOs", "Good", "toys_bundle"),
                ("Board games ×6", "Complete sets", "₹500 / lot", "Event hosts", "Like new", "toys_boardgames"),
                ("Soft toys ×15", "Washed", "₹400 / lot", "NGOs", "Good", "toys_soft")],
    "furniture":[("Study chairs ×4", "Sturdy", "₹1200 / lot", "Refurbishers", "Worn but works", "furniture_chairs"),
                ("Office desk", "Solid", "₹1500", None, "Good", "furniture_desk")],
    "books":   [("Story books ×40", "Grades 3–6", "₹600 / lot", "Schools & libraries", "Good", "books_story"),
                ("Engg textbooks ×10", "1st year", "₹500 / lot", "Students", "Like new", "books_textbooks")],
    "kitchen": [("Steel utensil set", "Fully usable", "₹350", None, "Good", "kitchen_utensils"),
                ("Glass jars ×10", "With lids", "₹250 / lot", None, "Like new", "kitchen_jars")],
    "tools":   [("Hand tools lot", "Hammer, pliers, etc", "₹600 / lot", "Makers & repairers", "Worn but works", "tools_handtools"),
                ("Brushes & rollers ×8", "Cleaned", "₹200 / lot", None, "Good", "tools_brushes")],
    "plastic": [("Sorted PET bottles", "Label-free", "₹18 / kg", "25 kg available", "Clean & sorted", "plastic_pet"),
                ("HDPE containers", "Rinsed", "₹22 / kg", "15 kg available", "Clean & sorted", "plastic_hdpe"),
                ("Mixed rigid plastic", "Incl. broken toys", "₹12 / kg", "40 kg available", "Mixed", "plastic_mixed")],
    "paper":   [("Cardboard — flattened", "Dry & clean", "₹9 / kg", "60 kg available", "Clean & sorted", "paper_cardboard"),
                ("Old newspapers", "Bundled", "₹12 / kg", "30 kg available", "Clean & sorted", "paper_newspaper"),
                ("Office paper", "Assorted", "₹10 / kg", "20 kg available", "Mixed", "paper_office")],
    "metal":   [("Aluminium cans", "Crushed", "₹95 / kg", "8 kg available", "Clean & sorted", "metal_cans"),
                ("Scrap steel utensils", "Beyond use", "₹35 / kg", "18 kg available", "Mixed", "metal_steel")],
    "glass":   [("Glass bottles", "Sorted by colour", "₹3 / kg", "50 kg available", "Clean & sorted", "glass_bottles"),
                ("Jar cullet", "Clean", "₹4 / kg", "30 kg available", "Clean & sorted", "glass_cullet")],
    "textile": [("Worn cotton clothing", "For shredding", "₹8 / kg", "22 kg available", "Mixed", "textile_cotton"),
                ("Fabric off-cuts", "Assorted", "₹10 / kg", "15 kg available", "Mixed", "textile_offcuts")],
    "wood":    [("Plywood off-cuts", "Project-sized", "₹6 / kg", "35 kg available", "Clean & sorted", "wood_plywood"),
                ("Broken furniture wood", "Salvageable", "₹5 / kg", "28 kg available", "Mixed", "wood_furniture")],
}


FACTS = [
    "A plastic bottle can take up to 450 years to break down in a landfill.",
    "Less than 10% of all plastic ever made has actually been recycled.",
    "Reusing an item beats recycling it — it skips all the energy of remaking.",
    "Recycling paper uses far less water and energy than making it from fresh wood.",
]

# Transparent impact basis: a fixed, stated average weight (kg) per listing/lot
# for each category. The kg figure is an ESTIMATE built only from these — no
# random numbers — so it is reproducible and defensible.
CAT_WEIGHT = {
    "clothes": 5, "toys": 4, "furniture": 12, "books": 8, "kitchen": 3, "tools": 4,
    "plastic": 6, "paper": 7, "metal": 5, "glass": 6, "textile": 5, "wood": 9,
}

# ----------------------------------------------------------------------
# Minimalist item illustrations (custom SVG — always appropriate)
# ----------------------------------------------------------------------
ICON = {
    "clothes": (
        "<defs><linearGradient id='clg' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0' stop-color='#46c47e'/><stop offset='1' stop-color='#138a4c'/></linearGradient></defs>"
        "<path d='M46 40 L34 47 Q31 49 33 53 L38 62 Q40 65 43 63 L47 60 V86 Q47 89 50 89 H70 Q73 89 73 86 V60 "
        "L77 63 Q80 65 82 62 L87 53 Q89 49 86 47 L74 40 L68 40 Q60 49 52 40 Z' fill='url(#clg)'/>"
        "<path d='M52 40 Q60 49 68 40' fill='none' stroke='#0c6e3d' stroke-width='2.4'/>"
        "<path d='M47 60 V86 H56 V60 Z' fill='#ffffff' opacity='0.10'/>"
        "<path d='M73 60 V86 H66 V60 Z' fill='#000000' opacity='0.06'/>"),
    "toys": (
        "<defs><radialGradient id='tob' cx='38%' cy='32%' r='72%'>"
        "<stop offset='0' stop-color='#8fd6ff'/><stop offset='1' stop-color='#1f7fce'/></radialGradient></defs>"
        "<circle cx='60' cy='60' r='27' fill='url(#tob)'/>"
        "<path d='M60 33 A27 27 0 0 1 87 60 L60 60 Z' fill='#ffd23f' opacity='0.92'/>"
        "<path d='M60 60 L60 87 A27 27 0 0 1 33 60 Z' fill='#ff5d5d' opacity='0.92'/>"
        "<path d='M33 60 A27 27 0 0 1 60 33 L60 60 Z' fill='#ffffff' opacity='0.85'/>"
        "<ellipse cx='50' cy='49' rx='8' ry='5' fill='#ffffff' opacity='0.55'/>"),
    "furniture": (
        "<defs><linearGradient id='fug' x1='0' y1='0' x2='1' y2='0'>"
        "<stop offset='0' stop-color='#cf9c5e'/><stop offset='1' stop-color='#a9763c'/></linearGradient></defs>"
        "<path d='M44 40 H52 V64 H44 Z' fill='url(#fug)'/>"
        "<path d='M44 40 H72 V46 H44 Z' fill='url(#fug)'/>"
        "<path d='M44 63 H74 V69 H44 Z' fill='url(#fug)'/>"
        "<path d='M44 69 H74 V72 H44 Z' fill='#8a5f2e'/>"
        "<path d='M45 72 H51 V92 H45 Z' fill='#9c6c36'/>"
        "<path d='M67 72 H73 V92 H67 Z' fill='#8a5f2e'/>"
        "<path d='M44 40 H72 V42 H44 Z' fill='#ffffff' opacity='0.18'/>"),
    "books": (
        "<defs>"
        "<linearGradient id='bk1' x1='0' x2='1'><stop offset='0' stop-color='#33a564'/><stop offset='1' stop-color='#1c7a44'/></linearGradient>"
        "<linearGradient id='bk2' x1='0' x2='1'><stop offset='0' stop-color='#ecbf63'/><stop offset='1' stop-color='#cf9a3a'/></linearGradient>"
        "<linearGradient id='bk3' x1='0' x2='1'><stop offset='0' stop-color='#5aa0e0'/><stop offset='1' stop-color='#3a7fc0'/></linearGradient></defs>"
        "<rect x='34' y='70' width='52' height='13' rx='2.5' fill='url(#bk3)'/><rect x='37' y='72.5' width='3' height='8' fill='#ffffff' opacity='0.6'/>"
        "<rect x='38' y='57' width='46' height='13' rx='2.5' fill='url(#bk2)'/><rect x='41' y='59.5' width='3' height='8' fill='#ffffff' opacity='0.6'/>"
        "<rect x='33' y='44' width='50' height='13' rx='2.5' fill='url(#bk1)'/><rect x='36' y='46.5' width='3' height='8' fill='#ffffff' opacity='0.6'/>"),
    "kitchen": (
        "<defs><linearGradient id='kig' x1='0' x2='1'>"
        "<stop offset='0' stop-color='#e9edf1'/><stop offset='0.5' stop-color='#aeb8c2'/><stop offset='1' stop-color='#ced6dd'/></linearGradient></defs>"
        "<rect x='30' y='56' width='10' height='6' rx='3' fill='#8b95a0'/><rect x='80' y='56' width='10' height='6' rx='3' fill='#8b95a0'/>"
        "<path d='M40 56 H80 L77 84 Q77 86 75 86 H45 Q43 86 43 84 Z' fill='url(#kig)'/>"
        "<rect x='37' y='51' width='46' height='7' rx='3.5' fill='#c2cad2'/>"
        "<rect x='49' y='60' width='5' height='22' rx='2.5' fill='#ffffff' opacity='0.55'/>"),
    "tools": (
        "<defs>"
        "<linearGradient id='tlh' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#dde3e9'/><stop offset='1' stop-color='#9aa4ae'/></linearGradient>"
        "<linearGradient id='tlw' x1='0' x2='1'><stop offset='0' stop-color='#cb9c5e'/><stop offset='1' stop-color='#a2733c'/></linearGradient></defs>"
        "<rect x='56' y='50' width='9' height='40' rx='4' fill='url(#tlw)'/>"
        "<path d='M40 41 Q33 43 36 52 L43 52 V46 Z' fill='#8a949e'/>"
        "<path d='M41 40 H73 Q77 40 77 44 V51 H65 V49 H56 V51 H43 V44 Q41 40 41 40 Z' fill='url(#tlh)'/>"
        "<rect x='45' y='43' width='22' height='3' rx='1.5' fill='#ffffff' opacity='0.5'/>"),
    "plastic": (
        "<defs><linearGradient id='plg' x1='0' x2='1'>"
        "<stop offset='0' stop-color='#cfeafc'/><stop offset='0.5' stop-color='#93c9f0'/><stop offset='1' stop-color='#cfeafc'/></linearGradient></defs>"
        "<rect x='53' y='27' width='14' height='9' rx='2' fill='#138a4c'/>"
        "<rect x='55' y='36' width='10' height='6' fill='#9fcde9'/>"
        "<path d='M50 42 Q48 47 48 53 V83 Q48 89 54 89 H66 Q72 89 72 83 V53 Q72 47 70 42 Q66 40 60 40 Q54 40 50 42 Z' fill='url(#plg)'/>"
        "<path d='M48 60 H72 M48 68 H72' stroke='#7fb8e0' stroke-width='1.4' opacity='0.6'/>"
        "<rect x='53' y='46' width='4' height='40' rx='2' fill='#ffffff' opacity='0.6'/>"),
    "paper": (
        "<defs>"
        "<linearGradient id='pa1' x1='0' x2='1'><stop offset='0' stop-color='#dcb784'/><stop offset='1' stop-color='#c69d63'/></linearGradient>"
        "<linearGradient id='pa2' x1='0' x2='1'><stop offset='0' stop-color='#c19a5e'/><stop offset='1' stop-color='#a67d44'/></linearGradient></defs>"
        "<path d='M42 54 L42 46 L52 44 L60 48 Z' fill='#cda268'/>"
        "<path d='M78 54 L78 46 L68 44 L60 48 Z' fill='#bb8f54'/>"
        "<path d='M42 54 L60 60 V88 L42 82 Z' fill='url(#pa1)'/>"
        "<path d='M78 54 L60 60 V88 L78 82 Z' fill='url(#pa2)'/>"
        "<path d='M42 54 L60 48 L78 54 L60 60 Z' fill='#e7c794'/>"),
    "metal": (
        "<defs><linearGradient id='mtg' x1='0' x2='1'>"
        "<stop offset='0' stop-color='#cdd4db'/><stop offset='0.35' stop-color='#eef2f5'/>"
        "<stop offset='0.65' stop-color='#aab4bd'/><stop offset='1' stop-color='#d6dce2'/></linearGradient></defs>"
        "<rect x='46' y='38' width='28' height='44' rx='4' fill='url(#mtg)'/>"
        "<ellipse cx='60' cy='82' rx='14' ry='4' fill='#b8c0c8'/>"
        "<ellipse cx='60' cy='38' rx='14' ry='4' fill='#e6eaee'/>"
        "<ellipse cx='60' cy='38' rx='10' ry='2.6' fill='#9aa4ae'/>"
        "<rect x='46' y='52' width='28' height='16' fill='#138a4c' opacity='0.92'/>"
        "<rect x='50' y='40' width='3' height='40' fill='#ffffff' opacity='0.55'/>"),
    "glass": (
        "<defs><linearGradient id='glg' x1='0' x2='1'>"
        "<stop offset='0' stop-color='#d2efe2'/><stop offset='0.5' stop-color='#a7dcc7'/><stop offset='1' stop-color='#d2efe2'/></linearGradient></defs>"
        "<rect x='48' y='33' width='24' height='10' rx='3' fill='#138a4c'/>"
        "<path d='M48 44 Q60 39 72 44 V80 Q72 85 67 85 H53 Q48 85 48 80 Z' fill='url(#glg)' stroke='#7cc3a8' stroke-width='1.5'/>"
        "<rect x='52' y='49' width='4' height='31' rx='2' fill='#ffffff' opacity='0.6'/>"
        "<rect x='52' y='66' width='16' height='14' rx='2' fill='#7cc3a8' opacity='0.35'/>"),
    "textile": (
        "<defs>"
        "<linearGradient id='tx1' x1='0' x2='1'><stop offset='0' stop-color='#f0a0b4'/><stop offset='1' stop-color='#d96f8c'/></linearGradient>"
        "<linearGradient id='tx2' x1='0' x2='1'><stop offset='0' stop-color='#8ccfac'/><stop offset='1' stop-color='#56a87f'/></linearGradient>"
        "<linearGradient id='tx3' x1='0' x2='1'><stop offset='0' stop-color='#a6bce6'/><stop offset='1' stop-color='#7090c8'/></linearGradient></defs>"
        "<path d='M40 74 Q40 70 44 70 H80 Q84 70 84 74 V80 Q84 84 80 84 H44 Q40 84 40 80 Z' fill='url(#tx3)'/>"
        "<path d='M40 74 Q44 71 44 78 Q44 84 40 80 Z' fill='#5f7fb8'/>"
        "<path d='M42 63 Q42 59 46 59 H82 Q86 59 86 63 V69 Q86 73 82 73 H46 Q42 73 42 69 Z' fill='url(#tx2)'/>"
        "<path d='M42 63 Q46 60 46 67 Q46 73 42 69 Z' fill='#479472'/>"
        "<path d='M44 52 Q44 48 48 48 H84 Q88 48 88 52 V58 Q88 62 84 62 H48 Q44 62 44 58 Z' fill='url(#tx1)'/>"
        "<path d='M44 52 Q48 49 48 56 Q48 62 44 58 Z' fill='#c75f7c'/>"),
    "wood": (
        "<defs>"
        "<linearGradient id='wdg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d6ab6e'/><stop offset='1' stop-color='#b07f44'/></linearGradient>"
        "<radialGradient id='wde' cx='50%' cy='50%' r='55%'><stop offset='0' stop-color='#eccea0'/><stop offset='1' stop-color='#bd9355'/></radialGradient></defs>"
        "<path d='M36 52 H72 V74 H36 Z' fill='url(#wdg)'/>"
        "<path d='M40 57 H68 M40 63 H68 M40 69 H68' stroke='#9a6e3a' stroke-width='1.2' opacity='0.5'/>"
        "<ellipse cx='72' cy='63' rx='9' ry='11' fill='url(#wde)'/>"
        "<ellipse cx='72' cy='63' rx='6' ry='7.5' fill='none' stroke='#a87a44' stroke-width='1.2'/>"
        "<ellipse cx='72' cy='63' rx='3' ry='4' fill='none' stroke='#a87a44' stroke-width='1.2'/>"),
}

def illo(cid):
    return (
        "<div class='rl-img'><svg viewBox='0 0 120 120' width='110' height='110' xmlns='http://www.w3.org/2000/svg'>"
        "<defs><radialGradient id='bgmint' cx='40%' cy='34%' r='75%'>"
        "<stop offset='0%' stop-color='#f4fbf7'/><stop offset='100%' stop-color='#dff0e7'/></radialGradient></defs>"
        "<circle cx='60' cy='60' r='56' fill='url(#bgmint)'/>"
        "<ellipse cx='60' cy='99' rx='27' ry='5' fill='#0b3a22' opacity='0.10'/>"
        + ICON.get(cid, "") + "</svg></div>")

# ----------------------------------------------------------------------
# State
# ----------------------------------------------------------------------
def init():
    d = st.session_state
    d.setdefault("page", "auth"); d.setdefault("user", {})
    d.setdefault("health", 0.18); d.setdefault("loops", 0); d.setdefault("kg", 0.0)
    d.setdefault("action", "shop"); d.setdefault("lane", "reuse"); d.setdefault("category", None)
    d.setdefault("posted", {}); d.setdefault("rescued", set())
    d.setdefault("orders", [])      # items the user has rescued
    d.setdefault("listings", [])    # items the user has listed (flat, for profile)
init()

def go(p): st.session_state.page = p
def word(h): return "Choking" if h < .33 else ("Recovering" if h < .7 else "Thriving")
def reward(pts, kg):
    st.session_state.health = min(1.0, st.session_state.health + pts/100)
    st.session_state.loops += 1; st.session_state.kg += kg

# ----------------------------------------------------------------------
# Styling — minimalist green / white
# ----------------------------------------------------------------------
st.markdown("""
<style>
.stApp{background:#ffffff}
.block-container{max-width:1080px;padding-top:1rem}
h1,h2,h3{font-family:Georgia,'Times New Roman',serif;color:#143d2b;letter-spacing:-.01em}
p,div,span,label{color:#2c3a33}
.rl-ticker{position:relative;overflow:hidden;height:42px;display:flex;align-items:center;
           background:linear-gradient(90deg,#0f7d44,#1ba35d);border-radius:12px;margin:0 0 18px;
           box-shadow:0 8px 20px -12px rgba(15,125,68,.6)}
.rl-badge{position:absolute;left:0;top:0;bottom:0;z-index:3;display:flex;align-items:center;gap:7px;
          background:#143d2b;color:#fff;font-weight:800;font-size:12px;letter-spacing:.10em;padding:0 16px}
.rl-badge .pulse{width:8px;height:8px;border-radius:50%;background:#7cf2a8;animation:rl-pulse 1.2s ease-in-out infinite}
@keyframes rl-pulse{0%,100%{opacity:.4;transform:scale(.8)}50%{opacity:1;transform:scale(1.2)}}
.rl-track{overflow:hidden;width:100%;margin-left:118px}
.rl-tk{display:inline-flex;white-space:nowrap;animation:rl-marq 26s linear infinite}
.rl-tk:hover{animation-play-state:paused}
.rl-tk span{color:#fff;font-weight:600;font-size:14px}
.rl-tk b{color:#bff7d3;margin:0 14px;font-weight:700}
@keyframes rl-marq{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.rl-brand{display:flex;align-items:center;gap:10px;font-family:Georgia,serif;font-weight:700;font-size:24px;color:#143d2b}
.rl-leaf{width:30px;height:30px;border-radius:50%;background:#169d57;display:flex;align-items:center;justify-content:center;color:#fff}
.rl-img{height:120px;display:flex;align-items:center;justify-content:center;background:#f4faf6;border-radius:12px;margin-bottom:10px}
.rl-tag{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;background:#eaf6ee;color:#0f7d44}
.rl-name{font-family:Georgia,serif;font-weight:600;font-size:16px;color:#143d2b;margin:6px 0 2px}
.rl-sub{font-size:12.5px;color:#5d6b63;line-height:1.35}
.rl-meta{font-size:12px;color:#7a857d}
.rl-price{font-family:Georgia,serif;font-weight:700;font-size:17px;color:#143d2b;margin-top:4px}
.rl-buyer{display:inline-block;font-size:11px;font-weight:600;color:#0f7d44;background:#eaf6ee;padding:2px 8px;border-radius:999px;margin-top:3px}
.stButton>button{border-radius:10px;border:1px solid #cfe6d8;font-weight:600}
.stButton>button[kind="primary"]{background:#169d57;border-color:#169d57}
hr{margin:1rem 0;border-color:#e7f0ea}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Living dark forest background (drop images/forest.jpg to use your own)
# ----------------------------------------------------------------------
def _forest_source():
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", "forest" + ext)
        if os.path.exists(p):
            mime = "png" if ext == ".png" else ("webp" if ext == ".webp" else "jpeg")
            data = base64.b64encode(open(p, "rb").read()).decode()
            return f"url('data:image/{mime};base64,{data}')"
    # fallback: a deep-forest gradient so it still looks good without a file
    return ("radial-gradient(120% 90% at 70% 10%, #1c4a31 0%, #103324 40%, #08180f 100%)")

st.markdown(f"""
<style>
.stApp::before{{content:"";position:fixed;inset:-6%;z-index:0;
    background:{_forest_source()} center/cover no-repeat;
    animation:rl-ken 45s ease-in-out infinite alternate;}}
.stApp::after{{content:"";position:fixed;inset:0;z-index:0;
    background:linear-gradient(180deg, rgba(6,16,10,.58), rgba(5,14,9,.72));}}
@keyframes rl-ken{{from{{transform:scale(1.02) translate(0,0)}}
                   to{{transform:scale(1.14) translate(-2%,-2.5%)}}}}
/* float the content as a frosted glass panel so the forest shows through */
.block-container{{position:relative;z-index:1;
    background:rgba(255,255,255,.86);
    backdrop-filter:blur(7px);-webkit-backdrop-filter:blur(7px);
    border:1px solid rgba(255,255,255,.5);border-radius:22px;
    padding:26px 30px 40px;margin-top:18px;
    box-shadow:0 30px 70px -30px rgba(0,0,0,.6);}}
section[data-testid="stSidebar"]{{background:rgba(244,250,246,.92);
    backdrop-filter:blur(6px);}}
</style>
""", unsafe_allow_html=True)

def facts_ribbon():
    run = "".join(f"<span>{f}</span><b>◆</b>" for f in FACTS)
    st.markdown(
        "<div class='rl-ticker'>"
        "<div class='rl-badge'><span class='pulse'></span>ECO FACTS</div>"
        f"<div class='rl-track'><div class='rl-tk'>{run}{run}</div></div>"
        "</div>", unsafe_allow_html=True)

def header():
    st.markdown("<div class='rl-brand'><span class='rl-leaf'>🌱</span> ReLoop</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Sidebar (compact)
# ----------------------------------------------------------------------
def sidebar():
    if not st.session_state.user:
        return
    st.sidebar.markdown("<div class='rl-brand'><span class='rl-leaf'>🌱</span> ReLoop</div>", unsafe_allow_html=True)
    st.sidebar.caption("Keep it in the loop")
    st.sidebar.divider()
    st.sidebar.progress(st.session_state.health, text=f"Planet: **{word(st.session_state.health)}**")
    c1, c2 = st.sidebar.columns(2)
    c1.metric("Looped", st.session_state.loops)
    c2.metric("Saved", f"{st.session_state.kg:.1f} kg")
    st.sidebar.divider()
    if st.sidebar.button("🏠 Home", use_container_width=True):
        go("hub"); st.rerun()
    if st.sidebar.button("👤 My profile", use_container_width=True):
        go("account"); st.rerun()
    if st.sidebar.button("Log out", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# ----------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------
def page_auth():
    facts_ribbon(); header()
    st.markdown("### Keep it in the loop")
    st.write("Reused while it's usable, remade into material when it's spent.")
    t1, t2 = st.tabs(["Log in", "Sign up"])
    with t1:
        email = st.text_input("Email", key="li_email")
        st.text_input("Password", type="password", key="li_pass")
        if st.button("Log in", type="primary", use_container_width=True):
            if email.strip():
                st.session_state.user = {"name": email.split("@")[0].replace(".", " ").replace("_", " ")}
                go("hub"); st.rerun()
            else: st.warning("Enter your email to continue.")
    with t2:
        email = st.text_input("Email", key="su_email")
        pw = st.text_input("Create a password", type="password", key="su_pass")
        if st.button("Continue", type="primary", use_container_width=True):
            if not email.strip(): st.warning("Enter your email to continue.")
            elif len(pw) < 6: st.warning("Password needs at least 6 characters.")
            else:
                st.session_state.user = {"email": email}; go("profile"); st.rerun()

def page_profile():
    facts_ribbon(); header()
    st.markdown("### Tell us who you are")
    name = st.text_input("Full name")
    prof = st.selectbox("You are a…", ["Select one…", "Household", "Maker / Student",
        "Daycare / School / NGO", "Small business / Workshop", "Recycler / Scrap dealer",
        "Refurbisher / Reseller", "Other"])
    city = st.text_input("City", placeholder="e.g. Hyderabad")
    if st.button("Enter ReLoop", type="primary"):
        if not name.strip(): st.warning("Add your name to continue.")
        elif prof == "Select one…": st.warning("Pick what you are to continue.")
        else:
            st.session_state.user = {"name": name, "prof": prof, "city": city}; go("hub"); st.rerun()

def page_hub():
    facts_ribbon(); header()
    first = st.session_state.user.get("name", "there").split(" ")[0].title()
    st.markdown(f"## Hi {first}")
    st.write("Keep things in the loop — reused while usable, remade when spent.")
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("#### 🔍 Rescue an item")
            st.caption("Browse reusable goods and recyclable materials — and keep them looping.")
            if st.button("Rescue an item", use_container_width=True, type="primary"):
                st.session_state.action = "shop"; go("lane"); st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown("#### 📦 Pass it on")
            st.caption("List something you're done with — as a usable item or as material.")
            if st.button("Pass it on", use_container_width=True):
                st.session_state.action = "post"; go("lane"); st.rerun()

def page_lane():
    facts_ribbon(); header()
    act = st.session_state.action
    st.markdown("## " + ("What are you looking for?" if act == "shop" else "What are you passing on?"))
    st.caption("Still usable as-is, or only good for material? Pick the lane.")
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("<span class='rl-tag'>Still usable as-is</span>", unsafe_allow_html=True)
            st.markdown("### ♻️ Reuse")
            st.caption("Whole items sold with a price & condition — often in lots for bulk buyers.")
            if st.button("Enter Reuse lane", use_container_width=True, type="primary"):
                st.session_state.lane = "reuse"; go("category"); st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown("<span class='rl-tag'>Spent — only good for material</span>", unsafe_allow_html=True)
            st.markdown("### 🔁 Recycle")
            st.caption("Material remade — bought by weight by recyclers & makers.")
            if st.button("Enter Recycle lane", use_container_width=True):
                st.session_state.lane = "recycle"; go("category"); st.rerun()
    st.divider()
    if st.button("← Home"): go("hub"); st.rerun()

def page_category():
    facts_ribbon(); header()
    lane = st.session_state.lane
    st.markdown(f"## {LANES[lane]['label']} — pick a {'category' if lane=='reuse' else 'material'}")
    st.caption("Whole items, priced by condition." if lane == "reuse"
               else "Material sold by weight (₹/kg).")
    cats = LANES[lane]["cats"]
    for r in range(0, len(cats), 3):
        cols = st.columns(3)
        for col, (cid, name, tag, sub) in zip(cols, cats[r:r+3]):
            with col:
                with st.container(border=True):
                    p = cat_image_path(cid)
                    if p:
                        st.image(p, use_container_width=True)
                    else:
                        st.markdown(illo(cid), unsafe_allow_html=True)
                    st.markdown(f"<span class='rl-tag'>{tag}</span>"
                                f"<div class='rl-name'>{name}</div>"
                                f"<div class='rl-sub'>{sub}</div>", unsafe_allow_html=True)
                    st.write("")
                    if st.button("Browse" if st.session_state.action == "shop" else "List here",
                                 key=f"cat_{cid}", use_container_width=True):
                        st.session_state.category = cid
                        go("list" if st.session_state.action == "shop" else "post"); st.rerun()
    st.divider()
    if st.button("← Back"): go("lane"); st.rerun()

def card_image(it, cid):
    if it.get("img"):
        st.image(it["img"], use_container_width=True)
        return
    p = slug_image_path(it.get("slug")) or cat_image_path(cid)
    if p:
        st.image(p, use_container_width=True)
    else:
        st.markdown(illo(cid), unsafe_allow_html=True)

def page_list():
    facts_ribbon(); header()
    lane = st.session_state.lane; cid = st.session_state.category
    cat_name = next(c[1] for c in LANES[lane]["cats"] if c[0] == cid)
    st.markdown(f"## {cat_name}")
    st.caption("Priced items & lots — reuse as-is." if lane == "reuse"
               else "Sold by weight — material for remaking.")

    mine = st.session_state.posted.get(cid, [])
    seeded = [{"t": t, "m": m, "price": p, "buyer": b, "cond": c, "slug": s}
              for (t, m, p, b, c, s) in SEED.get(cid, [])]
    items = mine + seeded
    if not items: st.info("Nothing here yet — be the first to add something.")

    for r in range(0, len(items), 3):
        cols = st.columns(3)
        for col, it in zip(cols, items[r:r+3]):
            with col:
                with st.container(border=True):
                    card_image(it, cid)
                    ribbon = "REUSE" if lane == "reuse" else "BY WEIGHT"
                    st.markdown(f"<span class='rl-tag'>{ribbon}</span> {cond_badge(it.get('cond'))}"
                                f"<div class='rl-name'>{it['t']}</div>"
                                f"<div class='rl-meta'>{it['m']}</div>", unsafe_allow_html=True)
                    if it.get("buyer"):
                        st.markdown(f"<div class='rl-buyer'>Bought by {it['buyer']}</div>", unsafe_allow_html=True)
                    price = it["price"] if lane == "reuse" else f"{it['price']} · {it.get('weight','')}"
                    st.markdown(f"<div class='rl-price'>{price}</div>", unsafe_allow_html=True)
                    st.write("")
                    key = f"take_{cid}_{r}_{it['t']}"
                    if key in st.session_state.rescued:
                        st.success("✓ " + ("Rescued" if lane == "reuse" else "Requested"))
                    elif st.button("Rescue" if lane == "reuse" else "Request pickup",
                                   key=key, use_container_width=True, type="primary"):
                        st.session_state.rescued.add(key)
                        w = CAT_WEIGHT.get(cid, 5)
                        st.session_state.orders.append(
                            {"t": it["t"], "cat": cat_name, "cid": cid,
                             "price": it["price"], "lane": lane, "kg": w})
                        reward(6 if lane == "reuse" else 8, w)
                        st.rerun()
    st.divider()
    if st.button("← Categories"): go("category"); st.rerun()

def page_post():
    facts_ribbon(); header()
    lane = st.session_state.lane; cid = st.session_state.category
    cat_name = next(c[1] for c in LANES[lane]["cats"] if c[0] == cid)
    st.markdown("## " + ("List a usable item" if lane == "reuse" else "List material (by weight)"))
    st.caption(f"{LANES[lane]['label']} · {cat_name}")
    st.caption("All fields are required, including a photo.")

    title = st.text_input("Item name *" if lane == "reuse" else "Material name *")
    photo = st.file_uploader("Photo * (required)", type=["png", "jpg", "jpeg"])
    if photo is not None:
        st.image(photo, caption="Preview", width=220)

    if lane == "reuse":
        lot = st.text_input("Lot size / quantity *", placeholder="e.g. 25 pieces")
        cond = st.selectbox("Condition *", ["Select…", "Like new", "Good, fully usable", "Worn but works"])
        price = st.text_input("Price (₹) *", placeholder="e.g. 450 / lot")
    else:
        weight = st.text_input("Approx. weight available *", placeholder="e.g. 25 kg")
        cond = st.selectbox("Quality / condition *", ["Select…", "Clean & sorted", "Mixed", "Contaminated"])
        rate = st.text_input("Expected rate (₹ / kg) *", placeholder="e.g. 18")
    note = st.text_input("Notes *", placeholder="e.g. who it suits / sorting details")

    if st.button("Add to the loop", type="primary"):
        # validate — nothing is optional
        missing = []
        if not title.strip(): missing.append("name")
        if photo is None: missing.append("photo")
        if cond == "Select…": missing.append("condition")
        if not note.strip(): missing.append("notes")
        if lane == "reuse":
            if not lot.strip(): missing.append("lot size")
            if not price.strip(): missing.append("price")
        else:
            if not weight.strip(): missing.append("weight")
            if not rate.strip(): missing.append("rate")

        if missing:
            st.warning("Please fill in: " + ", ".join(missing) + ".")
        else:
            img_bytes = photo.getvalue()
            w = CAT_WEIGHT.get(cid, 5)
            if lane == "reuse":
                pr = price if price.strip().startswith("₹") else "₹" + price.strip()
                item = {"t": title, "m": f"{lot} · {note}", "price": pr,
                        "buyer": None, "cond": cond, "slug": None, "img": img_bytes}
                reward(6, w)
            else:
                pr = "₹" + rate.strip().replace("₹", "").replace("/kg", "").strip() + " / kg"
                item = {"t": title, "m": note, "price": pr, "weight": weight,
                        "cond": cond, "slug": None, "img": img_bytes}
                reward(8, w)
            st.session_state.posted.setdefault(cid, []).insert(0, item)
            st.session_state.listings.append(
                {"t": title, "cat": cat_name, "cid": cid, "price": item["price"],
                 "lane": lane, "cond": cond, "kg": w})
            st.success("Listed! It's now in the loop 🌱")
            st.session_state.action = "shop"; go("list"); st.rerun()

    if lane == "reuse":
        st.divider()
        st.caption("Too worn to reuse? List it as material instead:")
        if st.button("Switch to the Recycle lane →"):
            m = {"clothes": "textile", "furniture": "wood", "toys": "plastic",
                 "kitchen": "glass", "books": "paper", "tools": "metal"}
            st.session_state.lane = "recycle"; st.session_state.category = m.get(cid, "plastic")
            go("post"); st.rerun()
    st.divider()
    if st.button("← Categories"): go("category"); st.rerun()

def page_account():
    facts_ribbon(); header()
    u = st.session_state.user
    st.markdown(f"## {u.get('name','My profile')}")
    bits = [u.get("prof"), u.get("city")]
    st.caption(" · ".join([b for b in bits if b]) or "Your ReLoop profile")

    orders = st.session_state.orders
    listings = st.session_state.listings
    rescued_kg = sum(o["kg"] for o in orders)
    listed_kg = sum(l["kg"] for l in listings)
    total_kg = rescued_kg + listed_kg

    # ---- contribution (precise counts + clearly-labelled estimate) ----
    st.markdown("### 🌍 Your contribution")
    c1, c2, c3 = st.columns(3)
    c1.metric("Items rescued", len(orders))
    c2.metric("Items listed", len(listings))
    c3.metric("Kept from landfill", f"{total_kg:.0f} kg")
    st.caption(
        "Item counts are exact. The weight is an **estimate** using a fixed average "
        "weight per category (e.g. a clothing lot ≈ 5 kg, furniture ≈ 12 kg, wood ≈ 9 kg). "
        "It is calculated only from those averages — no random numbers — so the same "
        "activity always gives the same figure.")
    st.progress(min(total_kg / 100, 1.0), text=f"Toward your first 100 kg")

    st.divider()
    # ---- past orders ----
    st.markdown("### 📦 Items you've rescued")
    if not orders:
        st.info("No rescues yet — browse the lanes and rescue something to see it here.")
    else:
        for o in reversed(orders):
            with st.container(border=True):
                a, b = st.columns([3, 1])
                a.markdown(f"**{o['t']}**  \n<span class='rl-meta'>{o['cat']} · "
                           f"{'Reuse' if o['lane']=='reuse' else 'Recycle'}</span>",
                           unsafe_allow_html=True)
                b.markdown(f"<div class='rl-price'>{o['price']}</div>", unsafe_allow_html=True)

    st.divider()
    # ---- your listings ----
    st.markdown("### 🏷️ Items you've listed")
    if not listings:
        st.info("You haven't listed anything yet. Use **Pass it on** to add an item.")
    else:
        for l in reversed(listings):
            with st.container(border=True):
                a, b = st.columns([3, 1])
                a.markdown(f"**{l['t']}**  \n<span class='rl-meta'>{l['cat']} · "
                           f"{'Reuse' if l['lane']=='reuse' else 'Recycle'}</span> "
                           f"{cond_badge(l.get('cond'))}", unsafe_allow_html=True)
                b.markdown(f"<div class='rl-price'>{l['price']}</div>", unsafe_allow_html=True)

    st.divider()
    if st.button("🏠 Back to home"): go("hub"); st.rerun()

# ----------------------------------------------------------------------
# Router
# ----------------------------------------------------------------------
sidebar()
{
    "auth": page_auth, "profile": page_profile, "hub": page_hub, "lane": page_lane,
    "category": page_category, "list": page_list, "post": page_post,
    "account": page_account,
}.get(st.session_state.page, page_auth)()
