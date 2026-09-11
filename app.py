from pathlib import Path
from io import StringIO
import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Engenharia de Produção • Matriz Interativa",
    page_icon="🎓",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent

# O app tenta encontrar a base em mais de um lugar.
# Se ela não existir no GitHub, usa uma cópia interna para evitar FileNotFoundError.
POSSIVEIS_ARQUIVOS = [
    BASE_DIR / "disciplinas.csv",
    BASE_DIR / "data" / "disciplinas.csv",
]

CSV_EMBUTIDO = r"""ref,nome,codigo,carga_horaria,tipo,periodo,area,pre_requisitos_refs,pre_requisito_observacao,origem
1A,Cálculo Dif. e Int. 1,PROD0001,60,Obrigatória,1,,,,Matriz por período
1B,Geometria Analítica,PROD0002,60,Obrigatória,1,,,,Matriz por período
1C,Química Geral 1,PROD0005,60,Obrigatória,1,,,,Matriz por período
1D,Introdução ao Desenho,PROD0017,75,Obrigatória,1,,,,Matriz por período
1E,Elementos de Sociologia,PROD0018,30,Obrigatória,1,,,,Matriz por período
1F,Introdução à Eng. de Produção,PROD0024,30,Obrigatória,1,,,,Matriz por período
2A,Física Geral 1,PROD0003,60,Obrigatória,2,,,,Matriz por período
2B,Algoritmos e Programação,PROD0004,60,Obrigatória,2,,,,Matriz por período
2C,Probabilidade e Estatística,PROD0006,60,Obrigatória,2,,1A,,Matriz por período
2D,Cálculo Dif. e Int. 2,PROD0007,60,Obrigatória,2,,1A,,Matriz por período
2E,Álgebra Linear,PROD0009,60,Obrigatória,2,,1B,,Matriz por período
2F,Administração para Engenharia,PROD0020,60,Obrigatória,2,,1F,,Matriz por período
3A,Cálculo Dif. e Int. 3,PROD0008,60,Obrigatória,3,,1B;2D,,Matriz por período
3B,Física Geral 2,PROD0010,60,Obrigatória,3,,2A,,Matriz por período
3C,Mecânica 1,PROD0011,60,Obrigatória,3,,2A,,Matriz por período
3D,Cálculo Numérico,PROD0013,60,Obrigatória,3,,2B;2D,,Matriz por período
3E,Teoria do Trabalho,PROD0021,30,Obrigatória,3,,,,Matriz por período
3F,Ecologia Aplicada à Engenharia,PROD0022,30,Obrigatória,3,,1F,,Matriz por período
3G,Gestão da Produção 1,PROD0032,60,Obrigatória,3,,2F,,Matriz por período
4A,Cálculo Dif. e Int. 4,PROD0012,60,Obrigatória,4,,,,Matriz por período
4B,Eletrotécnica,PROD0014,60,Obrigatória,4,,3B,,Matriz por período
4C,Resistência dos Materiais 1,PROD0015,60,Obrigatória,4,,3C,,Matriz por período
4D,Fenômenos de Transporte,PROD0016,60,Obrigatória,4,,2A;3A,,Matriz por período
4E,Engenharia Econômica,PROD0023,60,Obrigatória,4,,1A,,Matriz por período
4F,Pesquisa Operacional 1,PROD0033,60,Obrigatória,4,,2C;2D;2E;1F,,Matriz por período
5A,Processos Industriais 1,PROD0025,30,Obrigatória,5,,1C;3B;3G,,Matriz por período
5B,Pesquisa Operacional 2,PROD0034,60,Obrigatória,5,,3D;4F,,Matriz por período
5C,Custos de Produção,PROD0035,60,Obrigatória,5,,,,Matriz por período
5D,Gestão da Qualidade,PROD0036,60,Obrigatória,5,,3G,,Matriz por período
5E,Gestão da Produção 2,PROD0037,60,Obrigatória,5,,3G,,Matriz por período
5F,Engenharia de Métodos,PROD0039,60,Obrigatória,5,,2C;3G,,Matriz por período
5G,Engenharia de Segurança do Trabalho,PROD0040,30,Obrigatória,5,,1C;3B,,Matriz por período
6A,Processos Industriais 2,PROD0026,30,Obrigatória,6,,4A;4F;5A,,Matriz por período
6B,Materiais de Const. Civil 1,PROD0027,60,Obrigatória,6,,4C,,Matriz por período
6C,Português Instr. e Metod. Científ.,PROD0030,30,Obrigatória,6,,,,Matriz por período
6D,Controle Estat. da Qualidade,PROD0038,60,Obrigatória,6,,2C;5D,,Matriz por período
7A,Processos Industriais 3,PROD0028,30,Obrigatória,7,,6A,,Matriz por período
8A,Processos Industriais 4,PROD0029,30,Obrigatória,8,,7A,,Matriz por período
10A,TCC,PROD0031,30,Obrigatória,10,,3E;3F;4B;4D;4E;5B;5C;5E;5G;6D;8A,,Matriz por período
10B,Estágio,PROD0041,270,Obrigatória,10,,1D;1E;3E;3F;4B;4C;4E;5B;5C;5E;5F;5G;6A;6D,,Matriz por período
LIBRAS,Libras,EDUC0058,60,Obrigatória,,,,A disciplina aparece em azul na imagem e foi cadastrada como obrigatória conforme a legenda fornecida.,Matriz por período
11A,Eng. de Confiabilidade,PROD0042,60,Eletiva,,11. Eng. da Qualidade,2C;5B,,Matriz por área
11B,Sist. de Gestão da Qualidade,PROD0043,60,Obrigatória,,11. Eng. da Qualidade,5D;6D,,Matriz por área
11C,Auditoria da Qualidade,PROD0045,60,Obrigatória,,11. Eng. da Qualidade,11B,,Matriz por área
11D,Ferramentas Av. para Qualidade,PROD0046,60,Obrigatória,,11. Eng. da Qualidade,11B,,Matriz por área
11E,Gestão de Sistemas Integrados,PROD0047,30,Obrigatória,,11. Eng. da Qualidade,11B,,Matriz por área
11F,Org. de Pessoal para Qualidade,PROD0048,30,Obrigatória,,11. Eng. da Qualidade,5D,,Matriz por área
11G,TE em Qualidade,PROD0049,30,Eletiva,,11. Eng. da Qualidade,5D,,Matriz por área
12A,Engenharia da Confiabilidade,PROD0050,60,Eletiva,,12. Pesquisa Operacional,2C;5B,,Matriz por área
12B,Análise de Decisão,PROD0051,60,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
12C,Probab. e Proc. Estocásticos 1,PROD0052,60,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
12D,Program. Matemática,PROD0053,60,Eletiva,,12. Pesquisa Operacional,2E;4A;4F,,Matriz por área
12E,Análise de Regressão,PROD0054,60,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
12F,Engenharia da Manutenção,PROD0055,60,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
12G,Técnicas de Simulação,PROD0056,60,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
12H,Model. e Estrut. de Problemas,PROD0057,30,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
12I,TE em Pesquisa Operacional,PROD0058,30,Eletiva,,12. Pesquisa Operacional,5B,,Matriz por área
13A,Estratégia,PROD0044,60,Eletiva,,13. Gestão da Produção,2F,,Matriz por área
13B,Logística 1,PROD0059,60,Eletiva,,13. Gestão da Produção,5B;5E,,Matriz por área
13C,Logística 2,PROD0060,60,Eletiva,,13. Gestão da Produção,13B,,Matriz por área
13D,Organiz. do Trabalho,PROD0061,60,Eletiva,,13. Gestão da Produção,3E;5E,,Matriz por área
13E,Estratégia da Produção,PROD0062,30,Eletiva,,13. Gestão da Produção,5E,,Matriz por área
13F,TE em Gestão da Produção,PROD0063,30,Eletiva,,13. Gestão da Produção,5E,,Matriz por área
13G,Gestão da Produção 3,PROD0064,60,Eletiva,,13. Gestão da Produção,5E,,Matriz por área
13H,Gestão da Produção Aplicada,PROD0065,60,Eletiva,,13. Gestão da Produção,5E,,Matriz por área
13I,Empreendedorismo,PROD0066,60,Eletiva,,13. Gestão da Produção,,,Matriz por área
14A,TE em Gest. Econ. e Financeira,PROD0067,30,Eletiva,,14. Gestão Econ. e Fin.,4E,,Matriz por área
14B,Planejamento de Competitividade,PROD0068,30,Obrigatória,,14. Gestão Econ. e Fin.,3G;4E;13A,,Matriz por área
14C,Engenharia de Avaliações,PROD0069,45,Eletiva,,14. Gestão Econ. e Fin.,3G;4E,,Matriz por área
14D,Economia Industrial 1,PROD0070,60,Eletiva,,14. Gestão Econ. e Fin.,4E,,Matriz por área
14E,Análise Econ. e Financeira 1,PROD0071,60,Eletiva,,14. Gestão Econ. e Fin.,4E;13A,,Matriz por área
14F,Análise de Projetos,PROD0072,60,Eletiva,,14. Gestão Econ. e Fin.,4E,,Matriz por área
14G,Economia 1,PROD0073,60,Eletiva,,14. Gestão Econ. e Fin.,4E,,Matriz por área
14H,Microeconomia 1,PROD0074,60,Eletiva,,14. Gestão Econ. e Fin.,4E,,Matriz por área
15A,Sist. de Apoio à Decisão,PROD0075,30,Eletiva,,15. Gestão da Inform.,15F,,Matriz por área
15B,Planej. de Sist. de Informação,PROD0076,30,Eletiva,,15. Gestão da Inform.,15A;15D;15F,,Matriz por área
15C,TE em Sistemas de Informação,PROD0077,30,Eletiva,,15. Gestão da Inform.,15F,,Matriz por área
15D,Sistemas de Int. Gerencial e Executivo,PROD0078,30,Eletiva,,15. Gestão da Inform.,15F,,Matriz por área
15E,Manufatura Integrada por Computador,PROD0037,60,Eletiva,,15. Gestão da Inform.,3G;4F,"O código aparece como PROD0037 na imagem, duplicando Gestão da Produção 2. Convém conferir no PPC/SIGAA.",Matriz por área
15F,Gestão da Informação,PROD0080,30,Eletiva,,15. Gestão da Inform.,3G,,Matriz por área
15G,Gestão da Tecnologia da Informação,PROD0081,60,Eletiva,,15. Gestão da Inform.,3G,,Matriz por área
15H,Gestão do Conhec.,PROD0082,60,Eletiva,,15. Gestão da Inform.,15F,,Matriz por área
16A,Sistemas de Gestão Ambiental,PROD0083,60,Obrigatória,,16. Gestão Ambiental,5D,,Matriz por área
16B,Auditoria de Sist. de Gestão Ambiental,PROD0084,60,Obrigatória,,16. Gestão Ambiental,16A,,Matriz por área
16C,Economia do Meio Ambiente 1,PROD0085,60,Obrigatória,,16. Gestão Ambiental,3G;4E,,Matriz por área
16D,Av. Ambiental de Processos e Produtos,PROD0086,60,Obrigatória,,16. Gestão Ambiental,16A,,Matriz por área
16E,TE em Engenharia de Produção 8,PROD0087,30,Eletiva,,16. Gestão Ambiental,5D,,Matriz por área
16F,TE em Gestão Ambiental,PROD0088,30,Eletiva,,16. Gestão Ambiental,5D,,Matriz por área
17A,Projeto de Sist. de Produção,PROD0089,60,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
17B,Engenharia de Produto,PROD0090,60,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
17C,Planejamento do Arranjo Físico,PROD0091,60,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
17D,TE em Engenharia do Produto,PROD0092,30,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
17E,Lab. de Eng. de Produção,PROD0093,60,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
17F,TE em Projeto do Produto e da Fábrica,PROD0094,30,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
17G,Projeto do Produto,PROD0095,60,Eletiva,,17. Eng. do Produto,5E,,Matriz por área
18A,Probab. e Processos Estocásticos 2,PROD0096,60,Eletiva,,18. Av. Eng. de Prod. 1,12C,,Matriz por área
18B,Gestão da Inovação,PROD0097,30,Obrigatória,,18. Av. Eng. de Prod. 1,,O pré-requisito aparece como 'iB' na imagem e não foi convertido para evitar adivinhação.,Matriz por área
18C,Análise de Séries Temporais,PROD0098,60,Eletiva,,18. Av. Eng. de Prod. 1,2C;5B;12C,,Matriz por área
18D,Teoria das Filas,PROD0099,60,Eletiva,,18. Av. Eng. de Prod. 1,5B,,Matriz por área
18E,Fundamentos de Inteligência Artificial,PROD0100,60,Eletiva,,18. Av. Eng. de Prod. 1,4A,,Matriz por área
18F,Metrologia,PROD0101,60,Eletiva,,18. Av. Eng. de Prod. 1,11B,,Matriz por área
19A,TE em Eng. de Prod. 9,PROD0102,60,Eletiva,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
19B,TE em Eng. de Prod. 1,PROD0103,30,Eletiva,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
19C,TE em Eng. de Prod. 2,PROD0104,30,Obrigatória,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
19D,TE em Eng. de Prod. 3,PROD0105,60,Eletiva,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
19E,TE em Eng. de Prod. 4,PROD0106,60,Obrigatória,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
19F,TE em Eng. de Prod. 5,PROD0107,60,Eletiva,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
19G,TE em Eng. de Prod. 7,PROD0109,60,Eletiva,,19. Av. Eng. de Prod. 2,5B;5E,,Matriz por área
20A,Gestão de Projetos,PROD0110,60,Eletiva,,20. Gestão de Projetos,3G;4F,,Matriz por área
20B,Processos Organiz. para Projetos,PROD0111,30,Eletiva,,20. Gestão de Projetos,20A,,Matriz por área
20C,Gestão e Seleção de Portfólio,PROD0112,60,Eletiva,,20. Gestão de Projetos,20A,,Matriz por área
20D,Gestão de Riscos em Projetos,PROD0113,60,Eletiva,,20. Gestão de Projetos,5B;20A,,Matriz por área
20E,Gestão de Contratação em Projetos,PROD0114,60,Eletiva,,20. Gestão de Projetos,20A,,Matriz por área
20F,Ferram. para Gestão de Projetos,PROD0115,30,Eletiva,,20. Gestão de Projetos,20A,,Matriz por área
20G,TE em Gestão de Projetos,PROD0116,30,Eletiva,,20. Gestão de Projetos,20A,,Matriz por área
"""

@st.cache_data
def carregar_dados():
    arquivo_encontrado = next((p for p in POSSIVEIS_ARQUIVOS if p.exists()), None)

    if arquivo_encontrado is not None:
        df = pd.read_csv(arquivo_encontrado, dtype=str).fillna("")
    else:
        df = pd.read_csv(StringIO(CSV_EMBUTIDO), dtype=str).fillna("")

    df["carga_horaria"] = pd.to_numeric(
        df["carga_horaria"], errors="coerce"
    ).fillna(0).astype(int)

    df["periodo_num"] = pd.to_numeric(
        df["periodo"], errors="coerce"
    )
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

# Calcula automaticamente quais disciplinas cada componente libera.
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

    return " | ".join(partes) if partes else "Nenhum"

def card_html(linha, concluidas=None):
    concluidas = concluidas or set()
    ref = linha["ref"]
    tipo = linha["tipo"]

    classe = "obrigatoria" if tipo == "Obrigatória" else "eletiva"
    if ref in concluidas:
        classe += " concluida"

    periodo = (
        f'{linha["periodo"]}º período'
        if linha["periodo"]
        else (linha["area"] if linha["area"] else "Sem período indicado")
    )

    pre = observacao_prereq(linha)
    abre = lista_nomes(libera.get(ref, []))
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
            <b>Pré-requisitos</b><br>
            {html.escape(pre)}
            <hr>
            <b>Libera</b><br>
            {html.escape(abre)}
        </div>
    </div>
    """

def render_cards(frame, concluidas=None):
    if frame.empty:
        st.info("Nenhuma disciplina encontrada para este filtro.")
        return

    ordenado = frame.copy().sort_values(
        by=["periodo_num", "area", "ref"],
        na_position="last"
    )

    cards = "".join(
        card_html(linha, concluidas)
        for _, linha in ordenado.iterrows()
    )

    st.markdown(
        f'<div class="course-grid">{cards}</div>',
        unsafe_allow_html=True
    )

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
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 1.25rem 1.4rem;
    border: 1px solid rgba(49,51,63,.16);
    border-radius: 18px;
    margin-bottom: 1rem;
    background: linear-gradient(
        120deg,
        rgba(220,235,255,.55),
        rgba(255,248,214,.45)
    );
}

.hero h1 {
    margin: 0;
    font-size: 2rem;
}

.hero p {
    margin: .35rem 0 0 0;
    opacity: .78;
}

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

.course-card.obrigatoria {
    background: #dcecff;
}

.course-card.eletiva {
    background: #fff3c9;
}

.course-card.concluida {
    outline: 3px solid rgba(35,145,75,.35);
}

.card-top {
    display: flex;
    justify-content: space-between;
    font-size: .78rem;
    opacity: .76;
}

.ref {
    font-weight: 700;
}

.course-name {
    font-weight: 700;
    line-height: 1.18;
    margin-top: 14px;
    font-size: 1rem;
}

.course-code {
    font-size: .78rem;
    opacity: .72;
    margin-top: 6px;
}

.course-foot {
    font-size: .76rem;
    opacity: .72;
    margin-top: 8px;
}

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

.course-card:hover .course-tooltip {
    visibility: visible;
    opacity: 1;
}

.course-tooltip hr {
    border: 0;
    border-top: 1px solid rgba(255,255,255,.2);
    margin: 8px 0;
}

.legend {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin: .4rem 0 1rem 0;
}

.legend-item {
    display: flex;
    gap: 7px;
    align-items: center;
    font-size: .86rem;
    opacity: .82;
}

.swatch {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid rgba(0,0,0,.15);
}

.blue { background: #dcecff; }
.yellow { background: #fff3c9; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🎓 Engenharia de Produção — Matriz Interativa</h1>
    <p>Obrigatórias, eletivas, áreas, pré-requisitos e disciplinas liberadas.</p>
</div>

<div class="legend">
    <div class="legend-item">
        <span class="swatch blue"></span> Obrigatória
    </div>
    <div class="legend-item">
        <span class="swatch yellow"></span> Eletiva
    </div>
</div>
""", unsafe_allow_html=True)

st.caption(
    "Passe o mouse sobre uma disciplina para ver os pré-requisitos "
    "e quais disciplinas ela libera."
)

tab_obr, tab_areas, tab_mapa, tab_prog = st.tabs(
    [
        "📘 Obrigatórias",
        "🧭 Áreas",
        "🗺️ Mapa completo",
        "✅ Meu progresso",
    ]
)

with tab_obr:
    obrig = df[df["tipo"] == "Obrigatória"].copy()

    c1, c2, c3 = st.columns(3)
    c1.metric("Disciplinas obrigatórias", len(obrig))
    c2.metric(
        "Carga horária cadastrada",
        f'{obrig["carga_horaria"].sum()} h'
    )
    c3.metric(
        "Com área explícita",
        int((obrig["area"] != "").sum())
    )

    st.subheader("Todas as obrigatórias juntas")
    render_cards(obrig)

with tab_areas:
    areas = sorted(
        [x for x in df["area"].unique().tolist() if x]
    )

    area = st.selectbox(
        "Selecione a área",
        areas
    )

    area_df = df[df["area"] == area].copy()
    obrig_area = area_df[
        area_df["tipo"] == "Obrigatória"
    ]
    elet_area = area_df[
        area_df["tipo"] == "Eletiva"
    ]

    c1, c2, c3 = st.columns(3)
    c1.metric("Obrigatórias da área", len(obrig_area))
    c2.metric("Eletivas da área", len(elet_area))
    c3.metric(
        "Carga horária listada",
        f'{area_df["carga_horaria"].sum()} h'
    )

    st.subheader("Obrigatórias da área")
    render_cards(obrig_area)

    st.subheader("Eletivas da área")
    render_cards(elet_area)

    deps = set()

    for ref in area_df["ref"]:
        deps |= ancestrais(ref)

    base_obrig = df[
        (df["ref"].isin(deps))
        & (df["tipo"] == "Obrigatória")
        & (df["area"] != area)
    ]

    if not base_obrig.empty:
        st.subheader(
            "Base obrigatória que aparece nos pré-requisitos"
        )
        st.caption(
            "Estas disciplinas não são classificadas como componentes "
            "da área; elas aparecem na cadeia de pré-requisitos."
        )
        render_cards(base_obrig)

    st.info(
        "A matriz mostra as disciplinas pertencentes às áreas, mas ainda "
        "não informa a regra de quantas eletivas precisam ser cursadas "
        "para completar cada área."
    )

with tab_mapa:
    col1, col2, col3 = st.columns(3)

    tipos = col1.multiselect(
        "Tipo",
        ["Obrigatória", "Eletiva"],
        default=["Obrigatória", "Eletiva"]
    )

    areas_opts = sorted(
        [x for x in df["area"].unique().tolist() if x]
    )

    areas_sel = col2.multiselect(
        "Área",
        areas_opts
    )

    periodos_opts = sorted(
        [
            int(x)
            for x in df["periodo_num"]
            .dropna()
            .unique()
            .tolist()
        ]
    )

    periodos_sel = col3.multiselect(
        "Período",
        periodos_opts
    )

    filtrado = df[
        df["tipo"].isin(tipos)
    ].copy()

    if areas_sel:
        filtrado = filtrado[
            filtrado["area"].isin(areas_sel)
        ]

    if periodos_sel:
        filtrado = filtrado[
            filtrado["periodo_num"].isin(periodos_sel)
        ]

    render_cards(filtrado)

    st.divider()

    escolhas = {
        f'{r["nome"]} — {r["codigo"]} [{r["ref"]}]': r["ref"]
        for _, r in df.iterrows()
    }

    escolha = st.selectbox(
        "Detalhes de uma disciplina",
        list(escolhas.keys())
    )

    ref = escolhas[escolha]
    r = por_ref[ref]

    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"**Tipo:** {r['tipo']}")
        st.markdown(
            f"**Carga horária:** {r['carga_horaria']} h"
        )
        st.markdown(
            f"**Período/área:** "
            f"{r['periodo'] or r['area'] or 'Não indicado'}"
        )

    with c2:
        st.markdown("**Pré-requisitos:**")
        st.write(observacao_prereq(r))

        st.markdown("**Disciplinas que libera:**")
        st.write(
            lista_nomes(libera.get(ref, []))
        )

with tab_prog:
    opcoes = df.sort_values(
        ["periodo_num", "area", "ref"],
        na_position="last"
    )

    label_por_ref = {
        r["ref"]:
        f'{r["nome"]} — {r["codigo"]} [{r["ref"]}]'
        for _, r in opcoes.iterrows()
    }

    concluidas = st.multiselect(
        "Marque as disciplinas já concluídas",
        options=list(label_por_ref.keys()),
        format_func=lambda x: label_por_ref[x]
    )

    concluidas = set(concluidas)

    obrig = df[
        df["tipo"] == "Obrigatória"
    ]

    obrig_concl = obrig[
        obrig["ref"].isin(concluidas)
    ]

    pct = (
        0
        if len(obrig) == 0
        else len(obrig_concl) / len(obrig)
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Obrigatórias concluídas",
        f"{len(obrig_concl)}/{len(obrig)}"
    )

    c2.metric(
        "CH obrigatória concluída",
        f'{obrig_concl["carga_horaria"].sum()} h'
    )

    c3.metric(
        "Progresso por quantidade",
        f"{pct:.0%}"
    )

    st.progress(
        min(max(pct, 0), 1)
    )

    liberadas_agora = []
    bloqueadas_incerto = []

    for _, r in df.iterrows():
        ref = r["ref"]

        if ref in concluidas:
            continue

        prs = refs_de(
            r["pre_requisitos_refs"]
        )

        tem_obs_incerta = (
            bool(r["pre_requisito_observacao"])
            and not prs
        )

        if tem_obs_incerta:
            bloqueadas_incerto.append(ref)
            continue

        if all(
            p in concluidas
            for p in prs
        ):
            liberadas_agora.append(ref)

    st.subheader(
        "Disciplinas liberadas com o que foi marcado"
    )

    render_cards(
        df[df["ref"].isin(liberadas_agora)],
        concluidas
    )

    if bloqueadas_incerto:
        with st.expander(
            "Disciplinas com pré-requisito ainda não confirmado"
        ):
            for ref in bloqueadas_incerto:
                r = por_ref[ref]
                st.write(
                    f"• {r['nome']} ({r['codigo']}): "
                    f"{r['pre_requisito_observacao']}"
                )

st.divider()

st.caption(
    "Base transcrita das matrizes fornecidas. "
    "Quando a matriz mostra '??', o componente foi tratado como sem pré-requisito."
)
