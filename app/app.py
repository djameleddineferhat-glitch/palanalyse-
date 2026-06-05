"""
Palstream v5 - streamlit run app/app.py
"""
import streamlit as st
import pandas as pd
import os, base64
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Palstream", layout="wide", initial_sidebar_state="collapsed")

BASE     = Path(__file__).parent.resolve()
DATA_DIR = BASE.parent / "data"
PAL_DIR  = BASE / "assets" / "pals"
ELEM_DIR = BASE / "assets" / "pals"  # icones types dans le même dossier

BG_DIR  = BASE / "assets" / "backgrounds"
SND_DIR = BASE / "assets" / "sounds"

def bg_css(name: str) -> str:
    path = BG_DIR / f"{name}.jpg"
    data = b64(path)
    if not data:
        return ""
    return (
        '<style>.stTabs [data-baseweb="tab-panel"] > div:first-child {'
        f'background:url("data:image/jpeg;base64,{data}") center/cover no-repeat fixed;'
        'border-radius:16px;padding:24px;'
        'box-shadow:inset 0 0 0 9999px rgba(0,0,0,0.65)}</style>'
    )

def play_sound(name: str):
    path = SND_DIR / f"{name}.wav"
    data = b64(path)
    if not data:
        return
    st.markdown(
        f'<audio autoplay style="display:none">'
        f'<source src="data:audio/wav;base64,{data}" type="audio/wav">'
        f'</audio>',
        unsafe_allow_html=True)


# ── Mappings ──────────────────────────────────────────────────────────────
ELEM_FR = {
    "fire":"Feu","water":"Eau","Wood":"Plante","electricity":"Electricite",
    "ice":"Glace","dark":"Tenebres","dragon":"Dragon","land":"Terre","generally":"Normal",
}
ELEM_COLOR = {
    "fire":"#E74C3C","water":"#2980B9","Wood":"#27AE60","electricity":"#F39C12",
    "ice":"#85C1E9","dark":"#8E44AD","dragon":"#E67E22","land":"#A04000","generally":"#7F8C8D",
}
# Nom du fichier icône type dans assets/pals/
ELEM_ICON_FILE = {
    "fire":"feu","water":"eau","Wood":"feuille","electricity":"électricité",
    "ice":"glace","dark":"ténèbres","dragon":"dragon","land":"terre","generally":"normal",
}
SKILL_FR = {
    'Make a fire':'Allumage','watering':'Arrosage','planting':'Plantation',
    'generate electricity':'Production délectricité','manual':'Travail manuel',
    'collection':'Collecte','logging':'Déforestation','Mining':'Minage',
    'pharmaceutical':'Production de médicaments','cool down':'Refroidissement',
    'pasture':'Agriculture','carry':'Transport',
}
SKILL_ICON = {
    'Make a fire':'allumage','watering':'arrosage','planting':'plantation',
    'generate electricity':'production_délectricité','manual':'travail_manuel',
    'collection':'collecte','logging':'déforestation','Mining':'minage',
    'pharmaceutical':'production_de_médicaments','cool down':'refroidissement',
    'pasture':'agriculture','carry':'transport',
}
TAILLE_FR = {"XS":"Minuscule","S":"Petit","M":"Moyen","L":"Grand","XL":"Tres grand"}

# Backgrounds par onglet
TAB_BG = {
    0: "linear-gradient(135deg,#0D1B2A 0%,#1B2838 50%,#0D2137 100%)",  # Accueil - bleu nuit
    1: "linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%)",  # Paldex - bleu profond
    2: "linear-gradient(135deg,#2d1b33 0%,#1a1a2e 50%,#16213e 100%)",  # Fiche - violet sombre
    3: "linear-gradient(135deg,#1a0000 0%,#2d0a0a 50%,#1a1a2e 100%)",  # Combat - rouge sombre
    4: "linear-gradient(135deg,#0a2010 0%,#0d2818 50%,#1a2e1a 100%)",  # Campement - vert sombre
    5: "linear-gradient(135deg,#0a1628 0%,#1a2438 50%,#0d1f35 100%)",  # Zones - bleu acier
    6: "linear-gradient(135deg,#2d1500 0%,#3d1a00 50%,#1a0d00 100%)",  # Boss - orange sombre
    7: "linear-gradient(135deg,#1a1a1a 0%,#2d2d2d 50%,#1a1a2e 100%)",  # Explorateur - gris sombre
}

# ── CSS global ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display:none!important }

/* App background */
.stApp { background: #0D1B2A; }

/* Onglets */
.stTabs [data-baseweb="tab-list"] {
    gap:0; background:rgba(0,0,0,0.4); backdrop-filter:blur(10px);
    border-bottom:1px solid rgba(255,255,255,0.1);
    padding:0 16px; position:sticky; top:0; z-index:100;
}
.stTabs [data-baseweb="tab"] {
    color:rgba(255,255,255,0.55)!important; font-weight:600; font-size:.85rem;
    padding:14px 20px; border-bottom:3px solid transparent;
    border-radius:0; background:transparent!important; transition:all .25s;
    letter-spacing:.3px;
}
.stTabs [aria-selected="true"] {
    color:white!important; border-bottom:3px solid #42A5F5!important;
    background:rgba(66,165,245,0.08)!important;
}
.stTabs [data-baseweb="tab"]:hover { color:rgba(255,255,255,.85)!important }
.stTabs [data-baseweb="tab-panel"] { padding:24px 0 0 0 }

/* Métriques */
div[data-testid="metric-container"] {
    background:rgba(255,255,255,0.05); border-radius:12px;
    padding:14px 18px; border:1px solid rgba(255,255,255,0.1);
    backdrop-filter:blur(5px);
}
div[data-testid="metric-container"] label { color:rgba(255,255,255,.6)!important }
div[data-testid="metric-container"] div[data-testid="metric-value"] { color:white!important }

/* Texte général */
.stMarkdown, .stText, p, h1, h2, h3, h4 { color:rgba(255,255,255,.9)!important }

/* Inputs */
.stSelectbox>div>div, .stTextInput>div>div>input, .stNumberInput>div>div>input {
    background:rgba(255,255,255,0.08)!important;
    border:1.5px solid rgba(255,255,255,0.2)!important;
    color:white!important; border-radius:10px!important;
    font-size:1rem!important; padding:10px 16px!important;
    min-height:48px!important;
}
.stSelectbox [data-baseweb="select"] {
    background:rgba(255,255,255,0.08)!important; min-height:48px!important;
}
.stSelectbox [data-baseweb="select"] > div {
    padding:10px 16px!important; font-size:1rem!important; color:white!important;
}
.stSelectbox svg { fill:white!important }
[data-testid="stHorizontalBlock"] > [data-testid="column"] { padding:0 10px!important }

/* Slider */
.stSlider [data-baseweb="slider"] { padding:0 }

/* Divider */
hr { border-color:rgba(255,255,255,0.1)!important }

/* Dataframe */
.stDataFrame { border-radius:10px; overflow:hidden }

/* Scrollbar */
::-webkit-scrollbar { width:6px; height:6px }
::-webkit-scrollbar-track { background:rgba(255,255,255,.05) }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,.2); border-radius:3px }

/* Caption */
.stCaption { color:rgba(255,255,255,.45)!important }

/* Boutons */
.stButton>button {
    background:rgba(66,165,245,0.15)!important;
    border:1px solid rgba(66,165,245,0.4)!important;
    color:white!important; border-radius:8px!important;
    transition:all .2s!important;
}
.stButton>button:hover {
    background:rgba(66,165,245,0.3)!important;
    border-color:rgba(66,165,245,0.7)!important;
}

/* Cards */
.pal-card {
    border-radius:14px; padding:12px; text-align:center;
    border:1px solid; transition:transform .2s, box-shadow .2s;
    cursor:pointer; backdrop-filter:blur(5px);
}
.pal-card:hover { transform:translateY(-4px); box-shadow:0 8px 24px rgba(0,0,0,0.4)!important }

/* Info / warning */
.stAlert { background:rgba(255,255,255,0.06)!important; border-radius:10px!important }
</style>
""", unsafe_allow_html=True)

# ── Helpers images ─────────────────────────────────────────────────────────
def b64(path) -> str:
    try:
        with open(str(path), "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def pal_img(name: str, size=100) -> str:
    safe = name.replace(" ","_").replace("(","").replace(")","")
    data = b64(PAL_DIR / f"{safe}.png")
    if data:
        return (f'<img src="data:image/png;base64,{data}" width="{size}" height="{size}" '
                f'style="border-radius:50%;object-fit:cover;border:2px solid rgba(255,255,255,.3)"/>')
    # SVG fallback
    color = ELEM_COLOR.get("generally", "#888")
    init  = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<svg width="{size}" height="{size}"><circle cx="{size//2}" cy="{size//2}" '
            f'r="{size//2-2}" fill="{color}"/>'
            f'<text x="{size//2}" y="{size//2+5}" text-anchor="middle" font-size="{size//3}" '
            f'font-weight="900" fill="white" font-family="Arial">{init}</text></svg>')

def elem_img(elem: str, size=20) -> str:
    fname = ELEM_ICON_FILE.get(elem, "normal")
    data  = b64(ELEM_DIR / f"{fname}.png")
    color = ELEM_COLOR.get(elem, "#888")
    fr    = ELEM_FR.get(elem, elem)
    if data:
        return (f'<span style="display:inline-flex;align-items:center;gap:4px;'
                f'background:{color}33;border:1px solid {color}66;border-radius:20px;'
                f'padding:2px 8px;font-size:.75rem;font-weight:700;color:white">'
                f'<img src="data:image/png;base64,{data}" width="{size}" height="{size}" '
                f'style="border-radius:50%"/> {fr}</span>')
    return (f'<span style="background:{color};color:white;border-radius:20px;'
            f'padding:2px 8px;font-size:.75rem;font-weight:700">{fr}</span>')

def skill_img(skill_key: str, size=18) -> str:
    fname = SKILL_ICON.get(skill_key, "")
    if not fname:
        return ""
    data = b64(ELEM_DIR / f"{fname}.png")
    if data:
        return (f'<img src="data:image/png;base64,{data}" width="{size}" height="{size}" '
                f'style="border-radius:4px;vertical-align:middle"/>')
    return ""

def stat_bar(label, val, max_val, color):
    pct = min(int(float(val)/float(max_val)*100),100) if max_val>0 else 0
    return (f'<div style="margin:5px 0">'
            f'<div style="display:flex;justify-content:space-between;font-size:.78rem;margin-bottom:2px">'
            f'<span style="color:rgba(255,255,255,.7)">{label}</span>'
            f'<span style="font-weight:700;color:{color}">{int(float(val))}</span></div>'
            f'<div style="background:rgba(255,255,255,.1);border-radius:4px;height:7px">'
            f'<div style="background:{color};width:{pct}%;height:7px;border-radius:4px;'
            f'transition:width .5s ease"></div></div></div>')

def card(row, size=85, show_score=True):
    elem  = str(row.get('Element 1','generally'))
    color = ELEM_COLOR.get(elem,'#607D8B')
    score_html = f'<div style="font-size:.72rem;color:{color};font-weight:700;margin-top:2px">Score {int(row["combat_score"])}</div>' if show_score else ''
    return (f'<div class="pal-card" style="border-color:{color}55;'
            f'background:linear-gradient(160deg,{color}25,rgba(0,0,0,.3))">'
            f'{pal_img(str(row["Name"]),size)}'
            f'<div style="font-weight:700;font-size:.8rem;margin:5px 0 3px;color:white;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{row["Name"]}</div>'
            f'{elem_img(elem)}'
            f'<div style="font-size:.68rem;color:rgba(255,255,255,.6);margin-top:3px">'
            f'HP {int(row["HP"])} · Att {int(row["melee attack"])}</div>'
            f'{score_html}</div>')

def hex_to_rgba(h, a=0.2):
    h=h.lstrip('#'); r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

# ── Chargement ─────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df_c = pd.read_csv(DATA_DIR/"Palworld_Data--Palu_combat_attribute_table.csv", skiprows=1)
    df_j = pd.read_csv(DATA_DIR/"Palworld_Data-Palu_Job_Skills_Table.csv", skiprows=1)
    df_t = pd.read_csv(DATA_DIR/"Palworld_Data-Tower_BOSS_attribute_comparison.csv")
    df_b = pd.read_csv(DATA_DIR/"Palworld_Data-comparison_of_ordinary_BOSS_attributes.csv", skiprows=3)
    df_r = pd.read_csv(DATA_DIR/"Palworld_Data--Palu_refresh_level.csv", skiprows=1, header=None)

    for col in ['HP','melee attack','Remote attack','defense','support','Speed of work','rarity','running speed']:
        if col in df_c.columns:
            df_c[col] = pd.to_numeric(df_c[col], errors='coerce').fillna(0)
    if 'catch rate' in df_c.columns:
        df_c['catch_rate_num'] = df_c['catch rate'].astype(str).str.replace('%','',regex=False).pipe(pd.to_numeric, errors='coerce')
    df_c['Element FR'] = df_c['Element 1'].map(ELEM_FR).fillna(df_c['Element 1'])
    df_c['combat_score'] = df_c['HP'] + df_c['melee attack']*2 + df_c['defense']
    df_c['rang'] = df_c['combat_score'].rank(ascending=False, method='min').astype(int)

    SK = [c for c in SKILL_FR if c in df_j.columns]
    for c in SK:
        df_j[c] = pd.to_numeric(df_j[c], errors='coerce').fillna(0)
    for c in ['Handling speed','Total skills','Food intake']:
        if c in df_j.columns:
            df_j[c] = pd.to_numeric(df_j[c], errors='coerce')
    if 'night shift' in df_j.columns:
        df_j['nuit'] = df_j['night shift'].notna() & df_j['night shift'].astype(str).str.strip().str.lower().isin(['true','1','yes','oui','x'])

    merge_cols = ['English name'] + SK + [c for c in ['Handling speed','Total skills','Food intake','nuit','ranch items','pasture minimum output'] if c in df_j.columns]
    df_m = df_c.merge(df_j[merge_cols], left_on='Name', right_on='English name', how='left')
    return df_c, df_j, df_t, df_b, df_r, df_m

df_c, df_j, df_tower, df_boss, df_ref, df_m = load()
SK = [c for c in SKILL_FR if c in df_j.columns]

# ── ONGLETS ────────────────────────────────────────────────────────────────
t0,t1,t2,t3,t4,t5,t6,t7 = st.tabs([
    "Accueil","Paldex","Fiche Pal","Combat","Campement","Zones","Boss","Explorateur"
])

# ════════════════════════════════════════════════════════════════════════
# ACCUEIL
# ════════════════════════════════════════════════════════════════════════
with t0:
    st.markdown(bg_css("accueil"), unsafe_allow_html=True)
    play_sound("accueil")
    st.markdown(f"""
    <div style="background:{TAB_BG[0]};border-radius:16px;padding:32px;margin-bottom:24px;
        border:1px solid rgba(255,255,255,.08)">
        <h1 style="color:white;margin:0;font-size:2rem">Palstream</h1>
        <p style="color:rgba(255,255,255,.6);margin:6px 0 0">
            Analyse des 138 Pals de Palworld — combat, campement, zones
        </p>
    </div>""", unsafe_allow_html=True)

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Pals", len(df_c))
    k2.metric("HP max", int(df_c['HP'].max()))
    k3.metric("Attaque max", int(df_c['melee attack'].max()))
    k4.metric("Rarete max", int(df_c['rarity'].max()))
    k5.metric("Elements", int(df_c['Element 1'].nunique()))

    st.divider()
    st.markdown("### Top 5 Pals au combat")
    top5 = df_c.nlargest(5,'combat_score')
    cols = st.columns(5)
    for i,(_,row) in enumerate(top5.iterrows()):
        with cols[i]:
            st.markdown(card(row,90), unsafe_allow_html=True)

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        el = df_c['Element 1'].value_counts().reset_index()
        el.columns=['Element','Nb']
        el['FR'] = el['Element'].map(ELEM_FR)
        fig = px.bar(el, x='FR', y='Nb', color='Element',
                     color_discrete_map={e:ELEM_COLOR.get(e,'#888') for e in el['Element']},
                     title="Distribution des elements",
                     template="plotly_dark")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          showlegend=False, title_font_color='white')
        st.plotly_chart(fig, width='stretch')
    with c2:
        rc = df_c['rarity'].value_counts().sort_index().reset_index()
        rc.columns=['Rarete','Nb']
        fig2 = px.bar(rc, x='Rarete', y='Nb', color='Rarete',
                      color_continuous_scale='Viridis', title="Distribution de la rarete",
                      template="plotly_dark")
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           title_font_color='white', coloraxis_showscale=False)
        st.plotly_chart(fig2, width='stretch')

# ════════════════════════════════════════════════════════════════════════
# PALDEX
# ════════════════════════════════════════════════════════════════════════
with t1:
    st.markdown(bg_css("paldex"), unsafe_allow_html=True)
    play_sound("paldex")
    st.markdown(f"""
    <div style="background:{TAB_BG[1]};border-radius:16px;padding:20px 28px;margin-bottom:20px;
        border:1px solid rgba(255,255,255,.08)">
        <h2 style="color:white;margin:0">Paldex — {len(df_c)} Pals</h2>
    </div>""", unsafe_allow_html=True)

    f1,f2,f3,f4 = st.columns([4,3,3,3])
    with f1: srch = st.text_input("Rechercher",placeholder="Nom...",label_visibility="collapsed",key="pdx_s")
    with f2:
        el_list = ["Tous"]+sorted(df_c['Element 1'].dropna().unique().tolist())
        fe = st.selectbox("Element",el_list,label_visibility="collapsed",key="pdx_e")
    with f3:
        ta_list = ["Toutes"]+sorted(df_c['Volume size'].dropna().unique().tolist())
        ft = st.selectbox("Taille",ta_list,label_visibility="collapsed",key="pdx_t")
    with f4:
        tri = st.selectbox("Tri",["Paldex","Score","HP","Attaque","Defense","Rarete"],
                           label_visibility="collapsed",key="pdx_tri")

    TRI = {"Paldex":None,"Score":"combat_score","HP":"HP",
           "Attaque":"melee attack","Defense":"defense","Rarete":"rarity"}
    dff = df_c.copy()
    if srch: dff = dff[dff['Name'].str.contains(srch,case=False,na=False)]
    if fe!="Tous": dff = dff[dff['Element 1']==fe]
    if ft!="Toutes": dff = dff[dff['Volume size']==ft]
    if TRI[tri]: dff = dff.sort_values(TRI[tri],ascending=False)
    st.caption(f"{len(dff)} Pals")

    for chunk in [dff.iloc[i:i+6] for i in range(0,len(dff),6)]:
        cols_g = st.columns(6)
        for j,(_,row) in enumerate(chunk.iterrows()):
            with cols_g[j]:
                st.markdown(card(row,80), unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# FICHE PAL
# ════════════════════════════════════════════════════════════════════════
with t2:
    st.markdown(bg_css("fiche"), unsafe_allow_html=True)
    play_sound("fiche")
    cs,_ = st.columns([3,5])
    with cs:
        pal_sel = st.selectbox("Pal",df_m['Name'].tolist(),
                               label_visibility="collapsed",key="fiche_pal")

    row    = df_m[df_m['Name']==pal_sel].iloc[0]
    elem   = str(row.get('Element 1','generally'))
    elem2  = str(row.get('Element 2',''))
    color  = ELEM_COLOR.get(elem,'#1565C0')

    # Header fiche
    st.markdown(f"""
    <div style="background:{TAB_BG[2]};border-radius:16px;padding:20px 28px;margin-bottom:16px;
        border:1px solid {color}44">
        <h2 style="color:white;margin:0">{pal_sel}</h2>
    </div>""", unsafe_allow_html=True)

    names_l = df_m['Name'].tolist()
    idx = names_l.index(pal_sel)
    n1,n2,n3 = st.columns([1,6,1])
    with n1:
        if idx>0 and st.button("Prec.",key="btn_p"): st.session_state['fiche_pal']=names_l[idx-1]; st.rerun()
    with n3:
        if idx<len(names_l)-1 and st.button("Suiv.",key="btn_n"): st.session_state['fiche_pal']=names_l[idx+1]; st.rerun()

    left,mid,right = st.columns([2,3,3])

    with left:
        badges = elem_img(elem,22)
        if elem2 and elem2 not in ['nan','None','']: badges += " "+elem_img(elem2,22)
        taille = TAILLE_FR.get(str(row.get('Volume size','')),'—')
        st.markdown(f"""
        <div style="text-align:center;padding:24px 16px;border-radius:16px;
            background:{TAB_BG[2]};border:2px solid {color}60">
            {pal_img(pal_sel,140)}
            <h2 style="color:{color};margin:10px 0 6px">{pal_sel}</h2>
            <div style="margin-bottom:12px">{badges}</div>
            <table style="width:100%;font-size:.83rem;color:rgba(255,255,255,.8)">
              <tr><td>Taille</td><td style="text-align:right;font-weight:600">{taille}</td></tr>
              <tr><td>Rarete</td><td style="text-align:right;font-weight:600">{"★"*min(int(row.get("rarity",0)),5)} ({int(row.get("rarity",0))})</td></tr>
              <tr><td>Capture</td><td style="text-align:right;font-weight:600">{row.get("catch rate","—")}</td></tr>
            </table>
        </div>
        <div style="text-align:center;margin-top:10px;padding:12px;
            background:linear-gradient(90deg,{color},{color}AA);
            border-radius:12px;color:white">
            <div style="font-size:1.4rem;font-weight:800">Score {int(row["combat_score"])}</div>
            <div style="font-size:.82rem;opacity:.85">Rang #{int(row.get("rang",0))} / {len(df_c)}</div>
        </div>""", unsafe_allow_html=True)

    with mid:
        st.markdown("#### Stats de combat")
        mx = {k: float(df_c[k].max()) if k in df_c.columns else 1
              for k in ['HP','melee attack','Remote attack','defense','support','Speed of work']}
        bars = (stat_bar("Points de vie",    row.get('HP',0),           mx['HP'],           "#E74C3C")+
                stat_bar("Attaque melee",    row.get('melee attack',0), mx['melee attack'], "#E67E22")+
                stat_bar("Attaque distance", row.get('Remote attack',0),mx['Remote attack'],"#F39C12")+
                stat_bar("Defense",          row.get('defense',0),      mx['defense'],      "#3498DB")+
                stat_bar("Support",          row.get('support',0),      mx['support'],      "#9B59B6")+
                stat_bar("Vitesse craft",    row.get('Speed of work',0),mx['Speed of work'],"#2ECC71"))
        st.markdown(f'<div style="background:rgba(255,255,255,.04);border-radius:12px;padding:16px;border:1px solid rgba(255,255,255,.08)">{bars}</div>', unsafe_allow_html=True)

        st.markdown("#### Radar")
        cats=['PV','Att.','Dist.','Def.','Sout.','Craft']
        keys=['HP','melee attack','Remote attack','defense','support','Speed of work']
        norm=[float(row.get(k,0))/mx[k]*100 if mx[k]>0 else 0 for k in keys]
        top1=df_c.nlargest(1,'combat_score').iloc[0]
        norm_t=[float(top1.get(k,0))/mx[k]*100 if mx[k]>0 else 0 for k in keys]
        fig_r=go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=norm+[norm[0]],theta=cats+[cats[0]],fill='toself',
            name=pal_sel,line_color=color,fillcolor=hex_to_rgba(color,.2)))
        if top1['Name']!=pal_sel:
            fig_r.add_trace(go.Scatterpolar(r=norm_t+[norm_t[0]],theta=cats+[cats[0]],fill='toself',
                name=top1['Name'],line_color="#BDC3C7",fillcolor=hex_to_rgba("#BDC3C7",.1)))
        fig_r.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True,range=[0,100],showticklabels=False,
                           gridcolor='rgba(255,255,255,.1)',linecolor='rgba(255,255,255,.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,.1)',linecolor='rgba(255,255,255,.1)',
                            tickfont=dict(color='white'))),
            showlegend=True,height=280,margin=dict(t=10,b=10,l=30,r=30),
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color='white'),bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_r, width='stretch')

    with right:
        st.markdown("#### Competences de travail")
        skill_dispo=[(sk,SKILL_FR[sk],int(float(row[sk]))) for sk in SK
                     if sk in row.index and pd.notna(row[sk]) and float(row[sk])>0]
        if skill_dispo:
            for sk_key,sk_name,lv in skill_dispo:
                bc="#2ECC71" if lv>=3 else "#F39C12" if lv>=2 else "#7F8C8D"
                ic=skill_img(sk_key,20)
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:8px 12px;background:rgba(255,255,255,.04);border-radius:8px;
                    margin:3px 0;border-left:3px solid {bc}">
                    <span style="font-size:.83rem;color:white;display:flex;align-items:center;gap:6px">
                        {ic} {sk_name}
                    </span>
                    <span style="background:{bc};color:white;padding:1px 9px;
                        border-radius:10px;font-weight:700;font-size:.78rem">Niv {lv}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Aucune competence.")

        rv=row.get('ranch items','')
        if pd.notna(rv) and str(rv).strip() not in ['','nan']:
            st.markdown(f"""
            <div style="margin-top:10px;padding:10px 14px;background:rgba(46,204,113,.1);
                border-radius:10px;border-left:4px solid #2ECC71">
                <div style="color:white;font-weight:700;font-size:.85rem">Ranch</div>
                <div style="color:rgba(255,255,255,.8);font-size:.82rem">{rv} — {row.get("pasture minimum output","—")}</div>
            </div>""", unsafe_allow_html=True)

        if row.get('nuit',False):
            st.markdown("""
            <div style="margin-top:8px;padding:8px 14px;background:rgba(142,68,173,.15);
                border-radius:10px;border-left:4px solid #8E44AD">
                <span style="color:white;font-weight:700;font-size:.83rem">Travail de nuit possible</span>
            </div>""", unsafe_allow_html=True)

        cr=row.get('catch_rate_num',None)
        if cr is not None and pd.notna(cr):
            cc="#2ECC71" if cr>=100 else "#F39C12" if cr>=50 else "#E74C3C"
            st.markdown(f"""
            <div style="margin-top:8px;padding:8px 14px;background:rgba(255,255,255,.05);
                border-radius:10px;border-left:4px solid {cc}">
                <span style="color:white">Taux de capture :
                <strong style="color:{cc}">{int(cr)}%</strong></span>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# COMBAT
# ════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown(bg_css("combat"), unsafe_allow_html=True)
    play_sound("combat")
    st.markdown(f"""
    <div style="background:{TAB_BG[3]};border-radius:16px;padding:20px 28px;margin-bottom:20px;
        border:1px solid rgba(231,76,60,.3)">
        <h2 style="color:white;margin:0">Strategie de combat</h2>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Top 10 Pals")
    top10=df_c.nlargest(10,'combat_score')
    for grp in [top10.head(5),top10.tail(5)]:
        cols5=st.columns(5)
        for i,(_,row) in enumerate(grp.iterrows()):
            with cols5[i]: st.markdown(card(row,75), unsafe_allow_html=True)

    fig_t=px.bar(top10,x='Name',y='combat_score',color='melee attack',
                 color_continuous_scale='Reds',title='Top 10 — Score de combat',
                 template="plotly_dark",
                 labels={'Name':'Pal','combat_score':'Score','melee attack':'Attaque'})
    fig_t.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                        title_font_color='white')
    st.plotly_chart(fig_t, width='stretch')

    st.divider()
    c1,c2=st.columns(2)
    with c1:
        rs=df_c.groupby('rarity')[['HP','melee attack','defense']].mean().round(1).reset_index()
        fig2=px.line(rs,x='rarity',y=['HP','melee attack','defense'],markers=True,
                     title="Rarete et attributs moyens",template="plotly_dark",
                     labels={'rarity':'Rarete','value':'Valeur','variable':'Attribut'})
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                           title_font_color='white')
        st.plotly_chart(fig2, width='stretch')
    with c2:
        ncols=[c for c in ['HP','melee attack','Remote attack','defense'] if c in df_c.columns]
        fig_c,ax=plt.subplots(figsize=(5,4),facecolor='none')
        ax.set_facecolor('none')
        sns.heatmap(df_c[ncols].corr(),annot=True,cmap='coolwarm',fmt='.2f',ax=ax,
                    cbar=False,linewidths=.5,
                    annot_kws={'color':'white'},linecolor=(1,1,1,0.1))
        ax.set_title("Correlations",color='white')
        for t_item in ax.get_xticklabels()+ax.get_yticklabels():
            t_item.set_color('white')
        fig_c.patch.set_alpha(0)
        st.pyplot(fig_c); plt.close()

    st.divider()
    st.markdown("### Equipe equilibree")
    spd=next((c for c in ['running speed','Running speed'] if c in df_c.columns),None)
    equipe=[("Tank",df_c.nlargest(1,'HP').iloc[0],"HP"),
            ("Attaquant",df_c.nlargest(1,'melee attack').iloc[0],"melee attack"),
            ("Defenseur",df_c.nlargest(1,'defense').iloc[0],"defense"),
            ("Polyvalent",df_c.nlargest(1,'combat_score').iloc[0],"combat_score")]
    if spd: equipe.insert(3,("Rapide",df_c.nlargest(1,spd).iloc[0],spd))
    eq_cols=st.columns(len(equipe))
    for i,(role,row,stat) in enumerate(equipe):
        elem=str(row.get('Element 1','generally'))
        color=ELEM_COLOR.get(elem,'#1565C0')
        with eq_cols[i]:
            st.markdown(
                f'<div style="text-align:center;padding:12px;border-radius:14px;'
                f'background:linear-gradient(160deg,{color}30,rgba(0,0,0,.3));'
                f'border:2px solid {color}60">'
                f'<div style="font-size:.78rem;color:{color};font-weight:700;margin-bottom:6px">{role}</div>'
                f'{pal_img(str(row["Name"]),70)}'
                f'<div style="font-weight:700;font-size:.85rem;margin-top:6px;color:white">{row["Name"]}</div>'
                f'{elem_img(elem)}'
                f'<div style="font-size:.75rem;color:{color};font-weight:700;margin-top:4px">'
                f'{stat.replace("_"," ").title()}: {int(row[stat])}</div></div>',
                unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# CAMPEMENT
# ════════════════════════════════════════════════════════════════════════
with t4:
    st.markdown(bg_css("campement"), unsafe_allow_html=True)
    play_sound("campement")
    st.markdown(f"""
    <div style="background:{TAB_BG[4]};border-radius:16px;padding:20px 28px;margin-bottom:20px;
        border:1px solid rgba(39,174,96,.3)">
        <h2 style="color:white;margin:0">Production du campement</h2>
    </div>""", unsafe_allow_html=True)

    c1,c2=st.columns(2)
    with c1:
        st.markdown("### Ranch")
        rc=next((c for c in ['ranch items','Ranch items'] if c in df_j.columns),None)
        if rc:
            ranch=df_j[df_j[rc].notna()&(df_j[rc].astype(str).str.strip().isin(['','nan'])==False)][
                ['English name',rc,'pasture minimum output']].copy()
            ranch.columns=['Pal','Produit','Production']
            st.metric("Pals productifs",len(ranch))
            for _,r in ranch.iterrows():
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:8px 12px;'
                    f'background:rgba(39,174,96,.1);border-radius:8px;margin:3px;'
                    f'border-left:4px solid #2ECC71">'
                    f'{pal_img(r["Pal"],40)}'
                    f'<div><div style="font-weight:700;color:white;font-size:.85rem">{r["Pal"]}</div>'
                    f'<div style="font-size:.78rem;color:rgba(255,255,255,.6)">{r["Produit"]} — {r["Production"]}</div>'
                    f'</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### Competences de travail")
        if SK:
            sk=df_j[SK].sum().reset_index()
            sk.columns=['Competence','Total']
            sk['Icon'] = sk['Competence'].map(lambda x: SKILL_FR.get(x,x))
            sk['Competence'] = sk['Icon']
            sk=sk.sort_values('Total',ascending=False)
            fig=px.bar(sk,x='Competence',y='Total',color='Total',
                       color_continuous_scale='Greens',
                       title="Nb Pals par competence",template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                              title_font_color='white',coloraxis_showscale=False)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, width='stretch')

    st.divider()
    st.markdown("### Travail de nuit")
    if 'nuit' in df_j.columns:
        nuit=df_j[df_j['nuit']==True]
        mn=nuit.merge(df_c[['Name','Element 1','HP','melee attack','rarity']],
                      left_on='English name',right_on='Name',how='left')
        st.metric("Pals nocturnes",len(nuit))
        if len(mn)>0:
            nc=min(len(mn),6)
            cols_n=st.columns(nc)
            for i,(_,r) in enumerate(mn.head(nc).iterrows()):
                nm=str(r.get('Name',r.get('English name','')))
                elem=str(r.get('Element 1','generally'))
                color=ELEM_COLOR.get(elem,'#607D8B')
                with cols_n[i]:
                    st.markdown(
                        f'<div style="text-align:center;padding:10px;border-radius:12px;'
                        f'background:rgba(142,68,173,.15);border:2px solid {color}50">'
                        f'{pal_img(nm,65)}'
                        f'<div style="font-size:.8rem;font-weight:700;margin-top:4px;color:white">{nm}</div>'
                        f'{elem_img(elem)}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# ZONES
# ════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown(bg_css("zones"), unsafe_allow_html=True)
    play_sound("zones")
    st.markdown(f"""
    <div style="background:{TAB_BG[5]};border-radius:16px;padding:20px 28px;margin-bottom:20px;
        border:1px solid rgba(41,128,185,.3)">
        <h2 style="color:white;margin:0">Zones et niveaux d'apparition</h2>
    </div>""", unsafe_allow_html=True)
    try:
        dr=df_ref.copy()
        if dr.shape[1]>=4:
            dr=dr[[1,2,3]].dropna(subset=[1])
            dr.columns=['Pal','Niveau min','Niveau max']
            dr=dr[dr['Pal'].astype(str).str.strip()!='name']
            dr['Niveau min']=pd.to_numeric(dr['Niveau min'],errors='coerce')
            dr['Niveau max']=pd.to_numeric(dr['Niveau max'],errors='coerce')
            dr=dr.dropna().astype({'Niveau min':int,'Niveau max':int})

            z1,z2=st.columns(2)
            with z1:
                dr['Tranche']=pd.cut(dr['Niveau min'],bins=[0,10,20,30,100],
                    labels=['1-10 Debutant','11-20 Intermediaire','21-30 Avance','31+ Expert'])
                tc=dr['Tranche'].value_counts().reset_index(); tc.columns=['Tranche','Nb']
                fig=px.pie(tc,names='Tranche',values='Nb',
                           title="Repartition par tranche",template="plotly_dark",
                           color_discrete_sequence=px.colors.sequential.Blues_r)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',title_font_color='white')
                st.plotly_chart(fig, width='stretch')
            with z2:
                fig2=px.histogram(dr,x='Niveau min',nbins=20,
                                  title="Distribution des niveaux min",template="plotly_dark",
                                  color_discrete_sequence=['#2980B9'])
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                                   title_font_color='white')
                st.plotly_chart(fig2, width='stretch')

            st.markdown("### Pals par niveau")
            lv=st.slider("Niveau",1,int(dr['Niveau max'].max()),10,key="zones_niv")
            pls=dr[(dr['Niveau min']<=lv)&(dr['Niveau max']>=lv)]
            st.caption(f"{len(pls)} Pals au niveau {lv}")
            if len(pls)>0:
                nc=min(len(pls),6)
                cols_lv=st.columns(nc)
                for i,(_,r) in enumerate(pls.head(nc).iterrows()):
                    pr=df_c[df_c['Name']==r['Pal']]
                    elem=str(pr.iloc[0]['Element 1']) if not pr.empty else 'generally'
                    color=ELEM_COLOR.get(elem,'#607D8B')
                    with cols_lv[i]:
                        st.markdown(
                            f'<div style="text-align:center;padding:8px;border-radius:12px;'
                            f'background:linear-gradient(160deg,{color}25,rgba(0,0,0,.3));'
                            f'border:2px solid {color}50">'
                            f'{pal_img(r["Pal"],60)}'
                            f'<div style="font-size:.78rem;font-weight:700;margin-top:4px;color:white">{r["Pal"]}</div>'
                            f'<div style="font-size:.68rem;color:rgba(255,255,255,.5)">Niv {int(r["Niveau min"])}-{int(r["Niveau max"])}</div>'
                            f'{elem_img(elem)}</div>', unsafe_allow_html=True)
            st.dataframe(dr.sort_values('Niveau min'), width='stretch', hide_index=True)
    except Exception as e:
        st.warning(f"Erreur zones : {e}")

# ════════════════════════════════════════════════════════════════════════
# BOSS
# ════════════════════════════════════════════════════════════════════════
with t6:
    st.markdown(bg_css("boss"), unsafe_allow_html=True)
    play_sound("boss")
    st.markdown(f"""
    <div style="background:{TAB_BG[6]};border-radius:16px;padding:20px 28px;margin-bottom:20px;
        border:1px solid rgba(230,126,34,.3)">
        <h2 style="color:white;margin:0">Boss — Tower &amp; Ordinary</h2>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Tower Boss")
    try:
        sc=df_tower.columns[0]
        bnames=[c for c in df_tower.columns if c!=sc]
        boss_pals=["Grizzbolt","Lyleen","Faleris","Orserk","Shadowbeak"]
        tb_cols=st.columns(min(len(bnames),5))
        for i,boss in enumerate(bnames[:5]):
            pn=boss_pals[i] if i<len(boss_pals) else boss
            pr=df_c[df_c['Name']==pn]
            elem=str(pr.iloc[0]['Element 1']) if not pr.empty else 'generally'
            color=ELEM_COLOR.get(elem,'#E67E22')
            hp_r=df_tower[df_tower[sc].astype(str).str.upper().str.contains('HP',na=False)]
            ak_r=df_tower[df_tower[sc].astype(str).str.lower().str.contains('attack',na=False)]
            hp_v=int(float(hp_r[boss].values[0])) if len(hp_r)>0 else 0
            at_v=int(float(ak_r[boss].values[0])) if len(ak_r)>0 else 0
            with tb_cols[i]:
                st.markdown(
                    f'<div style="text-align:center;padding:14px;border-radius:14px;'
                    f'background:linear-gradient(160deg,{color}30,rgba(0,0,0,.4));'
                    f'border:2px solid {color}60">'
                    f'{pal_img(pn,75)}'
                    f'<div style="font-weight:700;font-size:.8rem;margin:6px 0 3px;color:white">{boss[:25]}</div>'
                    f'{elem_img(elem)}'
                    f'<div style="font-size:.78rem;color:#E74C3C;font-weight:700;margin-top:4px">HP {hp_v:,}</div>'
                    f'<div style="font-size:.72rem;color:#E67E22">Att {at_v}</div></div>',
                    unsafe_allow_html=True)
        st.dataframe(df_tower, width='stretch')
    except Exception as e:
        st.warning(f"Erreur Tower Boss : {e}")

    st.divider()
    st.markdown("### Ordinary Boss")
    st.dataframe(df_boss.dropna(how='all').reset_index(drop=True).head(20),
                 width='stretch', hide_index=True)

# ════════════════════════════════════════════════════════════════════════
# EXPLORATEUR
# ════════════════════════════════════════════════════════════════════════
with t7:
    st.markdown(bg_css("explorateur"), unsafe_allow_html=True)
    play_sound("explorateur")
    st.markdown(f"""
    <div style="background:{TAB_BG[7]};border-radius:16px;padding:20px 28px;margin-bottom:20px;
        border:1px solid rgba(255,255,255,.1)">
        <h2 style="color:white;margin:0">Explorateur de Pals</h2>
    </div>""", unsafe_allow_html=True)

    e1,e2,e3,e4=st.columns([2,2,2,3])
    with e1:
        ts=["Toutes"]+sorted(df_c['Volume size'].dropna().unique().tolist())
        tf=st.selectbox("Taille",ts,label_visibility="collapsed",key="exp_t")
    with e2:
        es=["Tous"]+sorted(df_c['Element 1'].dropna().unique().tolist())
        ef=st.selectbox("Element",es,label_visibility="collapsed",key="exp_e")
    with e3:
        ma=st.number_input("Att. min",value=0,min_value=0,
                           max_value=int(df_c['melee attack'].max()),
                           label_visibility="collapsed",key="exp_a")
    with e4:
        mr=st.slider("Rarete min",0,int(df_c['rarity'].max()),0,key="exp_r")

    dex=df_c.copy()
    if tf!="Toutes": dex=dex[dex['Volume size']==tf]
    if ef!="Tous":   dex=dex[dex['Element 1']==ef]
    dex=dex[(dex['melee attack']>=ma)&(dex['rarity']>=mr)]
    st.caption(f"{len(dex)} Pals")

    for chunk in [dex.iloc[i:i+6] for i in range(0,len(dex),6)]:
        cx=st.columns(6)
        for j,(_,row) in enumerate(chunk.iterrows()):
            with cx[j]: st.markdown(card(row,75), unsafe_allow_html=True)

    if len(dex)>1:
        st.divider()
        ca,cb=st.columns(2)
        with ca:
            fig=px.scatter(dex,x='melee attack',y='HP',color='rarity',
                           size='defense',hover_name='Name',
                           color_continuous_scale='Viridis',template="plotly_dark",
                           title="HP vs Attaque")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                              title_font_color='white')
            st.plotly_chart(fig, width='stretch')
        with cb:
            ct=['Name','HP','melee attack','defense','rarity','Volume size','Element FR','combat_score']
            ct=[c for c in ct if c in dex.columns]
            st.dataframe(dex[ct].rename(columns={
                'Name':'Pal','melee attack':'Attaque','defense':'Defense',
                'rarity':'Rarete','Volume size':'Taille','Element FR':'Element',
                'combat_score':'Score'}).sort_values('Attaque',ascending=False),
                width='stretch', hide_index=True)
