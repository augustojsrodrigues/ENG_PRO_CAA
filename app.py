from pathlib import Path
from io import StringIO
import html
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Engenharia de Produção | Matriz Interativa",
    page_icon="🎓",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent

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
    arquivo_encontrado = next(
        (p for p in POSSIVEIS_ARQUIVOS if p.exists()),
        None
    )

    if arquivo_encontrado is not None:
        dados = pd.read_csv(
            arquivo_encontrado,
            dtype=str
        ).fillna("")
    else:
        dados = pd.read_csv(
            StringIO(CSV_EMBUTIDO),
            dtype=str
        ).fillna("")

    dados["carga_horaria"] = pd.to_numeric(
        dados["carga_horaria"],
        errors="coerce"
    ).fillna(0).astype(int)

    dados["periodo_num"] = pd.to_numeric(
        dados["periodo"],
        errors="coerce"
    )

    return dados


df = carregar_dados()

por_ref = {
    linha["ref"]: linha
    for _, linha in df.iterrows()
}


def refs_de(valor):
    if not valor:
        return []

    return [
        item.strip()
        for item in str(valor).split(";")
        if item.strip()
    ]


def nome_ref(ref):
    if ref in por_ref:
        linha = por_ref[ref]
        return f'{linha["nome"]} ({linha["codigo"]})'

    return ref


def nome_area(area):
    texto = str(area).strip()

    partes = texto.split(".", 1)

    if (
        len(partes) == 2
        and partes[0].strip().isdigit()
    ):
        return partes[1].strip()

    return texto


def classe_ref(ref):
    seguro = "".join(
        caractere
        if caractere.isalnum()
        else "_"
        for caractere in str(ref)
    )
    return f"ref_{seguro}"


libera = {
    ref: []
    for ref in por_ref
}

for _, linha in df.iterrows():
    for pre in refs_de(
        linha["pre_requisitos_refs"]
    ):
        if pre in libera:
            libera[pre].append(
                linha["ref"]
            )


def gerar_css_relacoes():
    regras = []

    escopos = [
        ".course-grid",
        ".period-matrix",
        ".area-matrix",
    ]

    for ref, linha in por_ref.items():
        classe_origem = classe_ref(ref)

        pre_requisitos = refs_de(
            linha["pre_requisitos_refs"]
        )

        liberadas = libera.get(
            ref,
            []
        )

        for pre in pre_requisitos:
            if pre not in por_ref:
                continue

            classe_pre = classe_ref(pre)

            for escopo in escopos:
                regras.append(
                    f"""
                    {escopo}:has(.{classe_origem}:hover)
                    .{classe_pre} {{
                        background: #d9f4df !important;
                        border: 2px solid #2f8f4e !important;
                        box-shadow:
                            0 0 0 3px
                            rgba(47, 143, 78, .14) !important;
                        transform: translateY(-2px);
                    }}
                    """
                )

        for liberada in liberadas:
            if liberada not in por_ref:
                continue

            classe_liberada = classe_ref(
                liberada
            )

            for escopo in escopos:
                regras.append(
                    f"""
                    {escopo}:has(.{classe_origem}:hover)
                    .{classe_liberada} {{
                        background: #eee3ff !important;
                        border: 2px solid #7a4bc2 !important;
                        box-shadow:
                            0 0 0 3px
                            rgba(122, 75, 194, .13) !important;
                        transform: translateY(-2px);
                    }}
                    """
                )

    return "\n".join(regras)


CSS_RELACOES = gerar_css_relacoes()


def lista_nomes(refs):
    if not refs:
        return "Nenhuma indicada"

    return " • ".join(
        nome_ref(ref)
        for ref in refs
    )


def observacao_prereq(linha):
    partes = []

    refs = refs_de(
        linha["pre_requisitos_refs"]
    )

    if refs:
        partes.append(
            lista_nomes(refs)
        )

    if linha["pre_requisito_observacao"]:
        partes.append(
            linha["pre_requisito_observacao"]
        )

    if not partes:
        return "Nenhum"

    return " | ".join(partes)


def card_html(linha, concluidas=None):
    concluidas = concluidas or set()

    ref = linha["ref"]
    tipo = linha["tipo"]

    classe = (
        "obrigatoria"
        if tipo == "Obrigatória"
        else "eletiva"
    )

    if ref in concluidas:
        classe += " concluida"

    if linha["periodo"]:
        local = f'{linha["periodo"]}º período'
    elif linha["area"]:
        local = nome_area(
            linha["area"]
        )
    else:
        local = "Sem período"

    pre = observacao_prereq(linha)

    abre = lista_nomes(
        libera.get(ref, [])
    )

    check = (
        " ✓"
        if ref in concluidas
        else ""
    )

    ref_css = classe_ref(ref)

    return f"""
    <div class="course-card {classe} {ref_css}">
        <div class="card-top">
            <span class="ref">{html.escape(ref)}</span>
            <span class="ch">{linha["carga_horaria"]} h</span>
        </div>

        <div class="course-name">
            {html.escape(linha["nome"])}{check}
        </div>

        <div class="course-code">
            {html.escape(linha["codigo"])}
        </div>

        <div class="course-foot">
            {html.escape(local)} · {html.escape(tipo)}
        </div>

        <div class="course-tooltip">
            <b>Pré-requisitos</b><br>
            {html.escape(pre)}
            <hr>
            <b>Libera</b><br>
            {html.escape(abre)}
        </div>
    </div>
    """


def render_cards(
    frame,
    concluidas=None,
    ordenar_por_ref=False
):
    if frame.empty:
        st.info(
            "Nenhuma disciplina encontrada."
        )
        return

    ordenado = frame.copy()

    if ordenar_por_ref:
        ordenado = ordenado.sort_values(
            by=["ref"]
        )
    else:
        ordenado = ordenado.sort_values(
            by=[
                "periodo_num",
                "area",
                "ref"
            ],
            na_position="last"
        )

    cards = "".join(
        card_html(
            linha,
            concluidas
        )
        for _, linha in ordenado.iterrows()
    )

    st.html(
        f"""
        <div class="course-grid">
            {cards}
        </div>
        """
    )


def matrix_card_html(
    linha,
    concluidas=None
):
    concluidas = concluidas or set()

    tipo = linha["tipo"]

    classe = (
        "obrigatoria"
        if tipo == "Obrigatória"
        else "eletiva"
    )

    if linha["ref"] in concluidas:
        classe += " concluida"

    pre = observacao_prereq(linha)

    abre = lista_nomes(
        libera.get(
            linha["ref"],
            []
        )
    )

    tooltip = (
        f"Pré-requisitos: {pre}\n"
        f"Libera: {abre}"
    )

    ref_css = classe_ref(
        linha["ref"]
    )

    return f"""
    <div
        class="matrix-course {classe} {ref_css}"
        title="{html.escape(tooltip, quote=True)}"
    >
        <div class="matrix-course-top">
            <span>{html.escape(linha["ref"])}</span>
            <span>{linha["carga_horaria"]} h</span>
        </div>

        <div class="matrix-course-name">
            {html.escape(linha["nome"])}
        </div>

        <div class="matrix-course-code">
            {html.escape(linha["codigo"])}
        </div>
    </div>
    """


def render_matriz_periodos(concluidas=None):
    frame = df[
        df["origem"] == "Matriz por período"
    ].copy()

    colunas = []

    for periodo in range(1, 11):
        grupo = frame[
            frame["periodo_num"] == periodo
        ].copy().sort_values(
            "ref"
        )

        cards = "".join(
            matrix_card_html(
                linha,
                concluidas
            )
            for _, linha in grupo.iterrows()
        )

        if not cards:
            cards = """
            <div class="matrix-empty">
                Sem disciplina alocada
            </div>
            """

        ch = int(
            grupo["carga_horaria"].sum()
        )

        colunas.append(
            f"""
            <section class="matrix-column">
                <div class="matrix-column-header">
                    <strong>{periodo}º Período</strong>
                    <span>{ch} h</span>
                </div>

                <div class="matrix-column-body">
                    {cards}
                </div>
            </section>
            """
        )

    sem_periodo = frame[
        frame["periodo"] == ""
    ].copy().sort_values(
        "ref"
    )

    if not sem_periodo.empty:
        cards = "".join(
            matrix_card_html(
                linha,
                concluidas
            )
            for _, linha
            in sem_periodo.iterrows()
        )

        ch = int(
            sem_periodo[
                "carga_horaria"
            ].sum()
        )

        colunas.append(
            f"""
            <section class="matrix-column">
                <div class="matrix-column-header">
                    <strong>Sem período</strong>
                    <span>{ch} h</span>
                </div>

                <div class="matrix-column-body">
                    {cards}
                </div>
            </section>
            """
        )

    st.html(
        f"""
        <div class="matrix-scroll">
            <div class="period-matrix">
                {''.join(colunas)}
            </div>
        </div>
        """
    )


def render_matriz_areas(concluidas=None):
    frame = df[
        df["origem"] == "Matriz por área"
    ].copy()

    areas = sorted(
        [
            area
            for area
            in frame["area"].unique().tolist()
            if area
        ],
        key=lambda texto: int(
            texto.split(".")[0]
        )
    )

    colunas = []

    for area in areas:
        grupo = frame[
            frame["area"] == area
        ].copy().sort_values(
            "ref"
        )

        cards = "".join(
            matrix_card_html(
                linha,
                concluidas
            )
            for _, linha
            in grupo.iterrows()
        )

        ch = int(
            grupo[
                "carga_horaria"
            ].sum()
        )

        colunas.append(
            f"""
            <section class="matrix-column area-column">
                <div class="matrix-column-header">
                    <strong>{html.escape(nome_area(area))}</strong>
                    <span>{ch} h</span>
                </div>

                <div class="matrix-column-body">
                    {cards}
                </div>
            </section>
            """
        )

    st.html(
        f"""
        <div class="matrix-scroll">
            <div class="area-matrix">
                {''.join(colunas)}
            </div>
        </div>
        """
    )


st.html("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 2rem 2.2rem;
    border: 1px solid rgba(18, 72, 120, .18);
    border-radius: 24px;
    margin-bottom: 1.1rem;
    background:
        radial-gradient(
            circle at top right,
            rgba(255, 221, 102, .34),
            transparent 34%
        ),
        linear-gradient(
            135deg,
            rgba(224, 239, 255, .95),
            rgba(247, 250, 252, .98) 52%,
            rgba(255, 248, 218, .92)
        );
    box-shadow:
        0 10px 30px
        rgba(30, 64, 95, .08);
}

.hero::after {
    content: "";
    position: absolute;
    width: 250px;
    height: 250px;
    border-radius: 50%;
    right: -90px;
    bottom: -140px;
    background: rgba(47, 111, 176, .08);
}

.hero-kicker {
    display: inline-block;
    margin-bottom: .65rem;
    padding: .34rem .68rem;
    border-radius: 999px;
    background: rgba(47, 111, 176, .10);
    color: #235b8f;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .04em;
    text-transform: uppercase;
}

.hero-university {
    margin: 0;
    font-size: 1.02rem;
    font-weight: 700;
    color: #2b4f73;
}

.hero-campus {
    margin: .15rem 0 0 0;
    font-size: .93rem;
    color: #52677b;
}

.hero h1 {
    margin: .9rem 0 .35rem 0;
    font-size: clamp(2rem, 4vw, 3.25rem);
    line-height: 1.04;
    color: #1f3347;
    letter-spacing: -.025em;
}

.hero-subtitle {
    max-width: 900px;
    margin: 0;
    font-size: 1rem;
    line-height: 1.55;
    color: #5c6875;
}

.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: .55rem;
    margin-top: 1.2rem;
}

.hero-badge {
    padding: .42rem .72rem;
    border: 1px solid rgba(47, 111, 176, .14);
    border-radius: 999px;
    background: rgba(255, 255, 255, .72);
    color: #31495f;
    font-size: .78rem;
    font-weight: 600;
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
    border: 1px solid rgba(0, 0, 0, .15);
}

.blue {
    background: #dcecff;
}

.yellow {
    background: #fff3c9;
}

.course-grid {
    display: grid;
    grid-template-columns:
        repeat(
            auto-fill,
            minmax(210px, 1fr)
        );
    gap: 13px;
    overflow: visible;
    margin-top: .75rem;
    margin-bottom: 1.25rem;
}

.course-card {
    position: relative;
    min-height: 150px;
    padding: 12px 13px 13px 13px;
    border-radius: 14px;
    border: 1px solid rgba(49, 51, 63, .18);
    box-shadow: 0 2px 7px rgba(0, 0, 0, .04);
    transition:
        transform .14s ease,
        box-shadow .14s ease;
    overflow: visible;
}

.course-card:hover {
    transform: translateY(-2px);
    box-shadow:
        0 8px 20px
        rgba(0, 0, 0, .12);
    z-index: 50;
}

.course-card.obrigatoria,
.matrix-course.obrigatoria {
    background: #dcecff;
}

.course-card.eletiva,
.matrix-course.eletiva {
    background: #fff3c9;
}

.course-card.concluida,
.matrix-course.concluida {
    background: #ffd9d9 !important;
    border: 2px solid #c93636 !important;
    box-shadow:
        0 0 0 3px
        rgba(201, 54, 54, .12) !important;
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
    box-shadow:
        0 10px 28px
        rgba(0, 0, 0, .22);
}

.course-card:hover
.course-tooltip {
    visibility: visible;
    opacity: 1;
}

.course-tooltip hr {
    border: 0;
    border-top:
        1px solid
        rgba(255, 255, 255, .2);
    margin: 8px 0;
}

.matrix-scroll {
    width: 100%;
    overflow-x: auto;
    padding:
        3px 2px
        18px 2px;
    margin-bottom: 1.3rem;
}

.period-matrix {
    display: grid;
    grid-template-columns:
        repeat(
            11,
            minmax(190px, 1fr)
        );
    gap: 11px;
    min-width: 2200px;
    align-items: start;
}

.area-matrix {
    display: grid;
    grid-template-columns:
        repeat(
            10,
            minmax(205px, 1fr)
        );
    gap: 11px;
    min-width: 2200px;
    align-items: start;
}

.matrix-column {
    min-width: 0;
}

.matrix-column-header {
    min-height: 54px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 2px;
    padding: 8px 10px;
    margin-bottom: 9px;
    border-radius: 9px;
    border:
        1px solid
        rgba(49, 51, 63, .22);
    background: #f2f3f5;
    text-align: center;
    font-size: .83rem;
}

.matrix-column-header span {
    font-size: .72rem;
    opacity: .65;
}

.matrix-column-body {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.matrix-course {
    min-height: 108px;
    padding: 8px 9px;
    border:
        1px solid
        rgba(49, 51, 63, .18);
    border-radius: 5px;
    box-sizing: border-box;
    cursor: help;
}

.matrix-course-top {
    display: flex;
    justify-content: space-between;
    gap: 7px;
    font-size: .68rem;
    opacity: .72;
}

.matrix-course-name {
    margin-top: 12px;
    font-size: .79rem;
    line-height: 1.18;
    font-weight: 700;
    text-align: center;
}

.matrix-course-code {
    margin-top: 4px;
    font-size: .67rem;
    opacity: .7;
    text-align: center;
}

.matrix-empty {
    padding: 13px 8px;
    border:
        1px dashed
        rgba(49, 51, 63, .2);
    border-radius: 6px;
    text-align: center;
    font-size: .75rem;
    opacity: .55;
}

</style>
""")

st.html(
    f"""
    <style>
        {CSS_RELACOES}

        .course-card,
        .matrix-course {{
            transition:
                background .16s ease,
                border-color .16s ease,
                box-shadow .16s ease,
                transform .16s ease;
        }}

        .course-card:hover,
        .matrix-course:hover {{
            outline:
                3px solid
                rgba(32, 66, 96, .16);
        }}
    </style>
    """
)


st.html("""
<div class="hero">
    <div class="hero-kicker">
        Matriz Curricular Interativa
    </div>

    <p class="hero-university">
        Universidade Federal de Pernambuco (UFPE)
    </p>

    <p class="hero-campus">
        Centro Acadêmico do Agreste (CAA)
    </p>

    <h1>
        Engenharia de Produção
    </h1>

    <p class="hero-subtitle">
        Visualize a matriz curricular, consulte pré-requisitos,
        veja quais disciplinas são liberadas e explore
        os componentes de cada área do curso.
    </p>

    <div class="hero-badges">
        <span class="hero-badge">
            Disciplinas obrigatórias
        </span>
        <span class="hero-badge">
            Disciplinas eletivas
        </span>
        <span class="hero-badge">
            Pré-requisitos
        </span>
        <span class="hero-badge">
            Áreas da Engenharia de Produção
        </span>
    </div>
</div>

<div class="legend">
    <div class="legend-item">
        <span class="swatch blue"></span>
        Obrigatória
    </div>

    <div class="legend-item">
        <span class="swatch yellow"></span>
        Eletiva
    </div>

    <div class="legend-item">
        <span
            class="swatch"
            style="background:#d9f4df; border-color:#2f8f4e;"
        ></span>
        Pré-requisito da disciplina em foco
    </div>

    <div class="legend-item">
        <span
            class="swatch"
            style="background:#eee3ff; border-color:#7a4bc2;"
        ></span>
        Disciplina liberada pela disciplina em foco
    </div>
</div>
""")


st.caption(
    "Passe o mouse sobre uma disciplina. "
    "Os pré-requisitos ficam verdes e as disciplinas "
    "que ela libera ficam roxas. "
    "O texto com os detalhes continua disponível."
)


tab_periodos, tab_areas, tab_matrizes, tab_prog = st.tabs(
    [
        "📅 Por período",
        "🧭 Áreas",
        "📋 Matrizes completas",
        "✅ Minha matriz",
    ]
)


with tab_periodos:
    st.subheader(
        "Matriz curricular organizada por período"
    )

    st.caption(
        "Esta visualização reproduz a organização "
        "da matriz principal."
    )

    render_matriz_periodos()


with tab_areas:
    areas = sorted(
        [
            area
            for area
            in df["area"].unique().tolist()
            if area
        ],
        key=lambda texto: int(
            texto.split(".")[0]
        )
    )

    area = st.selectbox(
        "Selecione a área",
        areas,
        format_func=nome_area
    )

    area_df = df[
        df["area"] == area
    ].copy().sort_values(
        "ref"
    )

    obrig_area = area_df[
        area_df["tipo"] == "Obrigatória"
    ]

    elet_area = area_df[
        area_df["tipo"] == "Eletiva"
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Obrigatórias",
        len(obrig_area)
    )

    c2.metric(
        "Eletivas",
        len(elet_area)
    )

    c3.metric(
        "Carga horária listada",
        f'{area_df["carga_horaria"].sum()} h'
    )

    st.subheader(
        f"Disciplinas de {nome_area(area)}"
    )

    st.caption(
        "Aqui aparecem somente as disciplinas "
        "que pertencem à área selecionada."
    )

    render_cards(
        area_df,
        ordenar_por_ref=True
    )


with tab_matrizes:
    st.subheader(
        "Tabela 1 | Disciplinas organizadas por período"
    )

    st.caption(
        "A organização segue a primeira matriz enviada."
    )

    render_matriz_periodos()

    st.divider()

    st.subheader(
        "Tabela 2 | Disciplinas organizadas por área"
    )

    st.caption(
        "Nesta tabela as disciplinas obrigatórias e eletivas "
        "aparecem misturadas nas respectivas áreas, "
        "como na segunda matriz enviada."
    )

    render_matriz_areas()


with tab_prog:
    st.subheader(
        "Minha matriz curricular"
    )

    st.caption(
        "Selecione as disciplinas que você já cursou. "
        "Elas continuarão aparecendo na matriz e ficarão vermelhas."
    )

    opcoes = df.sort_values(
        [
            "periodo_num",
            "area",
            "ref"
        ],
        na_position="last"
    )

    label_por_ref = {
        linha["ref"]:
        (
            f'{linha["nome"]} | '
            f'{linha["codigo"]} '
            f'[{linha["ref"]}]'
        )
        for _, linha
        in opcoes.iterrows()
    }

    concluidas = st.multiselect(
        "Disciplinas já cursadas",
        options=list(
            label_por_ref.keys()
        ),
        format_func=lambda ref:
            label_por_ref[ref],
        placeholder=(
            "Selecione uma ou mais disciplinas"
        )
    )

    concluidas = set(
        concluidas
    )

    c1, c2, c3 = st.columns(3)

    obrig = df[
        df["tipo"] == "Obrigatória"
    ]

    obrig_concl = obrig[
        obrig["ref"].isin(
            concluidas
        )
    ]

    elet_concl = df[
        (df["tipo"] == "Eletiva")
        & (df["ref"].isin(
            concluidas
        ))
    ]

    c1.metric(
        "Disciplinas selecionadas",
        len(concluidas)
    )

    c2.metric(
        "Obrigatórias cursadas",
        len(obrig_concl)
    )

    c3.metric(
        "Eletivas cursadas",
        len(elet_concl)
    )

    st.html(
        """
        <div class="legend">
            <div class="legend-item">
                <span
                    class="swatch"
                    style="
                        background:#ffd9d9;
                        border-color:#c93636;
                    "
                ></span>
                Disciplina já cursada
            </div>
        </div>
        """
    )

    st.subheader(
        "Matriz organizada por período"
    )

    render_matriz_periodos(
        concluidas
    )

    st.divider()

    st.subheader(
        "Matriz organizada por área"
    )

    render_matriz_areas(
        concluidas
    )


st.divider()

st.caption(
    "Quando a matriz apresenta ??, "
    "a disciplina é tratada como sem pré-requisito."
)
