"""
app.py - Palstream v4
Lancement : streamlit run app/app.py
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

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Palstream - Analyse Palworld",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE     = Path(__file__).parent.resolve()
DATA_DIR = str(BASE.parent / "data")
PAL_IMG  = BASE / "assets" / "pals"
ELEM_IMG = BASE / "assets" / "elements"

# ── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display:none!important }
.stTabs [data-baseweb="tab-list"] {
    gap:0; background:#0D47A1; border-radius:0;
    padding:0 12px; position:sticky; top:0; z-index:100;
}
.stTabs [data-baseweb="tab"] {
    color:rgba(255,255,255,.7)!important; font-weight:600;
    font-size:.85rem; padding:12px 18px;
    border-bottom:3px solid transparent; border-radius:0;
    background:transparent!important;
}
.stTabs [aria-selected="true"] {
    color:white!important;
    border-bottom:3px solid #42A5F5!important;
    background:rgba(255,255,255,.08)!important;
}
.stTabs [data-baseweb="tab"]:hover { color:white!important }
.stTabs [data-baseweb="tab-panel"] { padding:20px 0 0 0 }
div[data-testid="metric-container"] {
    background:#F0F7FF; border-radius:10px;
    padding:12px 16px; border-left:4px solid #1565C0;
}
</style>
""", unsafe_allow_html=True)

# ── Traductions ────────────────────────────────────────────────────────────
ELEM_FR = {
    "fire":"Feu","water":"Eau","Wood":"Plante",
    "electricity":"Electricite","ice":"Glace",
    "dark":"Tenebres","dragon":"Dragon",
    "land":"Terre","generally":"Normal",
}
ELEM_COLOR = {
    "fire":"#E74C3C","water":"#2980B9","Wood":"#27AE60",
    "electricity":"#F1C40F","ice":"#85C1E9","dark":"#8E44AD",
    "dragon":"#E67E22","land":"#A04000","generally":"#7F8C8D",
}
SKILL_FR = {
    'Make a fire':'Feu','watering':'Arrosage','planting':'Plantation',
    'generate electricity':'Electricite','manual':'Manuel',
    'collection':'Collecte','logging':'Abattage','Mining':'Minage',
    'pharmaceutical':'Pharmacie','cool down':'Refroidissement',
    'pasture':'Elevage','carry':'Transport',
}
TAILLE_FR = {
    "XS":"XS - Minuscule","S":"S - Petit","M":"M - Moyen",
    "L":"L - Grand","XL":"XL - Tres grand"
}

# ── Image helpers ──────────────────────────────────────────────────────────
def hex_to_rgba(hex_color, alpha=0.2):
    h = hex_color.lstrip('#')
    r,g,b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def img_b64(path):
    try:
        with open(str(path), "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

def pal_img_tag(name, size=100):
    safe = name.replace(" ","_").replace("(","").replace(")","")
    path = PAL_IMG / f"{safe}.png"
    b64  = img_b64(path)
    if b64:
        return (f'<img src="data:image/png;base64,{b64}" '
                f'width="{size}" height="{size}" '
                f'style="object-fit:contain;border-radius:50%"/>')
    # Fallback SVG
    elem  = "generally"
    color = ELEM_COLOR.get(elem,"#888")
    init  = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
            f'<circle cx="{size//2}" cy="{size//2}" r="{size//2-2}" fill="{color}"/>'
            f'<text x="{size//2}" y="{size//2+5}" text-anchor="middle" '
            f'font-size="{size//3}" font-weight="900" fill="white" '
            f'font-family="Arial">{init}</text></svg>')

def elem_img_tag(elem, size=22):
    path = ELEM_IMG / f"{elem}.png"
    b64  = img_b64(path)
    color = ELEM_COLOR.get(elem,"#888")
    fr    = ELEM_FR.get(elem, elem)
    if b64:
        return (f'<span style="display:inline-flex;align-items:center;gap:3px;'
                f'background:{color}22;border:1px solid {color}66;'
                f'border-radius:6px;padding:1px 6px;font-size:.75rem;font-weight:700">'
                f'<img src="data:image/png;base64,{b64}" width="{size}" height="{size}" '
                f'style="border-radius:50%"/> {fr}</span>')
    return (f'<span style="display:inline-flex;align-items:center;'
            f'background:{color};color:white;border-radius:6px;'
            f'padding:1px 8px;font-size:.75rem;font-weight:700">{fr}</span>')

def stat_bar(label, val, max_val, color="#1565C0"):
    pct = min(int(float(val)/float(max_val)*100),100) if max_val>0 else 0
    return (f'<div style="margin:4px 0">'
            f'<div style="display:flex;justify-content:space-between;font-size:.78rem;margin-bottom:2px">'
            f'<span style="color:#555">{label}</span>'
            f'<span style="font-weight:700;color:{color}">{int(float(val))}</span></div>'
            f'<div style="background:#E8EAF6;border-radius:5px;height:7px">'
            f'<div style="background:{color};width:{pct}%;height:7px;border-radius:5px"></div>'
            f'</div></div>')

def pal_card(row, size=90, show_score=True):
    elem  = str(row.get('Element 1','generally'))
    color = ELEM_COLOR.get(elem,'#607D8B')
    fr_e  = ELEM_FR.get(elem, elem)
    img   = pal_img_tag(str(row['Name']), size)
    score_html = f'<div style="font-size:.75rem;color:{color};font-weight:700">Score {int(row["combat_score"])}</div>' if show_score else ""
    return (f'<div style="text-align:center;padding:10px;border-radius:14px;'
            f'background:linear-gradient(160deg,{color}20,{color}06);'
            f'border:2px solid {color}55;margin:3px;min-height:185px">'
            f'{img}'
            f'<div style="font-weight:700;font-size:.82rem;margin:5px 0 3px;'
            f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{row["Name"]}</div>'
            f'{elem_img_tag(elem)}'
            f'<div style="font-size:.7rem;color:#666;margin-top:3px">'
            f'HP {int(row["HP"])} · Att {int(row["melee attack"])}</div>'
            f'{score_html}</div>')

# ══════════════════════════════════════════════════════════════════════════
# CHARGEMENT
# ══════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_all():
    df_c = pd.read_csv(os.path.join(DATA_DIR,"Palworld_Data--Palu_combat_attribute_table.csv"), skiprows=1)
    df_j = pd.read_csv(os.path.join(DATA_DIR,"Palworld_Data-Palu_Job_Skills_Table.csv"), skiprows=1)
    df_h = pd.read_csv(os.path.join(DATA_DIR,"Palworld_Data-hide_pallu_attributes.csv"))
    df_t = pd.read_csv(os.path.join(DATA_DIR,"Palworld_Data-Tower_BOSS_attribute_comparison.csv"))
    df_b = pd.read_csv(os.path.join(DATA_DIR,"Palworld_Data-comparison_of_ordinary_BOSS_attributes.csv"), skiprows=3)
    df_r = pd.read_csv(os.path.join(DATA_DIR,"Palworld_Data--Palu_refresh_level.csv"), skiprows=1, header=None)

    # Nettoyage numérique
    for col in ['HP','melee attack','Remote attack','defense','support','Speed of work','rarity','running speed']:
        if col in df_c.columns:
            df_c[col] = pd.to_numeric(df_c[col], errors='coerce').fillna(0)
    if 'catch rate' in df_c.columns:
        df_c['catch_rate_num'] = df_c['catch rate'].astype(str).str.replace('%','',regex=False).pipe(pd.to_numeric,errors='coerce')

    # Traduction élément
    df_c['Element FR'] = df_c['Element 1'].map(ELEM_FR).fillna(df_c['Element 1'])

    df_c['combat_score'] = df_c['HP'] + df_c['melee attack']*2 + df_c['defense']
    df_c['rang'] = df_c['combat_score'].rank(ascending=False,method='min').astype(int)

    # Nettoyage job
    SKILLS = [c for c in ['Make a fire','watering','planting','generate electricity',
              'manual','collection','logging','Mining','pharmaceutical',
              'cool down','pasture','carry'] if c in df_j.columns]
    for c in SKILLS:
        df_j[c] = pd.to_numeric(df_j[c], errors='coerce').fillna(0)
    for c in ['Handling speed','Total skills','Food intake']:
        if c in df_j.columns:
            df_j[c] = pd.to_numeric(df_j[c], errors='coerce')
    if 'night shift' in df_j.columns:
        df_j['nuit'] = df_j['night shift'].notna() & (
            df_j['night shift'].astype(str).str.strip().str.lower().isin(['true','1','yes','oui','x']))

    # Fusion
    merge_cols = ['English name'] + SKILLS + [c for c in
        ['Handling speed','Total skills','Food intake','nuit','ranch items','pasture minimum output']
        if c in df_j.columns]
    df_m = df_c.merge(df_j[merge_cols], left_on='Name', right_on='English name', how='left')
    return df_c, df_j, df_h, df_t, df_b, df_r, df_m

df_c, df_j, df_h, df_tower, df_boss, df_ref, df_m = load_all()
SKILLS = [c for c in ['Make a fire','watering','planting','generate electricity',
          'manual','collection','logging','Mining','pharmaceutical',
          'cool down','pasture','carry'] if c in df_j.columns]

# ══════════════════════════════════════════════════════════════════════════
# ONGLETS
# ══════════════════════════════════════════════════════════════════════════
tabs = st.tabs(["Accueil","Paldex","Fiche Pal","Combat","Campement","Zones","Boss","Explorateur"])
t_acc, t_pal, t_fiche, t_com, t_camp, t_zone, t_boss, t_exp = tabs

# ══════════════════════════════════════════════════════════════════════════
# ACCUEIL
# ══════════════════════════════════════════════════════════════════════════
with t_acc:
    st.markdown("## Palstream - Analyse des Pals de Palworld")
    st.markdown("Explorez les **138 Pals** : statistiques, Paldex, strategie de combat et production.")
    st.divider()

    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Pals analyses",   len(df_c))
    k2.metric("HP maximum",      int(df_c['HP'].max()))
    k3.metric("Attaque maximum", int(df_c['melee attack'].max()))
    k4.metric("Rarete maximum",  int(df_c['rarity'].max()))
    k5.metric("Elements",        int(df_c['Element 1'].nunique()))

    st.divider()
    st.markdown("### Top 5 Pals au combat")
    top5 = df_c.nlargest(5,'combat_score')
    cols = st.columns(5)
    for i,(_,row) in enumerate(top5.iterrows()):
        with cols[i]:
            st.markdown(pal_card(row, size=90), unsafe_allow_html=True)

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        sz = df_c['Volume size'].value_counts().reset_index()
        sz.columns = ['Taille','Nombre']
        st.plotly_chart(px.pie(sz,names='Taille',values='Nombre',
            title="Repartition des tailles",
            color_discrete_sequence=px.colors.sequential.Blues_r),
            width='stretch')
    with c2:
        el = df_c['Element 1'].value_counts().reset_index()
        el.columns = ['Element','Nombre']
        el['Traduit'] = el['Element'].map(ELEM_FR)
        el['Couleur'] = el['Element'].map(ELEM_COLOR)
        st.plotly_chart(px.bar(el,x='Traduit',y='Nombre',
            title="Distribution des elements",
            color='Element',
            color_discrete_map={e:ELEM_COLOR.get(e,'#888') for e in el['Element']}),
            width='stretch')

# ══════════════════════════════════════════════════════════════════════════
# PALDEX
# ══════════════════════════════════════════════════════════════════════════
with t_pal:
    st.markdown("## Paldex - Tous les Pals")

    f1,f2,f3,f4 = st.columns([3,2,2,2])
    with f1: recherche = st.text_input("Rechercher",placeholder="Nom...",label_visibility="collapsed",key="pdx_search")
    with f2:
        elems_list = ["Tous"] + sorted(df_c['Element 1'].dropna().unique().tolist())
        fe = st.selectbox("Element",elems_list,label_visibility="collapsed",key="pdx_elem")
    with f3:
        tailles_list = ["Toutes"] + sorted(df_c['Volume size'].dropna().unique().tolist())
        ft = st.selectbox("Taille",tailles_list,label_visibility="collapsed",key="pdx_taille")
    with f4:
        tri = st.selectbox("Tri",["Paldex","Score","HP","Attaque","Defense","Rarete"],
                           label_visibility="collapsed",key="pdx_tri")

    TRI = {"Paldex":None,"Score":"combat_score","HP":"HP",
           "Attaque":"melee attack","Defense":"defense","Rarete":"rarity"}
    dff = df_c.copy()
    if recherche: dff = dff[dff['Name'].str.contains(recherche,case=False,na=False)]
    if fe != "Tous":   dff = dff[dff['Element 1']==fe]
    if ft != "Toutes": dff = dff[dff['Volume size']==ft]
    if TRI[tri]:       dff = dff.sort_values(TRI[tri],ascending=False)

    st.caption(f"{len(dff)} Pals affiches")
    st.divider()

    N = 6
    for chunk in [dff.iloc[i:i+N] for i in range(0,len(dff),N)]:
        cols_g = st.columns(N)
        for j,(_,row) in enumerate(chunk.iterrows()):
            with cols_g[j]:
                elem  = str(row.get('Element 1','generally'))
                color = ELEM_COLOR.get(elem,'#607D8B')
                img   = pal_img_tag(str(row['Name']),80)
                st.markdown(
                    f'<div style="text-align:center;padding:10px;border-radius:14px;'
                    f'background:linear-gradient(160deg,{color}20,{color}05);'
                    f'border:2px solid {color}50;margin:2px;min-height:190px">'
                    f'{img}'
                    f'<div style="font-weight:700;font-size:.8rem;margin:5px 0 3px;'
                    f'overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{row["Name"]}</div>'
                    f'{elem_img_tag(elem)}'
                    f'<div style="font-size:.68rem;color:#666;margin-top:3px">'
                    f'HP {int(row["HP"])} · Att {int(row["melee attack"])}</div>'
                    f'<div style="font-size:.68rem;color:{color};font-weight:700">'
                    f'Rar. {int(row["rarity"])}</div></div>',
                    unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# FICHE PAL
# ══════════════════════════════════════════════════════════════════════════
with t_fiche:
    st.markdown("## Fiche detaillee")

    cs,_ = st.columns([3,5])
    with cs:
        pal_choisi = st.selectbox("Pal",df_m['Name'].tolist(),
                                  label_visibility="collapsed",key="fiche_pal")

    row    = df_m[df_m['Name']==pal_choisi].iloc[0]
    elem   = str(row.get('Element 1','generally'))
    elem2  = str(row.get('Element 2',''))
    color  = ELEM_COLOR.get(elem,'#1565C0')
    score  = int(row['combat_score'])
    rang   = int(row.get('rang',0))

    names_list = df_m['Name'].tolist()
    idx = names_list.index(pal_choisi)
    n1,n2,n3 = st.columns([1,6,1])
    with n1:
        if idx>0 and st.button("Precedent",key="btn_prev"):
            st.session_state['fiche_pal'] = names_list[idx-1]; st.rerun()
    with n3:
        if idx<len(names_list)-1 and st.button("Suivant",key="btn_next"):
            st.session_state['fiche_pal'] = names_list[idx+1]; st.rerun()

    st.divider()
    left,mid,right = st.columns([2,3,3])

    with left:
        img_lg = pal_img_tag(pal_choisi, 140)
        badges = elem_img_tag(elem,24)
        if elem2 and elem2 not in ['nan','None','']:
            badges += " " + elem_img_tag(elem2,24)
        taille = TAILLE_FR.get(str(row.get('Volume size','')),'—')
        st.markdown(f"""
        <div style="text-align:center;padding:22px 16px;border-radius:18px;
            background:linear-gradient(160deg,{color}28,{color}06);
            border:2.5px solid {color}70">
            {img_lg}
            <h2 style="margin:10px 0 6px;color:{color}">{pal_choisi}</h2>
            <div style="margin-bottom:12px">{badges}</div>
            <table style="width:100%;font-size:.83rem;border-collapse:collapse">
              <tr><td style="color:#888;padding:4px 0">Taille</td>
                  <td style="font-weight:600;text-align:right">{taille}</td></tr>
              <tr><td style="color:#888;padding:4px 0">Rarete</td>
                  <td style="font-weight:600;text-align:right">{"★"*min(int(row.get("rarity",0)),5)} ({int(row.get("rarity",0))})</td></tr>
              <tr><td style="color:#888;padding:4px 0">Capture</td>
                  <td style="font-weight:600;text-align:right">{row.get("catch rate","—")}</td></tr>
            </table>
        </div>
        <div style="text-align:center;margin-top:10px;padding:12px;
            background:linear-gradient(90deg,{color},{color}AA);
            border-radius:12px;color:white">
            <div style="font-size:1.3rem;font-weight:800">Score {score}</div>
            <div style="font-size:.82rem;opacity:.9">Classement #{rang} sur {len(df_c)}</div>
        </div>""", unsafe_allow_html=True)

    with mid:
        st.markdown("#### Stats de combat")
        mx = {
            'HP': float(df_c['HP'].max()),
            'melee attack': float(df_c['melee attack'].max()),
            'Remote attack': float(df_c['Remote attack'].max()) if 'Remote attack' in df_c.columns else 1,
            'defense': float(df_c['defense'].max()),
            'support': float(df_c['support'].max()) if 'support' in df_c.columns else 1,
            'Speed of work': float(df_c['Speed of work'].max()) if 'Speed of work' in df_c.columns else 1,
        }
        bars = (
            stat_bar("Points de vie",    row.get('HP',0),           mx['HP'],           "#E74C3C") +
            stat_bar("Attaque melee",    row.get('melee attack',0), mx['melee attack'], "#E67E22") +
            stat_bar("Attaque distance", row.get('Remote attack',0),mx['Remote attack'],"#F39C12") +
            stat_bar("Defense",          row.get('defense',0),      mx['defense'],      "#2980B9") +
            stat_bar("Support",          row.get('support',0),      mx['support'],      "#8E44AD") +
            stat_bar("Vitesse craft",    row.get('Speed of work',0),mx['Speed of work'],"#27AE60")
        )
        st.markdown(f'<div style="background:#F8F9FA;border-radius:12px;padding:16px;border:1px solid #E8EAF6">{bars}</div>',
                    unsafe_allow_html=True)

        st.markdown("#### Radar comparatif")
        cats = ['PV','Att.','Dist.','Def.','Sout.','Craft']
        keys = ['HP','melee attack','Remote attack','defense','support','Speed of work']
        norm = [float(row.get(k,0))/mx[k]*100 if mx[k]>0 else 0 for k in keys]
        norm_c = norm+[norm[0]]
        cats_c = cats+[cats[0]]
        top1 = df_c.nlargest(1,'combat_score').iloc[0]
        norm_t = [float(top1.get(k,0))/mx[k]*100 if mx[k]>0 else 0 for k in keys]
        norm_tc= norm_t+[norm_t[0]]

        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=norm_c, theta=cats_c, fill='toself',
            name=pal_choisi, line_color=color, fillcolor=hex_to_rgba(color,0.2)))
        if top1['Name'] != pal_choisi:
            fig_r.add_trace(go.Scatterpolar(r=norm_tc, theta=cats_c, fill='toself',
                name=top1['Name'], line_color="#BDC3C7", fillcolor=hex_to_rgba("#BDC3C7",0.15)))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100],showticklabels=False)),
                            showlegend=True, height=280, margin=dict(t=10,b=10,l=30,r=30))
        st.plotly_chart(fig_r, width='stretch')

    with right:
        st.markdown("#### Competences de travail")
        skill_dispo = [(SKILL_FR.get(sc,sc), int(float(row[sc])))
                       for sc in SKILLS if sc in row.index and pd.notna(row[sc]) and float(row[sc])>0]
        if skill_dispo:
            for sk,lv in skill_dispo:
                bc = "#27AE60" if lv>=3 else "#F39C12" if lv>=2 else "#95A5A6"
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                    padding:7px 12px;background:#F8F9FA;border-radius:8px;margin:3px 0;
                    border-left:3px solid {bc}">
                    <span style="font-size:.83rem">{sk}</span>
                    <span style="background:{bc};color:white;padding:1px 9px;
                        border-radius:10px;font-weight:700;font-size:.78rem">Niv {lv}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("Aucune competence de travail.")

        ranch_v = row.get('ranch items','')
        if pd.notna(ranch_v) and str(ranch_v).strip() not in ['','nan']:
            st.markdown(f"""
            <div style="margin-top:10px;padding:10px 14px;background:#E8F5E9;
                border-radius:10px;border-left:4px solid #27AE60">
                <div style="font-weight:700;font-size:.85rem">Produit du ranch</div>
                <div style="font-size:.82rem;margin-top:3px">{ranch_v}</div>
                <div style="font-size:.78rem;color:#555">Production : {row.get("pasture minimum output","—")}</div>
            </div>""", unsafe_allow_html=True)

        if row.get('nuit',False):
            st.markdown("""
            <div style="margin-top:8px;padding:8px 14px;background:#EDE7F6;
                border-radius:10px;border-left:4px solid #8E44AD">
                <span style="font-weight:700;font-size:.83rem">Travail de nuit possible</span>
            </div>""", unsafe_allow_html=True)

        cr = row.get('catch_rate_num',None)
        if cr is not None and pd.notna(cr):
            cc = "#27AE60" if cr>=100 else "#F39C12" if cr>=50 else "#E74C3C"
            st.markdown(f"""
            <div style="margin-top:8px;padding:8px 14px;background:#FFF8E1;
                border-radius:10px;border-left:4px solid {cc}">
                Taux de capture : <strong style="color:{cc}">{int(cr)}%</strong>
            </div>""", unsafe_allow_html=True)

        food = row.get('Food intake',None)
        if food is not None and pd.notna(food):
            st.markdown(f"""
            <div style="margin-top:8px;padding:8px 14px;background:#E3F2FD;
                border-radius:10px;border-left:4px solid #1565C0">
                Nourriture : <strong>{int(float(food))}/10</strong>
            </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# COMBAT
# ══════════════════════════════════════════════════════════════════════════
with t_com:
    st.markdown("## Strategie de combat")
    st.divider()
    st.markdown("### Top 10 Pals")
    top10 = df_c.nlargest(10,'combat_score')
    for grp in [top10.head(5), top10.tail(5)]:
        cols5 = st.columns(5)
        for i,(_,row) in enumerate(grp.iterrows()):
            with cols5[i]:
                st.markdown(pal_card(row,size=80), unsafe_allow_html=True)

    fig_top = px.bar(top10, x='Name', y='combat_score', color='melee attack',
                     color_continuous_scale='Reds',
                     title='Top 10 - Score de combat (HP + Att x2 + Def)',
                     labels={'Name':'Pal','combat_score':'Score','melee attack':'Attaque'})
    st.plotly_chart(fig_top, width='stretch')

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        rs = df_c.groupby('rarity')[['HP','melee attack','defense']].mean().round(1).reset_index()
        st.plotly_chart(px.line(rs,x='rarity',y=['HP','melee attack','defense'],
            markers=True, title="Rarete et attributs moyens",
            labels={'rarity':'Rarete','value':'Valeur','variable':'Attribut'}),
            width='stretch')
    with c2:
        ncols = [c for c in ['HP','melee attack','Remote attack','defense'] if c in df_c.columns]
        fig_c, ax = plt.subplots(figsize=(5,4))
        sns.heatmap(df_c[ncols].corr(), annot=True, cmap='coolwarm', fmt='.2f', ax=ax, cbar=False)
        ax.set_title("Correlations entre attributs")
        st.pyplot(fig_c); plt.close()

    st.divider()
    st.markdown("### Equipe equilibree recommandee")
    spd = next((c for c in ['running speed','Running speed'] if c in df_c.columns), None)
    equipe = [
        ("Tank",      df_c.nlargest(1,'HP').iloc[0],          "HP"),
        ("Attaquant", df_c.nlargest(1,'melee attack').iloc[0],"melee attack"),
        ("Defenseur", df_c.nlargest(1,'defense').iloc[0],     "defense"),
        ("Polyvalent",df_c.nlargest(1,'combat_score').iloc[0],"combat_score"),
    ]
    if spd: equipe.insert(3,("Rapide", df_c.nlargest(1,spd).iloc[0], spd))
    eq_cols = st.columns(len(equipe))
    for i,(role,row,stat) in enumerate(equipe):
        elem  = str(row.get('Element 1','generally'))
        color = ELEM_COLOR.get(elem,'#1565C0')
        with eq_cols[i]:
            st.markdown(
                f'<div style="text-align:center;padding:12px;border-radius:14px;'
                f'background:linear-gradient(160deg,{color}22,{color}06);'
                f'border:2px solid {color}70">'
                f'<div style="font-size:.78rem;color:{color};font-weight:700;margin-bottom:6px">{role}</div>'
                f'{pal_img_tag(str(row["Name"]),70)}'
                f'<div style="font-weight:700;font-size:.85rem;margin-top:6px">{row["Name"]}</div>'
                f'{elem_img_tag(elem)}'
                f'<div style="font-size:.75rem;color:{color};font-weight:700;margin-top:4px">'
                f'{stat.replace("_"," ").title()} : {int(row[stat])}</div></div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# CAMPEMENT
# ══════════════════════════════════════════════════════════════════════════
with t_camp:
    st.markdown("## Production du campement")
    st.divider()

    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Pals productifs au ranch")
        rc = next((c for c in ['ranch items','Ranch items'] if c in df_j.columns), None)
        if rc:
            ranch = df_j[df_j[rc].notna()&(df_j[rc].astype(str).str.strip().isin(['','nan'])==False)][
                ['English name',rc,'pasture minimum output']].copy()
            ranch.columns=['Pal','Produit','Production']
            st.metric("Pals au ranch", len(ranch))
            for _,r in ranch.iterrows():
                img = pal_img_tag(r['Pal'], 40)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;padding:6px;'
                    f'background:#E8F5E9;border-radius:8px;margin:3px;border-left:4px solid #27AE60">'
                    f'{img}'
                    f'<div><b>{r["Pal"]}</b><br>'
                    f'<span style="font-size:.8rem">{r["Produit"]} - {r["Production"]}</span>'
                    f'</div></div>', unsafe_allow_html=True)

    with c2:
        st.markdown("### Competences de travail")
        if SKILLS:
            sk = df_j[SKILLS].sum().reset_index()
            sk.columns = ['Competence','Total']
            sk['Competence'] = sk['Competence'].map(SKILL_FR).fillna(sk['Competence'])
            sk = sk.sort_values('Total',ascending=False)
            st.plotly_chart(px.bar(sk,x='Competence',y='Total',color='Total',
                color_continuous_scale='Blues',
                title="Nb de Pals par competence").update_xaxes(tickangle=45),
                width='stretch')

    st.divider()
    st.markdown("### Pals pour le travail de nuit")
    if 'nuit' in df_j.columns:
        nuit = df_j[df_j['nuit']==True]
        merged_n = nuit.merge(df_c[['Name','Element 1','HP','melee attack','rarity']],
                              left_on='English name',right_on='Name',how='left')
        st.metric("Pals nocturnes", len(nuit))
        if len(merged_n)>0:
            nc = min(len(merged_n),6)
            cols_n = st.columns(nc)
            for i,(_,r) in enumerate(merged_n.head(nc).iterrows()):
                with cols_n[i]:
                    nm = str(r.get('Name',r.get('English name','')))
                    elem = str(r.get('Element 1','generally'))
                    color = ELEM_COLOR.get(elem,'#607D8B')
                    st.markdown(
                        f'<div style="text-align:center;padding:10px;border-radius:12px;'
                        f'background:linear-gradient(160deg,#1a237e18,#1a237e05);'
                        f'border:2px solid {color}50">'
                        f'{pal_img_tag(nm,65)}'
                        f'<div style="font-size:.8rem;font-weight:700;margin-top:4px">{nm}</div>'
                        f'{elem_img_tag(elem)}</div>',
                        unsafe_allow_html=True)

    st.divider()
    st.markdown("### Top 10 - Vitesse de travail")
    sc2 = next((c for c in ['Handling speed','handling speed'] if c in df_j.columns),None)
    if sc2:
        tw = df_j.nlargest(10,sc2)[['English name',sc2,'Total skills']].dropna(subset=[sc2])
        tw.columns=['Pal','Vitesse','Competences']
        st.plotly_chart(px.bar(tw,x='Pal',y='Vitesse',color='Competences',
            color_continuous_scale='Greens',title="Top 10 - Vitesse de travail"),
            width='stretch')

# ══════════════════════════════════════════════════════════════════════════
# ZONES
# ══════════════════════════════════════════════════════════════════════════
with t_zone:
    st.markdown("## Zones et niveaux d'apparition")
    st.divider()
    try:
        dr = df_ref.copy()
        if dr.shape[1]>=4:
            dr = dr[[1,2,3]].dropna(subset=[1])
            dr.columns=['Pal','Niveau min','Niveau max']
            dr = dr[dr['Pal'].astype(str).str.strip()!='name']
            dr['Niveau min'] = pd.to_numeric(dr['Niveau min'],errors='coerce')
            dr['Niveau max'] = pd.to_numeric(dr['Niveau max'],errors='coerce')
            dr = dr.dropna().astype({'Niveau min':int,'Niveau max':int})

            z1,z2 = st.columns(2)
            with z1:
                dr['Tranche'] = pd.cut(dr['Niveau min'],bins=[0,10,20,30,100],
                    labels=['1-10 Debutant','11-20 Intermediaire','21-30 Avance','31+ Expert'])
                tc = dr['Tranche'].value_counts().reset_index(); tc.columns=['Tranche','Nb']
                st.plotly_chart(px.pie(tc,names='Tranche',values='Nb',
                    title="Repartition par tranche",
                    color_discrete_sequence=px.colors.sequential.Blues_r),
                    width='stretch')
            with z2:
                st.plotly_chart(px.histogram(dr,x='Niveau min',nbins=20,
                    title="Distribution des niveaux min",
                    color_discrete_sequence=['#1565C0']),
                    width='stretch')

            st.markdown("### Pals apparaissant a un niveau")
            lv = st.slider("Niveau",1,int(dr['Niveau max'].max()),10,key="zones_niveau")
            pals_lv = dr[(dr['Niveau min']<=lv)&(dr['Niveau max']>=lv)]
            st.caption(f"{len(pals_lv)} Pals au niveau {lv}")
            if len(pals_lv)>0:
                nc = min(len(pals_lv),6)
                cols_lv = st.columns(nc)
                for i,(_,r) in enumerate(pals_lv.head(nc).iterrows()):
                    pal_r = df_c[df_c['Name']==r['Pal']]
                    elem = str(pal_r.iloc[0]['Element 1']) if not pal_r.empty else 'generally'
                    color = ELEM_COLOR.get(elem,'#607D8B')
                    with cols_lv[i]:
                        st.markdown(
                            f'<div style="text-align:center;padding:8px;border-radius:12px;'
                            f'background:linear-gradient(160deg,{color}18,{color}05);'
                            f'border:2px solid {color}50">'
                            f'{pal_img_tag(r["Pal"],60)}'
                            f'<div style="font-size:.78rem;font-weight:700;margin-top:4px">{r["Pal"]}</div>'
                            f'<div style="font-size:.68rem;color:#666">Niv {int(r["Niveau min"])}-{int(r["Niveau max"])}</div>'
                            f'{elem_img_tag(elem)}</div>',
                            unsafe_allow_html=True)
            st.dataframe(dr.sort_values('Niveau min'),width='stretch',hide_index=True)
    except Exception as e:
        st.warning(f"Erreur zones : {e}")

# ══════════════════════════════════════════════════════════════════════════
# BOSS
# ══════════════════════════════════════════════════════════════════════════
with t_boss:
    st.markdown("## Boss - Comparatif")
    st.divider()
    st.markdown("### Tower Boss")
    try:
        stat_col = df_tower.columns[0]
        boss_names = [c for c in df_tower.columns if c != stat_col]
        boss_pals = ["Grizzbolt","Lyleen","Faleris","Orserk","Shadowbeak"]

        tb_cols = st.columns(min(len(boss_names),5))
        for i,boss in enumerate(boss_names[:5]):
            pal_n = boss_pals[i] if i<len(boss_pals) else boss
            pal_r = df_c[df_c['Name']==pal_n]
            elem  = str(pal_r.iloc[0]['Element 1']) if not pal_r.empty else 'generally'
            color = ELEM_COLOR.get(elem,'#9c27b0')
            hp_row  = df_tower[df_tower[stat_col].astype(str).str.upper().str.contains('HP',na=False)]
            atk_row = df_tower[df_tower[stat_col].astype(str).str.lower().str.contains('attack',na=False)]
            hp_val  = int(float(hp_row[boss].values[0]))  if len(hp_row)>0  else 0
            atk_val = int(float(atk_row[boss].values[0])) if len(atk_row)>0 else 0
            with tb_cols[i]:
                st.markdown(
                    f'<div style="text-align:center;padding:14px;border-radius:14px;'
                    f'background:linear-gradient(160deg,{color}25,{color}06);'
                    f'border:2px solid {color}70">'
                    f'{pal_img_tag(pal_n,75)}'
                    f'<div style="font-weight:700;font-size:.8rem;margin:6px 0 3px">{boss[:28]}</div>'
                    f'{elem_img_tag(elem)}'
                    f'<div style="font-size:.75rem;color:#E74C3C;font-weight:700;margin-top:4px">HP {hp_val:,}</div>'
                    f'<div style="font-size:.72rem;color:#E67E22">Att {atk_val}</div></div>',
                    unsafe_allow_html=True)

        # Graphique
        records=[]
        for boss in boss_names:
            rec={'Boss':boss[:25]}
            for _,rw in df_tower.iterrows():
                rec[str(rw[stat_col])]=pd.to_numeric(rw[boss],errors='coerce')
            records.append(rec)
        df_tb=pd.DataFrame(records)
        hp_c  = next((c for c in df_tb.columns if 'HP' in c),None)
        atk_c = next((c for c in df_tb.columns if 'attack' in c.lower()),None)
        def_c = next((c for c in df_tb.columns if 'defense' in c.lower()),None)
        if hp_c:
            df_tb['Score'] = df_tb[hp_c].fillna(0)+df_tb.get(atk_c,pd.Series(0)).fillna(0)*2+df_tb.get(def_c,pd.Series(0)).fillna(0)
            st.plotly_chart(px.bar(df_tb,x='Boss',y='Score',color='Score',
                color_continuous_scale='Reds',title="Tower Boss - Score estime"),
                width='stretch')
        st.dataframe(df_tower,width='stretch')
    except Exception as e:
        st.warning(f"Erreur Tower Boss : {e}")
        st.dataframe(df_tower,width='stretch')

    st.divider()
    st.markdown("### Ordinary Boss")
    st.dataframe(df_boss.dropna(how='all').reset_index(drop=True).head(20),
                 width='stretch',hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# EXPLORATEUR
# ══════════════════════════════════════════════════════════════════════════
with t_exp:
    st.markdown("## Explorateur de Pals")
    st.divider()

    e1,e2,e3,e4 = st.columns([2,2,2,3])
    with e1:
        tailles_e = ["Toutes"]+sorted(df_c['Volume size'].dropna().unique().tolist())
        t_f = st.selectbox("Taille",tailles_e,label_visibility="collapsed",key="exp_taille")
    with e2:
        elems_e = ["Tous"]+sorted(df_c['Element 1'].dropna().unique().tolist())
        el_f = st.selectbox("Element",elems_e,label_visibility="collapsed",key="exp_elem")
    with e3:
        min_atk = st.number_input("Attaque min.",value=0,min_value=0,
                                   max_value=int(df_c['melee attack'].max()),
                                   label_visibility="collapsed",key="exp_atk")
    with e4:
        min_rar = st.slider("Rarete min.",0,int(df_c['rarity'].max()),0,key="exp_rar")

    df_ex = df_c.copy()
    if t_f  != "Toutes": df_ex = df_ex[df_ex['Volume size']==t_f]
    if el_f != "Tous":   df_ex = df_ex[df_ex['Element 1']==el_f]
    df_ex = df_ex[(df_ex['melee attack']>=min_atk)&(df_ex['rarity']>=min_rar)]

    st.markdown(f"**{len(df_ex)} Pals** correspondent")

    for chunk in [df_ex.iloc[i:i+6] for i in range(0,len(df_ex),6)]:
        cx = st.columns(6)
        for j,(_,row) in enumerate(chunk.iterrows()):
            with cx[j]:
                st.markdown(pal_card(row,size=75), unsafe_allow_html=True)

    if len(df_ex)>1:
        st.divider()
        ca,cb = st.columns(2)
        with ca:
            st.plotly_chart(px.scatter(df_ex,x='melee attack',y='HP',
                color='rarity',size='defense',hover_name='Name',
                color_continuous_scale='Viridis',
                title="HP vs Attaque (taille=defense, couleur=rarete)"),
                width='stretch')
        with cb:
            cols_t=['Name','HP','melee attack','defense','rarity','Volume size','Element FR','combat_score']
            cols_t=[c for c in cols_t if c in df_ex.columns]
            df_disp=df_ex[cols_t].rename(columns={
                'Name':'Pal','melee attack':'Attaque','defense':'Defense',
                'rarity':'Rarete','Volume size':'Taille',
                'Element FR':'Element','combat_score':'Score'})
            st.dataframe(df_disp.sort_values('Attaque',ascending=False),
                         width='stretch',hide_index=True)
