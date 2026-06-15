"""
ReLoop — keep it in the loop (Retro Edition)
Pure-Python Streamlit app. Run: streamlit run app.py
"""

import os
import base64
import streamlit as st

st.set_page_config(page_title="ReLoop — [RETRO_VER_2.0]",
                   page_icon="📟", layout="wide")

# ======================================================================
# DATA
# ======================================================================
LANES = {
    "reuse":   {"label": "Reuse",   "cats": [
        ("clothes",   "Clothes & footwear"), ("toys", "Toys & games"),
        ("furniture", "Furniture"), ("books", "Books & stationery"),
        ("kitchen",   "Kitchen & household"), ("tools", "Tools & hardware")]},
    "recycle": {"label": "Recycle", "cats": [
        ("plastic", "Plastic"), ("paper", "Paper & cardboard"),
        ("metal",   "Metal"),   ("glass", "Glass"),
        ("textile", "Textile scrap"), ("wood", "Wood")]},
}
CAT_NAME = {cid: name for L in LANES.values() for cid, name in L["cats"]}
CAT_LANE = {cid: lane for lane, L in LANES.items() for cid, _ in L["cats"]}

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
    "plastic": [("Sorted PET bottles", "Label-free", "₹18 / kg", "25 kg", "Clean & sorted", "plastic_pet"),
                ("HDPE containers", "Rinsed", "₹22 / kg", "15 kg", "Clean & sorted", "plastic_hdpe"),
                ("Mixed rigid plastic", "Incl. broken toys", "₹12 / kg", "40 kg", "Mixed", "plastic_mixed")],
    "paper":   [("Cardboard — flattened", "Dry & clean", "₹9 / kg", "60 kg", "Clean & sorted", "paper_cardboard"),
                ("Old newspapers", "Bundled", "₹12 / kg", "30 kg", "Clean & sorted", "paper_newspaper"),
                ("Office paper", "Assorted", "₹10 / kg", "20 kg", "Mixed", "paper_office")],
    "metal":   [("Aluminium cans", "Crushed", "₹95 / kg", "8 kg", "Clean & sorted", "metal_cans"),
                ("Scrap steel utensils", "Beyond use", "₹35 / kg", "18 kg", "Mixed", "metal_steel")],
    "glass":   [("Glass bottles", "Sorted by colour", "₹3 / kg", "50 kg", "Clean & sorted", "glass_bottles"),
                ("Jar cullet", "Clean", "₹4 / kg", "30 kg", "Clean & sorted", "glass_cullet")],
    "textile": [("Worn cotton clothing", "For shredding", "₹8 / kg", "22 kg", "Mixed", "textile_cotton"),
                ("Fabric off-cuts", "Assorted", "₹10 / kg", "15 kg", "Mixed", "textile_offcuts")],
    "wood":    [("Plywood off-cuts", "Project-sized", "₹6 / kg", "35 kg", "Clean & sorted", "wood_plywood"),
                ("Broken furniture wood", "Salvageable", "₹5 / kg", "28 kg", "Mixed", "wood_furniture")],
}

FACTS = [
    "A plastic bottle can take up to 450 years to break down in a landfill.",
    "Less than 10% of all plastic ever made has actually been recycled.",
    "Reusing an item beats recycling it — it skips all the energy of remaking.",
    "Recycling paper uses far less water and energy than making it from fresh wood.",
]

CAT_WEIGHT = {"clothes": 5, "toys": 4, "furniture": 12, "books": 8, "kitchen": 3,
              "tools": 4, "plastic": 6, "paper": 7, "metal": 5, "glass": 6,
              "textile": 5, "wood": 9}

# ======================================================================
# RETRO MONOCHROME / BITMAP SVG GRAPHICS
# ======================================================================
ICON = {
 "clothes": "<path d='M30 40 L45 25 L55 35 L65 35 L75 25 L90 40 L80 55 L70 55 L70 90 L50 90 L50 55 L40 55 Z' fill='none' stroke='#39ff14' stroke-width='3'/>",
 "toys": "<circle cx='60' cy='60' r='30' fill='none' stroke='#ff007f' stroke-width='3'/><path d='M40 50 L80 50 M50 70 L70 70' stroke='#ff007f' stroke-width='2'/>",
 "furniture": "<path d='M35 45 H85 V60 H35 Z M45 60 V90 M75 60 V90 M35 45 V30 H45 V45 M75 45 V30 H85 V45' fill='none' stroke='#00ffff' stroke-width='3'/>",
 "books": "<rect x='35' y='35' width='50' height='50' fill='none' stroke='#ffff00' stroke-width='3'/><path d='M60 35 V85' stroke='#ffff00' stroke-width='2'/>",
 "kitchen": "<path d='M40 35 H80 V65 C80 80 40 80 40 65 Z M60 35 V25 M35 35 H85' fill='none' stroke='#ff9900' stroke-width='3'/>",
 "tools": "<path d='M40 80 L70 50 M65 45 L75 55 M70 40 L80 50' stroke='#ff0000' stroke-width='4' stroke-linecap='round'/>",
 "plastic": "<path d='M50 30 H70 L75 45 V85 H45 V45 Z M55 30 V20 H65 V30' fill='none' stroke='#39ff14' stroke-width='3'/>",
 "paper": "<rect x='35' y='35' width='50' height='50' fill='none' stroke='#00ffff' stroke-width='3'/><path d='M45 45 H75 M45 55 H75 M45 65 H65' stroke='#00ffff' stroke-width='2'/>",
 "metal": "<rect x='42' y='30' width='36' height='60' rx='5' fill='none' stroke='#ff007f' stroke-width='3'/>",
 "glass": "<path d='M48 35 H72 V45 L78 55 V85 H42 V55 L48 45 Z' fill='none' stroke='#ffff00' stroke-width='3'/>",
 "textile": "<path d='M35 40 Q45 30 55 40 T75 40 T95 40 L85 85 H45 Z' fill='none' stroke='#ff9900' stroke-width='3'/>",
 "wood": "<rect x='35' y='40' width='50' height='40' fill='none' stroke='#8b5a2b' stroke-width='3'/><circle cx='60' cy='60' r='10' fill='none' stroke='#8b5a2b' stroke-width='2'/>",
}

def illo(cid):
    return (f"<div class='rl-img'><svg viewBox='0 0 120 120' width='120' height='120' xmlns='http://www.w3.org/2000/svg'>"
            f"<rect width='120' height='120' fill='#0e1510' stroke='#223322' stroke-width='2'/>"
            + ICON.get(cid, "") + "</svg></div>")

# ======================================================================
# IMAGE HELPERS
# ======================================================================
def _find(slug):
    if not slug:
        return None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", slug + ext)
        if os.path.exists(p):
            return p
    return None

def item_image(it):
    if it.get("img"):
        st.image(it["img"], use_container_width=True)
        return
    p = _find(it.get("slug")) or _find(it["cid"])
    if p:
        st.image(p, use_container_width=True)
    else:
        st.markdown(illo(it["cid"]), unsafe_allow_html=True)

COND_COLOR = {"Like new": "#39ff14", "Good": "#00ffff", "Good, fully usable": "#00ffff",
              "Clean & sorted": "#39ff14", "Worn but works": "#ff9900", "Mixed": "#ff9900",
              "Contaminated": "#ff0000"}

def badge(c):
    if not c:
        return ""
    return (f"<span style='display:inline-block;font-family:monospace;font-size:11px;padding:1px 6px;"
            f"border:1px solid {COND_COLOR.get(c,'#5d6b63')};color:{COND_COLOR.get(c,'#fff')}; background:transparent;'>[{c}]</span>")

# ======================================================================
# STATE
# ======================================================================
def init():
    d = st.session_state
    d.setdefault("page", "auth")
    d.setdefault("user", {})
    d.setdefault("posted", [])      
    d.setdefault("cart", [])        
    d.setdefault("purchased", [])   
    d.setdefault("nid", 1)          
init()

def go(p):
    st.session_state.page = p

def seed_items():
    out = []
    for cid, rows in SEED.items():
        lane = CAT_LANE[cid]
        for i, row in enumerate(rows):
            title, meta, price, buyer_or_weight, cond, slug = row
            it = {"id": f"s_{cid}_{i}", "cid": cid, "cat": CAT_NAME[cid], "lane": lane,
                  "title": title, "meta": meta, "price": price, "cond": cond,
                  "slug": slug, "img": None, "kg": CAT_WEIGHT[cid]}
            if lane == "reuse":
                it["buyer"] = buyer_or_weight
            else:
                it["weight"] = buyer_or_weight
            out.append(it)
    return out

def all_items():
    return st.session_state.posted + seed_items()

def cart_ids():
    return {c["id"] for c in st.session_state.cart}

def bought_ids():
    return {b["id"] for b in st.session_state.purchased}

def cart_kg():
    return sum(c["kg"] for c in st.session_state.cart)

def saved_kg():
    return sum(b["kg"] for b in st.session_state.purchased) + sum(p["kg"] for p in st.session_state.posted)

# ======================================================================
# RETRO STYLING — 16-BIT CRT ARCADE GREEN SCREEN AESTHETIC
# ======================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

/* ---- Core App Overrides ---- */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #0a0f0d !important;
    font-family: 'VT323', monospace !important;
}

/* CRT Scanline Effect Overlay */
.stApp::before {
    content: " ";
    display: block;
    position: fixed;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 99999;
    opacity: 0.4;
    pointer-events: none;
    background-size: 100% 4px, 6px 100%;
}

/* Text Base Styles */
.block-container, .block-container p, .block-container li, .block-container label,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {
    color: #39ff14 !important;
    font-family: 'VT323', monospace !important;
    font-size: 20px !important;
    text-shadow: 0 0 4px rgba(57, 255, 20, 0.5);
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'VT323', monospace !important;
    color: #ffffff !important;
    text-shadow: 0 0 8px #39ff14 !important;
    text-transform: uppercase;
}
h1 { font-size: 52px !important; }
h2 { font-size: 40px !important; }
h3 { font-size: 32px !important; }

/* Retro Header Box */
.hero-box {
    text-align: center;
    padding: 30px;
    border: 4px double #39ff14;
    background: #0d1611;
    margin-bottom: 25px;
    box-shadow: 0 0 15px rgba(57, 255, 20, 0.2);
}

/* Hard Solid Retro Borders (Containers) */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: #0d1611 !important;
    border: 3px solid #39ff14 !important;
    border-radius: 0px !important; /* Zero round corners for retro crispness */
    box-shadow: 6px 6px 0px #122416 !important;
    padding: 15px !important;
}

/* Input Fields Overrides */
.stTextInput input, .stTextInput textarea, [data-baseweb="input"] input,
[data-baseweb="select"]>div, [data-baseweb="textarea"] textarea {
    background: #000000 !important;
    color: #39ff14 !important;
    border: 2px solid #39ff14 !important;
    border-radius: 0px !important;
    font-family: 'VT323', monospace !important;
    font-size: 20px !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] > div {
    background-color: #050a07 !important;
    border-right: 3px dashed #39ff14;
}

/* Custom Old-School Buttons */
.stButton>button {
    border-radius: 0px !important;
    border: 2px solid #39ff14 !important;
    background: #050a07 !important;
    color: #39ff14 !important;
    font-family: 'VT323', monospace !important;
    font-size: 22px !important;
    text-transform: uppercase;
    box-shadow: 4px 4px 0px #122416;
    transition: all 0.1s ease;
}
.stButton>button:hover {
    background: #39ff14 !important;
    color: #000000 !important;
    box-shadow: 0px 0px 0px transparent;
    text-shadow: none !important;
}
.stButton>button[kind="primary"] {
    background: #225511 !important;
    border: 2px solid #39ff14 !important;
    color: #ffffff !important;
}

/* Eco Marquee / Ticker Box */
.rl-ticker {
    border: 2px solid #39ff14;
    background: #000;
    padding: 6px;
    margin-bottom: 20px;
}
.rl-badge {
    color: #000 !important;
    background: #39ff14;
    font-weight: bold;
    padding: 0 8px;
    margin-right: 10px;
    text-shadow: none !important;
}
.rl-tk span { color: #39ff14 !important; }
.rl-tk b { color: #ff007f !important; }

/* Items Display Tweaks */
.rl-brand { font-size: 32px !important; color: #fff !important; font-weight: bold; }
.rl-name { font-size: 24px !important; color: #fff !important; margin: 5px 0; font-weight: bold;}
.rl-price { font-size: 24px !important; color: #ffff00 !important; font-family: monospace; }
.rl-meta { color: #88c288 !important; font-size: 16px !important; }
.rl-tag { border: 1px solid #39ff14; padding: 2px 6px; font-size: 14px !important; background: rgba(57,255,20,0.1); }
.rl-tag.rec { border: 1px solid #ff007f; color: #ff007f !important; background: rgba(255,0,127,0.1); }
.rl-img { background: #000 !important; border: 1px solid #223322; padding: 10px; margin-bottom: 5px;}
.step { border: 1px dashed #39ff14; padding: 10px; background: #050a07; }
hr { border-color: #39ff14 !important; border-style: dashed; }
</style>
""", unsafe_allow_html=True)

def ticker():
    run = "".join(f"<span>{f}</span> <b>*</b> " for f in FACTS)
    st.markdown("<div class='rl-ticker'><span class='rl-badge'>[SYS_NEWS]</span>"
                f"<marquee scrollamount='4'>{run}</marquee></div>",
                unsafe_allow_html=True)

def brand():
    st.markdown("<div class='rl-brand'>&gt; ReLoop_OS v2.0</div>", unsafe_allow_html=True)

# ======================================================================
# SIDEBAR
# ======================================================================
def sidebar():
    if not st.session_state.user:
        return
    s = st.sidebar
    s.markdown("<div class='rl-brand'>📟 RELOOP</div>", unsafe_allow_html=True)
    name = st.session_state.user.get("name", "USER").upper()
    s.caption(f"LOGGED IN AS: {name}")
    s.divider()

    s.markdown(f"### [BUFFER]")
    s.write(f"Items in Cart: {len(st.session_state.cart)}")
    s.write(f"Pending Mass: {cart_kg():.0f} KG")
    s.metric("TOTAL SAVED MASS", f"{saved_kg():.0f} KG")
    s.divider()

    nav = [("COMMAND: HOME", "home"), ("COMMAND: MARKET", "market"),
           ("COMMAND: SELL", "sell"), ("COMMAND: VIEW_CART", "cart"),
           ("COMMAND: PROFILE", "account")]
    for label, page in nav:
        if s.button(label, use_container_width=True, key=f"nav_{page}"):
            go(page); st.rerun()
    s.divider()
    if s.button("DISCONNECT", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ======================================================================
# ITEM CARD
# ======================================================================
def item_card(it, col):
    with col:
        with st.container(border=True):
            item_image(it)
            tagcls = "rl-tag" if it["lane"] == "reuse" else "rl-tag rec"
            tagtxt = "MODE: REUSE" if it["lane"] == "reuse" else "MODE: RECYCLE"
            st.markdown(f"<span class='{tagcls}'>{tagtxt}</span> {badge(it.get('cond'))}"
                        f"<div class='rl-name'>{it['title'].upper()}</div>"
                        f"<div class='rl-meta'>CAT: {it['cat'].upper()} // {it['meta']}</div>", unsafe_allow_html=True)
            if it.get("buyer"):
                st.markdown(f"<div class='rl-meta'>TARGET: {it['buyer']}</div>", unsafe_allow_html=True)
            price = it["price"] if it["lane"] == "reuse" else f"{it['price']} [{it.get('weight','')}]"
            st.markdown(f"<div class='rl-price'>{price}</div>", unsafe_allow_html=True)
            st.caption(f"EST_MASS: {it['kg']} KG")
            st.write("")
            if it["id"] in bought_ids():
                st.success("[ALLOCATED]")
            elif it["id"] in cart_ids():
                st.button("[STAGED]", key=f"in_{it['id']}", use_container_width=True, disabled=True)
            else:
                if st.button("STAGE ITEM 🧺", key=f"add_{it['id']}", use_container_width=True, type="primary"):
                    st.session_state.cart.append(it)
                    st.rerun()

# ======================================================================
# PAGES
# ======================================================================
def page_auth():
    ticker(); brand()
    st.markdown("### SYSTEM OVERVIEW")
    st.write("Buy/sell reusable assets & recycle core materials. Prevent landfill dumps.")
    t1, t2 = st.tabs(["[ SECURE_LOGIN ]", "[ REGISTER_USER ]"])
    with t1:
        e = st.text_input("ENTER EMAIL", key="li")
        st.text_input("ENTER PASSWORD", type="password", key="lp")
        if st.button("INITIALIZE TERMINAL", type="primary", use_container_width=True):
            if e.strip():
                st.session_state.user = {"name": e.split("@")[0].replace(".", " ").replace("_", " ")}
                go("home"); st.rerun()
            else:
                st.warning("ERROR: Email context required.")
    with t2:
        e = st.text_input("CHOOSE EMAIL", key="si")
        p = st.text_input("CHOOSE PASSWORD", type="password", key="sp")
        if st.button("WRITE ACCESS CREDENTIALS", type="primary", use_container_width=True):
            if not e.strip():
                st.warning("ERROR: Email required.")
            elif len(p) < 6:
                st.warning("ERROR: Security key too weak (< 6 chars).")
            else:
                st.session_state.user = {"email": e}
                go("setup"); st.rerun()

def page_setup():
    ticker(); brand()
    st.markdown("### CONFIG_USER_PROFILE")
    name = st.text_input("IDENTIFICATION (FULL NAME)")
    prof = st.selectbox("USER CLASS TYPE...", ["Select…", "Household", "Maker / Student",
        "Daycare / School / NGO", "Small business / Workshop", "Recycler / Scrap dealer",
        "Refurbisher / Reseller", "Other"])
    city = st.text_input("SECTOR (CITY LOCATION)", placeholder="e.g. Hyderabad")
    if st.button("EXECUTE PROFILE_START", type="primary"):
        if not name.strip():
            st.warning("Field Required: Identification.")
        elif prof == "Select…":
            st.warning("Field Required: User Class Type.")
        else:
            st.session_state.user = {"name": name, "prof": prof, "city": city}
            go("home"); st.rerun()

def page_home():
    ticker(); brand()
    st.markdown("""
    <div class='hero-box'>
        <h1>📟 RE_LOOP // SYSTEM</h1>
        <h3>&gt;&gt; ACCESS_GRANTED: REUSE . RECYCLE . RECOVER</h3>
        <p>Routing obsolete and secondary goods back into production tracks.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### OPERATIONAL MATRIX")
    a, b, c = st.columns(3)
    a.markdown("<div class='step'>[01] EMIT ASSET 📦<br><span class='rl-meta'>List your surplus hardware/scrap with specifications.</span></div>", unsafe_allow_html=True)
    b.markdown("<div class='step'>[02] ACQUIRE ASSET 🛒<br><span class='rl-meta'>Query database and capture units for secondary usage.</span></div>", unsafe_allow_html=True)
    c.markdown("<div class='step'>[03] CLOSED_LOOP ♻️<br><span class='rl-meta'>Diverted components skip terminal dumping nodes.</span></div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("##### SELECT ROUTE COMMAND")
    x, y = st.columns(2)
    with x:
        with st.container(border=True):
            st.markdown("### Query Marketplace Database")
            if st.button("RUN: MARKET_DB", type="primary", use_container_width=True):
                go("market"); st.rerun()
    with y:
        with st.container(border=True):
            st.markdown("### Broadcast New Asset")
            if st.button("RUN: BROADCAST_ASSET", use_container_width=True):
                go("sell"); st.rerun()

    st.markdown("## 📡 HIGHLIGHTED CACHE SUMMARY")
    featured = all_items()[:3]
    cols = st.columns(3)
    for item, col in zip(featured, cols):
        item_card(item, col)

def page_market():
    ticker(); brand()
    st.markdown("## 🛒 CENTRAL DATABASE QUERY")

    market_type = st.radio("FILTER MATRIX CLASSIFICATION:", ["All", "Reuse", "Recycle"], horizontal=True)
    cat = st.selectbox("FILTER FIELD CATEGORY:", ["All"] + [CAT_NAME[c] for c in CAT_NAME])
    q = st.text_input("EXECUTE CONSOLE SEARCH", placeholder="🔍 Input keyword parameters...")

    items = all_items()
    if market_type != "All":
        items = [i for i in items if i["lane"] == market_type.lower()]
    if cat != "All":
        items = [i for i in items if i["cat"] == cat]
    if q.strip():
        ql = q.lower()
        items = [i for i in items if ql in i["title"].lower() or ql in i["cat"].lower()]

    st.write(f"**MATCHES FOUND: {len(items)} RECORD(S)**")
    if not items:
        st.info("Zero results match configuration parameters.")
    for r in range(0, len(items), 3):
        cols = st.columns(3)
        for it, col in zip(items[r:r+3], cols):
            item_card(it, col)

def page_sell():
    ticker(); brand()
    st.markdown("## ➕ BROADCAST DISPOSAL PIPELINE")
    st.caption("All data points mandatory. Upload metadata photo to initialize.")

    lane_label = st.radio("ASSET INTEGRITY STATE:",
                          ["Reuse — functional deployment", "Recycle — raw base materials"], horizontal=False)
    lane = "reuse" if lane_label.startswith("Reuse") else "recycle"
    cats = [CAT_NAME[c] for c, _ in LANES[lane]["cats"]]
    cat_label = st.selectbox("SYSTEM CLASS CATEGORY", cats)
    cid = next(c for c in CAT_NAME if CAT_NAME[c] == cat_label)

    title = st.text_input("ASSET LOGICAL NAME")
    photo = st.file_uploader("IMAGE BITMAP DESCRIPTOR (REQUIRED)", type=["png", "jpg", "jpeg"])
    if photo is not None:
        st.image(photo, width=220, caption="Preview Image Buffer")

    if lane == "reuse":
        qty = st.text_input("BATCH METRIC QUANTITY", placeholder="e.g. 25 pieces")
        cond = st.selectbox("OPERATION STATUS CODES", ["Select…", "Like new", "Good, fully usable", "Worn but works"])
        price = st.text_input("VALUE ASSESSMENT VALUE (₹)", placeholder="e.g. 450")
    else:
        weight = st.text_input("ESTIMATED QUANTUM WEIGHT", placeholder="e.g. 25 kg")
        cond = st.selectbox("RAW MATERIAL VALUE RATING", ["Select…", "Clean & sorted", "Mixed", "Contaminated"])
        rate = st.text_input("BASE MASS VALUE RATE (₹ / kg)", placeholder="e.g. 18")
    note = st.text_input("SYSTEM NOTES", placeholder="Target use case / sorting details")

    if st.button("TRANSMIT TO MARKET SYSTEM NODE", type="primary"):
        miss = []
        if not title.strip(): miss.append("name")
        if photo is None: miss.append("photo")
        if cond == "Select…": miss.append("condition")
        if not note.strip(): miss.append("notes")
        if lane == "reuse":
            if not qty.strip(): miss.append("lot size")
            if not price.strip(): miss.append("price")
        else:
            if not weight.strip(): miss.append("weight")
            if not rate.strip(): miss.append("rate")
        if miss:
            st.warning("CRITICAL EXCEPTION: Empty fields -> " + ", ".join(miss) + ".")
        else:
            iid = f"u_{st.session_state.nid}"; st.session_state.nid += 1
            it = {"id": iid, "cid": cid, "cat": cat_label, "lane": lane, "title": title,
                  "cond": cond, "slug": None, "img": photo.getvalue(), "kg": CAT_WEIGHT[cid]}
            if lane == "reuse":
                it["meta"] = f"{qty} · {note}"
                it["price"] = price if price.strip().startswith("₹") else "₹" + price.strip()
                it["buyer"] = None
            else:
                it["meta"] = note
                it["price"] = "₹" + rate.strip().replace("₹", "").replace("/kg", "").strip() + " / kg"
                it["weight"] = weight
            st.session_state.posted.insert(0, it)
            st.success("SUCCESS: Memory block written to active Market Registry Node! 🌱")
            go("market"); st.rerun()

def page_cart():
    ticker(); brand()
    st.markdown("## 🧺 STAGING BUFFER AREA")
    cart = st.session_state.cart
    if not cart:
        st.info("Staging buffer array empty. Intercept market assets to pipeline them.")
        if st.button("GOTO: MARKET_DB_CONSOLE", type="primary"):
            go("market"); st.rerun()
        return

    st.success(f"DIVERSION ALERT: Resolving this matrix keeps ~{cart_kg():.0f} KG safely routed away from disposal nodes.")
    for idx, it in enumerate(list(cart)):
        with st.container(border=True):
            a, b, c = st.columns([1, 3, 1])
            with a:
                item_image(it)
            b.markdown(f"**{it['title'].upper()}** \n<span class='rl-meta'>CLASS: {it['cat'].upper()} · "
                       f"{'REUSE' if it['lane']=='reuse' else 'RECYCLE'}</span> {badge(it.get('cond'))}  \n"
                       f"<span class='rl-price'>{it['price']}</span> · {it['kg']} KG",
                       unsafe_allow_html=True)
            if c.button("DROP RECORD", key=f"rm_{idx}"):
                st.session_state.cart.pop(idx); st.rerun()

    st.divider()
    st.markdown(f"### COMBINED TOTAL SUMMARY: {len(cart)} BLOCK ENTRIES · ~{cart_kg():.0f} KG DIVERTED")
    if st.button("EXECUTE COMMIT TRANSACTION ✅", type="primary", use_container_width=True):
        st.session_state.purchased.extend(cart)
        st.session_state.cart = []
        st.success("TRANSACTION COMMITTED: Inventory ownership arrays modified.")
        go("account"); st.rerun()

def page_account():
    ticker(); brand()
    u = st.session_state.user
    st.markdown(f"## 👤 CONSOLE_USER: {u.get('name','ANONYMOUS').upper()}")
    st.caption(" // ".join([x.upper() for x in [u.get('prof'), u.get('city')] if x]) or "USER TERMINAL NODE STATUS")

    bought, posted = st.session_state.purchased, st.session_state.posted
    st.markdown("### SYSTEM RECOVERY METRICS")
    c1, c2, c3 = st.columns(3)
    c1.metric("ASSETS ACQUIRED", len(bought))
    c2.metric("ASSETS BROADCASTED", len(posted))
    c3.metric("MASS COUPLING SAVED", f"{saved_kg():.0f} KG")
    
    st.progress(min(saved_kg() / 100, 1.0), text="System Node status calibration to 100 KG target metric")

    st.divider()
    st.markdown("### 🛍️ INBOUND LOG ENTRY HISTORY")
    if not bought:
        st.info("No logs present. Stage and process checkout arrays.")
    else:
        for r in range(0, len(bought), 3):
            for it, col in zip(bought[r:r+3], st.columns(3)):
                item_card_static(it, col)

    st.divider()
    st.markdown("### 🏷️ OUTBOUND BROADCAST REGISTRY")
    if not posted:
        st.info("No assets listed. Broadcast units from the Sell Terminal Console.")
    else:
        for r in range(0, len(posted), 3):
            for it, col in zip(posted[r:r+3], st.columns(3)):
                item_card_static(it, col)

    st.divider()
    if st.button("RETURN TO ROOT DIRECTORY (HOME)"):
        go("home"); st.rerun()

def item_card_static(it, col):
    with col:
        with st.container(border=True):
            item_image(it)
            st.markdown(f"<div class='rl-name'>{it['title'].upper()}</div>"
                        f"<div class='rl-meta'>{it['cat'].upper()}</div> {badge(it.get('cond'))}"
                        f"<div class='rl-price'>{it.get('price','')}</div>", unsafe_allow_html=True)
            st.caption(f"MASS: {it['kg']} KG")

# ======================================================================
# ROUTER
# ======================================================================
sidebar()
{
    "auth": page_auth, "setup": page_setup, "home": page_home, "market": page_market,
    "sell": page_sell, "cart": page_cart, "account": page_account,
}.get(st.session_state.page, page_auth)()