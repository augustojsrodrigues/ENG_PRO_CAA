from pathlib import Path
import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Engenharia de Produção • Matriz Interativa",
    page_icon="🎓",
    layout="wide",
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "disciplinas.csv"

@st.cache_data
def carregar_dados():
    df = pd.read_csv(DATA_FILE, dtype=str).fillna("")
    df["carga_horaria"] = pd.to_numeric(df["carga_horaria"], errors="coerce").fillna(0).astype(int)
    df["periodo_num"] = pd.to_numeric(df["periodo"], errors="coerce")
    return df

df = carregar_dados()
por_ref = {r["ref"]: r for _, r in df.iterrows()}

def refs_de(valor):
    if not valor:
        return []
    return [x.strip() for x in str(valor).split(";") if x.strip()]

def nome_ref(ref):
    if ref in por_ref:
        r = por_ref[ref]
        return f'{r["nome"]} ({r["codigo"]})'
    return ref

# Quem cada disciplina libera
libera = {ref: [] for ref in por_ref}
for _, linha in df.iterrows():
    for pre in refs_de(linha["pre_requisitos_refs"]):
        if pre in libera:
            libera[pre].append(linha["ref"])

def lista_nomes(refs):
    if not refs:
        return "Nenhuma indicada"
    return " • ".join(nome_ref(x) for x in refs)

def observacao_prereq(linha):
    partes = []
    refs = refs_de(linha["pre_requisitos_refs"])
    if refs:
        partes.append(lista_nomes(refs))
    if linha["pre_requisito_observacao"]:
        partes.append(linha["pre_requisito_observacao"])
    return " | ".join(partes) if partes else "Nenhum indicado"

def sort_key(linha):
    p = linha["periodo_num"]
    p = int(p) if pd.notna(p) else 99
    return (p, linha["area"], linha["ref"])

def card_html(linha, concluidas=None):
    concluidas = concluidas or set()
    ref = linha["ref"]
    tipo = linha["tipo"]
    classe = "obrigatoria" if tipo == "Obrigatória" else "eletiva"
    if ref in concluidas:
        classe += " concluida"

    periodo = f'{linha["periodo"]}º período' if linha["periodo"] else (
        linha["area"] if linha["area"] else "Sem período indicado"
    )
    pre = observacao_prereq(linha)
    abre_refs = libera.get(ref, [])
    abre = lista_nomes(abre_refs)

    badge = "Obrigatória" if tipo == "Obrigatória" else "Eletiva"
    check = " ✓" if ref in concluidas else ""

    return f"""
    <div class="course-card {classe}">
        <div class="card-top">
            <span class="ref">{html.escape(ref)}</span>
            <span class="ch">{linha["carga_horaria"]} h</span>
        </div>
        <div class="course-name">{html.escape(linha["nome"])}{check}</div>
        <div class="course-code">{html.escape(linha["codigo"])}</div>
        <div class="course-foot">{html.escape(periodo)} · {badge}</div>
        <div class="course-tooltip">
            <b>Pré-requisitos</b><br>{html.escape(pre)}
            <hr>
            <b>Libera</b><br>{html.escape(abre)}
        </div>
    </div>
    """

def render_cards(frame, concluidas=None):
    if frame.empty:
        st.info("Nenhuma disciplina encontrada para este filtro.")
        return
    ordenado = frame.copy()
    ordenado = ordenado.sort_values(
        by=["periodo_num", "area", "ref"],
        na_position="last"
    )
    cards = "".join(card_html(linha, concluidas) for _, linha in ordenado.iterrows())
    st.markdown(f'<div class="course-grid">{cards}</div>', unsafe_allow_html=True)

def ancestrais(ref, visitados=None):
    visitados = visitados or set()
    if ref in visitados or ref not in por_ref:
        return set()
    visitados.add(ref)
    resultado = set()
    for pre in refs_de(por_ref[ref]["pre_requisitos_refs"]):
        if pre in por_ref:
            resultado.add(pre)
            resultado |= ancestrais(pre, visitados)
    return resultado

st.markdown("""
<style>
    .block-container {padding-top: 1.6rem; padding-bottom: 3rem;}
    .hero {
        padding: 1.25rem 1.4rem;
        border: 1px solid rgba(49,51,63,.16);
        border-radius: 18px;
        margin-bottom: 1rem;
        background: linear-gradient(120deg, rgba(220,235,255,.55), rgba(255,248,214,.45));
    }
    .hero h1 {margin: 0; font-size: 2rem;}
    .hero p {margin: .35rem 0 0 0; opacity: .78;}
    .course-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
        gap: 13px;
        overflow: visible;
        margin-top: .75rem;
        margin-bottom: 1.25rem;
    }
    .course-card {
        position: relative;
        min-height: 152px;
        padding: 12px 13px 13px 13px;
        border-radius: 14px;
        border: 1px solid rgba(49,51,63,.18);
        box-shadow: 0 2px 7px rgba(0,0,0,.04);
        transition: transform .14s ease, box-shadow .14s ease;
        overflow: visible;
    }
    .course-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,.12);
        z-index: 50;
    }
    .course-card.obrigatoria {background: #dcecff;}
    .course-card.eletiva {background: #fff3c9;}
    .course-card.concluida {outline: 3px solid rgba(35,145,75,.35);}
    .card-top {display:flex; justify-content:space-between; font-size:.78rem; opacity:.76;}
    .ref {font-weight:700;}
    .course-name {font-weight:700; line-height:1.18; margin-top:14px; font-size:1rem;}
    .course-code {font-size:.78rem; opacity:.72; margin-top:6px;}
    .course-foot {font-size:.76rem; opacity:.72; margin-top:8px;}
    .course-tooltip {
        visibility: hidden;
        opacity: 0;
        position: absolute;
        z-index: 1000;
        left: 8px;
        right: 8px;
        top: calc(100% + 7px);
        background: #16181d;
        color: white;
        border-radius: 10px;
        padding: 11px 12px;
        font-size: .78rem;
        line-height: 1.35;
        pointer-events: none;
        transition: opacity .12s ease;
        box-shadow: 0 10px 28px rgba(0,0,0,.22);
    }
    .course-card:hover .course-tooltip {visibility:visible; opacity:1;}
    .course-tooltip hr {border:0; border-top:1px solid rgba(255,255,255,.2); margin:8px 0;}
    .legend {display:flex; gap:12px; flex-wrap:wrap; margin:.4rem 0 1rem 0;}
    .legend-item {display:flex; gap:7px; align-items:center; font-size:.86rem; opacity:.82;}
    .swatch {width:18px; height:18px; border-radius:5px; border:1px solid rgba(0,0,0,.15);}
    .blue {background:#dcecff;} .yellow {background:#fff3c9;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎓 Engenharia de Produção — Matriz Interativa</h1>
    <p>Obrigatórias, eletivas, áreas, pré-requisitos e disciplinas liberadas.</p>
</div>
<div class="legend">
    <div class="legend-item"><span class="swatch blue"></span> Obrigatória</div>
    <div class="legend-item"><span class="swatch yellow"></span> Eletiva</div>
</div>
""", unsafe_allow_html=True)

st.caption("Passe o mouse sobre uma disciplina para ver os pré-requisitos e quais disciplinas ela libera.")

tab_obr, tab_areas, tab_mapa, tab_prog = st.tabs(
    ["📘 Obrigatórias", "🧭 Áreas", "🗺️ Mapa completo", "✅ Meu progresso"]
)

with tab_obr:
    obrig = df[df["tipo"] == "Obrigatória"].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Disciplinas obrigatórias", len(obrig))
    c2.metric("Carga horária cadastrada", f'{obrig["carga_horaria"].sum()} h')
    c3.metric("Com área explícita", int((obrig["area"] != "").sum()))
    st.subheader("Todas as obrigatórias juntas")
    render_cards(obrig)

with tab_areas:
    areas = sorted([x for x in df["area"].unique().tolist() if x])
    area = st.selectbox("Selecione a área", areas)
    area_df = df[df["area"] == area].copy()
    obrig_area = area_df[area_df["tipo"] == "Obrigatória"]
    elet_area = area_df[area_df["tipo"] == "Eletiva"]

    c1, c2, c3 = st.columns(3)
    c1.metric("Obrigatórias da área", len(obrig_area))
    c2.metric("Eletivas da área", len(elet_area))
    c3.metric("Carga horária listada", f'{area_df["carga_horaria"].sum()} h')

    st.subheader("Obrigatórias da área")
    render_cards(obrig_area)

    st.subheader("Eletivas da área")
    render_cards(elet_area)

    # Base obrigatória necessária para chegar aos componentes da área
    deps = set()
    for ref in area_df["ref"]:
        deps |= ancestrais(ref)
    base_obrig = df[(df["ref"].isin(deps)) & (df["tipo"] == "Obrigatória") & (df["area"] != area)]
    if not base_obrig.empty:
        st.subheader("Base obrigatória que aparece nos pré-requisitos")
        st.caption("Estas disciplinas não são classificadas como componentes da área; elas aparecem na cadeia de pré-requisitos.")
        render_cards(base_obrig)

    st.info(
        "A imagem informa quais disciplinas pertencem a cada área, mas não traz a regra de quantas eletivas "
        "precisam ser cursadas para 'fechar' cada área. Por isso, o aplicativo não presume que todas as eletivas sejam obrigatórias."
    )

with tab_mapa:
    col1, col2, col3 = st.columns(3)
    tipos = col1.multiselect("Tipo", ["Obrigatória", "Eletiva"], default=["Obrigatória", "Eletiva"])
    areas_opts = sorted([x for x in df["area"].unique().tolist() if x])
    areas_sel = col2.multiselect("Área", areas_opts)
    periodos_opts = sorted([int(x) for x in df["periodo_num"].dropna().unique().tolist()])
    periodos_sel = col3.multiselect("Período", periodos_opts)

    filtrado = df[df["tipo"].isin(tipos)].copy()
    if areas_sel:
        filtrado = filtrado[filtrado["area"].isin(areas_sel)]
    if periodos_sel:
        filtrado = filtrado[filtrado["periodo_num"].isin(periodos_sel)]
    render_cards(filtrado)

    st.divider()
    escolhas = {f'{r["nome"]} — {r["codigo"]} [{r["ref"]}]': r["ref"] for _, r in df.iterrows()}
    escolha = st.selectbox("Detalhes de uma disciplina", list(escolhas.keys()))
    ref = escolhas[escolha]
    r = por_ref[ref]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Tipo:** {r['tipo']}")
        st.markdown(f"**Carga horária:** {r['carga_horaria']} h")
        st.markdown(f"**Período/área:** {r['periodo'] or r['area'] or 'Não indicado'}")
    with c2:
        st.markdown("**Pré-requisitos:**")
        st.write(observacao_prereq(r))
        st.markdown("**Disciplinas que libera:**")
        st.write(lista_nomes(libera.get(ref, [])))

with tab_prog:
    opcoes = df.sort_values(["periodo_num","area","ref"], na_position="last")
    label_por_ref = {
        r["ref"]: f'{r["nome"]} — {r["codigo"]} [{r["ref"]}]'
        for _, r in opcoes.iterrows()
    }
    concluidas = st.multiselect(
        "Marque as disciplinas já concluídas",
        options=list(label_por_ref.keys()),
        format_func=lambda x: label_por_ref[x]
    )
    concluidas = set(concluidas)

    obrig = df[df["tipo"] == "Obrigatória"]
    obrig_concl = obrig[obrig["ref"].isin(concluidas)]
    pct = 0 if len(obrig) == 0 else len(obrig_concl) / len(obrig)

    c1, c2, c3 = st.columns(3)
    c1.metric("Obrigatórias concluídas", f"{len(obrig_concl)}/{len(obrig)}")
    c2.metric("CH obrigatória concluída", f'{obrig_concl["carga_horaria"].sum()} h')
    c3.metric("Progresso por quantidade", f"{pct:.0%}")
    st.progress(min(max(pct, 0), 1))

    liberadas_agora = []
    bloqueadas_incerto = []
    for _, r in df.iterrows():
        ref = r["ref"]
        if ref in concluidas:
            continue
        prs = refs_de(r["pre_requisitos_refs"])
        tem_obs_incerta = bool(r["pre_requisito_observacao"]) and not prs
        if tem_obs_incerta:
            bloqueadas_incerto.append(ref)
            continue
        if all(p in concluidas for p in prs):
            liberadas_agora.append(ref)

    st.subheader("Disciplinas liberadas com o que foi marcado")
    render_cards(df[df["ref"].isin(liberadas_agora)], concluidas)

    if bloqueadas_incerto:
        with st.expander("Disciplinas com pré-requisito não resolvido na imagem"):
            for ref in bloqueadas_incerto:
                r = por_ref[ref]
                st.write(f"• {r['nome']} ({r['codigo']}): {r['pre_requisito_observacao']}")

st.divider()
st.caption(
    "Base inicial transcrita das duas imagens fornecidas. Pontos ambíguos foram mantidos como observação, "
    "sem inventar pré-requisitos."
)
