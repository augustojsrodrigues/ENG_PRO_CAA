# Matriz Interativa — Engenharia de Produção

Aplicativo em Streamlit para visualizar:

- todas as disciplinas obrigatórias em conjunto;
- disciplinas eletivas;
- áreas da Engenharia de Produção;
- pré-requisitos ao passar o mouse sobre a disciplina;
- disciplinas que são liberadas por cada componente;
- acompanhamento simples do progresso do aluno.

## Estrutura

```text
engenharia_producao_streamlit/
├── app.py
├── requirements.txt
├── data/
│   └── disciplinas.csv
├── .streamlit/
│   └── config.toml
└── referencias/
    ├── matriz_periodos.jpeg
    └── matriz_areas.jpeg
```

## Como colocar no GitHub

1. Crie um repositório novo.
2. Envie **todo o conteúdo da pasta**, preservando as subpastas `data`, `.streamlit` e `referencias`.
3. No Streamlit Community Cloud, escolha o repositório.
4. Em `Main file path`, use:

```text
app.py
```

5. Faça o deploy.

## Como editar disciplinas

A base está em:

```text
data/disciplinas.csv
```

Campos principais:

- `ref`: posição da disciplina na matriz (ex.: `5B`, `11A`);
- `nome`;
- `codigo`;
- `carga_horaria`;
- `tipo`: `Obrigatória` ou `Eletiva`;
- `periodo`;
- `area`;
- `pre_requisitos_refs`: referências separadas por `;`;
- `pre_requisito_observacao`;
- `origem`.

O aplicativo calcula automaticamente **quais disciplinas são liberadas** a partir dos pré-requisitos.

## Pontos que precisam de confirmação

A transcrição foi feita a partir das imagens fornecidas e não inventa informação quando a imagem é ambígua.

1. **Cálculo Dif. e Int. 4 (4A)**: o pré-requisito aparece como `??`.
2. **Custos de Produção (5C)**: o pré-requisito aparece como `??`.
3. **Gestão da Inovação (18B)**: o pré-requisito aparece como `iB` e ficou sem conversão automática.
4. **Manufatura Integrada por Computador (15E)**: a imagem mostra o código `PROD0037`, que também aparece em Gestão da Produção 2. O valor foi preservado exatamente como aparece na matriz e deve ser conferido no PPC/SIGAA.
5. A imagem mostra as disciplinas que compõem cada área, mas **não informa a regra de quantas eletivas precisam ser cursadas para fechar a área**. O aplicativo, portanto, lista as eletivas sem assumir que todas são obrigatórias.

Quando essas regras forem fornecidas, é possível incluir no aplicativo um indicador do tipo **“Área de Qualidade: 80% concluída / faltam X horas eletivas”**.
