from io import BytesIO
import re
import unicodedata

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Baterias | Painel executivo",
    page_icon="🔋",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #122a34;
        --muted: #687d83;
        --green: #13a878;
        --orange: #f08a32;
        --canvas: #f3f7f6;
    }

    html, body, [class*="css"] { font-family: 'Segoe UI', 'Aptos', sans-serif; }
    .stApp { background: var(--canvas); color: var(--ink); }
    [data-testid="stHeader"] { background: rgba(243, 247, 246, .92); }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e4ece9; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--ink); }
    h1, h2, h3 { font-family: 'Segoe UI', 'Aptos', sans-serif; color: var(--ink); letter-spacing: -.035em; }
    h1 { font-size: clamp(2rem, 4vw, 3.15rem) !important; font-weight: 800 !important; }
    h2 { font-weight: 750 !important; }
    p, label, [data-testid="stCaptionContainer"] { color: var(--muted); }
    .block-container { max-width: 1480px; padding-top: 2rem; padding-bottom: 3rem; }
    .hero {
        position: relative; overflow: hidden; display: flex; justify-content: space-between;
        align-items: center; gap: 24px; padding: 30px 34px; margin: 4px 0 20px;
        border-radius: 24px; color: #fff;
        background: radial-gradient(ellipse at 88% 10%, #29bf88 0, transparent 32%),
                    linear-gradient(120deg, #102e3a 0%, #164b50 55%, #147c67 100%);
        box-shadow: 0 18px 44px #153d3a20;
    }
    .hero h1 { margin: 4px 0 8px; color: #fff !important; }
    .hero p { margin: 0; max-width: 650px; color: #d5eae3; font-size: 1rem; }
    .hero-kicker { color: #83e5bd; font-size: .73rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
    .hero-art { width: 250px; min-width: 180px; height: auto; filter: drop-shadow(0 12px 14px #061e2233); }
    .section-label { margin: 26px 0 12px; color: #718389; font-size: .72rem; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
    [data-testid="stFileUploader"] section {
        border: 1px dashed #18a675; border-radius: 13px; background: #f4fcf8;
    }
    [data-testid="stFileUploader"] button, div.stButton > button, div.stDownloadButton > button {
        min-height: 44px; border: 1px solid #d9e6e1; border-radius: 12px;
        background: #fff; color: var(--ink); font-weight: 700; transition: .18s ease;
    }
    [data-testid="stFileUploader"] button {
        border-color: #13a878; background: #13a878; color: #fff;
    }
    [data-testid="stFileChipDeleteBtn"],
    [data-testid="stFileChipDeleteBtn"] button,
    [data-testid="stFileChips"] button[aria-label="Add files"] {
        box-sizing: border-box; width: 24px; min-width: 24px; max-width: 24px;
        height: 44px; min-height: 44px; padding: 0; flex: 0 0 24px;
    }
    [data-testid="stFileChipDeleteBtn"] { margin-left: 28px; }
    [data-testid="stFileChipDeleteBtn"] button svg { display: none; }
    [data-testid="stFileChipDeleteBtn"] button { position: relative; }
    [data-testid="stFileChipDeleteBtn"] button::before {
        content: ""; position: absolute; top: 50%; left: 50%;
        width: 10px; height: 2px; border-radius: 2px;
        background: currentColor; transform: translate(-50%, -50%);
    }
    [data-testid="stFileChips"] button[aria-label="Add files"] {
        z-index: 1; margin-left: -64px;
    }
    [data-testid="stFileUploader"] button:hover, div.stButton > button:hover,
    div.stDownloadButton > button:hover { border-color: #0d8d62; color: #0d8d62; }
    [data-testid="stFileUploader"] button:hover { background: #0d8d62; color: #fff; }
    div.stButton > button:focus, [data-testid="stFileUploader"] button:focus {
        box-shadow: 0 0 0 3px #13a87825;
    }
    .st-key-analytics_controls div.stButton > button,
    .st-key-analytics_controls div.stDownloadButton > button {
        box-sizing: border-box; min-height: 44px;
    }
    [data-testid="stMetric"] {
        background: #fff; border: 1px solid #e5eeea; border-radius: 18px;
        padding: 20px 22px; box-shadow: 0 8px 24px #183c350a;
    }
    [data-testid="stMetricLabel"] p { font-size: .88rem; font-weight: 700; color: #63787c; }
    [data-testid="stMetricValue"] { color: var(--ink); font-family: 'Segoe UI', 'Aptos', sans-serif; font-weight: 800; }
    .metric-card { min-height: 126px; padding: 20px 22px; border: 1px solid #e5eeea;
        border-top: 4px solid #9aaeb0; border-radius: 18px; background: #fff;
        box-shadow: 0 8px 24px #183c350a; }
    .metric-card--installed { border-top-color: var(--green); }
    .metric-card--omr { border-top-color: #39a9f5; }
    .metric-card--completion { border-top-color: #39a9f5; }
    .metric-card__label { color: #63787c; font-size: .88rem; font-weight: 700; }
    .metric-card__value { margin: 7px 0 3px; color: var(--ink); font: 800 1.9rem 'Segoe UI', 'Aptos', sans-serif; }
    .metric-progress { height: 6px; margin: 9px 0 5px; overflow: hidden; border-radius: 999px; background: #e8eff1; }
    .metric-progress__fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #39a9f5, #13a878); }
    .battery-icon { width: 22px; height: 22px; margin-right: 6px; vertical-align: -5px; }
    .stButton:has(button div[title*="Baterias não instaladas"]) button {
        display: block; min-height: 126px; width: 100%; padding: 16px 12px; border: 1px solid #e5eeea;
        border-top: 4px solid var(--orange); border-radius: 18px; background: #fff;
        box-shadow: 0 8px 24px #183c350a; text-align: left; white-space: normal;
    }
    .stButton:has(button div[title*="Baterias não instaladas"]) button > div {
        width: 100%; align-items: flex-start; justify-content: flex-start;
    }
    .stButton:has(button div[title*="Baterias não instaladas"]) [data-testid="stMarkdownContainer"] {
        width: 100%; overflow: visible; white-space: normal !important; text-overflow: clip;
    }
    .stButton:has(button div[title*="Baterias não instaladas"]) button:hover {
        border-color: #f0b16d; background: #fffaf5;
    }
    .stButton:has(button div[title*="Baterias não instaladas"]) button p {
        display: block !important; margin: 0; white-space: normal !important; overflow-wrap: anywhere;
    }
    .stButton:has(button div[title*="Baterias não instaladas"]) button p:first-child {
        color: #63787c; font-size: .78rem; font-weight: 700;
    }
    .stButton:has(button div[title*="Baterias não instaladas"]) button p:nth-child(2) {
        margin: 7px 0 3px; color: var(--ink); font-size: 1.9rem; font-weight: 800;
    }
    .panel {
        background: #fff; border: 1px solid #e4ece9; border-radius: 18px;
        padding: 18px 20px; box-shadow: 0 8px 24px #183c350a; margin: 10px 0;
    }
    .panel-title { color: var(--ink); font-family: 'Manrope', sans-serif; font-size: 1.05rem; font-weight: 800; }
    .panel-subtitle { margin-top: 5px; color: var(--muted); font-size: .83rem; }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"]) {
        padding: 14px 16px; border: 1px solid #263e49; border-radius: 18px;
        background: linear-gradient(145deg, #142f3b, #0e2631);
        box-shadow: 0 12px 30px #102a351c;
    }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"]) .panel {
        margin: 0 0 10px; padding: 2px 2px 8px; border: 0;
        background: transparent; box-shadow: none;
    }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"]) .panel-title { color: #f1f7f8; }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"]) .panel-subtitle { color: #a9c0c9; }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"])
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background: #102936;
        border: 1px solid #fff;
        color: #fff;
        box-shadow: none;
    }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"])
    [data-testid="stSelectbox"] [data-baseweb="select"] *,
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"])
    [data-testid="stSelectbox"] [data-baseweb="select"] svg {
        color: #fff;
        fill: #fff;
    }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"])
    [data-testid="stSelectbox"] [data-baseweb="select"]:hover > div,
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"])
    [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
        border-color: #fff;
        box-shadow: 0 0 0 1px #fff;
    }
    div[data-testid="stColumn"]:has([data-testid="stVegaLiteChart"]) [data-testid="stVegaLiteChart"] {
        overflow: visible; border-radius: 12px;
    }
    .justification {
        border-left: 4px solid var(--orange); border-radius: 0 12px 12px 0;
        background: #fff8f1; padding: 13px 16px; margin: 7px 0; color: #654528;
    }
    .floating-analytics {
        position: fixed; right: 24px; bottom: 24px; z-index: 999;
        width: min(340px, calc(100vw - 40px)); padding: 18px 20px;
        border: 1px solid #cfe6dc; border-radius: 18px; background: #fff;
        box-shadow: 0 18px 55px #122a3440; color: var(--ink);
    }
    .floating-analytics strong { display: block; margin-bottom: 8px; font: 800 1rem 'Segoe UI', 'Aptos', sans-serif; }
    .floating-analytics span { display: block; padding: 5px 0; color: #587078; font-size: .82rem; }
    [data-testid="stDataFrame"] { border: 1px solid #e4ece9; border-radius: 14px; overflow: hidden; }
    @media (max-width: 720px) {
        .hero { padding: 24px 20px; }
        .hero-art { width: 125px; min-width: 100px; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
    }
    @media (max-width: 520px) {
        .hero-art { display: none; }
        .hero { padding: 22px 18px; border-radius: 18px; }
        .st-key-analytics_controls div.stButton > button,
        .st-key-analytics_controls div.stDownloadButton > button {
            width: 100%; min-width: 0;
        }
        .metric-card, .stButton:has(button div[title*="Baterias não instaladas"]) button {
            min-height: 112px; padding: 15px;
        }
        .metric-card__value,
        .stButton:has(button div[title*="Baterias não instaladas"]) button p:nth-child(2) {
            font-size: 1.6rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def make_unique_columns(columns):
    used = set()
    counts = {}
    unique = []
    for column in columns:
        base = str(column).strip() or "Coluna"
        counts[base] = counts.get(base, 0) + 1
        name = base if counts[base] == 1 else f"{base}_{counts[base]}"
        while name in used:
            counts[base] += 1
            name = f"{base}_{counts[base]}"
        used.add(name)
        unique.append(name)
    return unique


def promote_first_row_to_header(data):
    if data.empty or len(data.columns) < 2:
        return data

    placeholders = [
        not str(column).strip()
        or bool(re.fullmatch(r"Unnamed:\s*\d+", str(column).strip(), re.IGNORECASE))
        or pd.notna(pd.to_numeric(str(column).strip(), errors="coerce"))
        for column in data.columns
    ]
    minimum_labels = max(2, (len(data.columns) + 1) // 2)
    if sum(placeholders) < minimum_labels:
        return data

    first_row = data.iloc[0]
    labels = first_row.astype("string").str.strip()
    text_labels = labels.notna() & labels.ne("") & pd.to_numeric(
        labels, errors="coerce"
    ).isna()
    if int(text_labels.sum()) < minimum_labels:
        return data

    promoted = [
        label if pd.notna(label) and label else old_name
        for label, old_name in zip(labels, data.columns)
    ]
    data = data.iloc[1:].copy()
    data.columns = make_unique_columns(promoted)
    return data.reset_index(drop=True)


@st.cache_data(show_spinner="Lendo arquivo...")
def read_uploaded_file(file_bytes, file_name):
    extension = file_name.rsplit(".", 1)[-1].lower()
    if extension in {"xlsx", "xls"}:
        data = pd.read_excel(BytesIO(file_bytes))
    else:
        last_error = None
        for encoding in ("utf-8-sig", "cp1252"):
            try:
                data = pd.read_csv(
                    BytesIO(file_bytes),
                    sep=None,
                    engine="python",
                    encoding=encoding,
                )
                break
            except (
                UnicodeDecodeError,
                pd.errors.EmptyDataError,
                pd.errors.ParserError,
            ) as error:
                last_error = error
        else:
            raise ValueError(f"Não foi possível ler o CSV: {last_error}") from last_error
    data = promote_first_row_to_header(data)
    data.columns = make_unique_columns(data.columns)
    return data


def normalize_text(value):
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text.casefold()).strip()


def suggested_column(columns, keywords):
    normalized_keywords = [normalize_text(keyword) for keyword in keywords]
    for keyword in normalized_keywords:
        for column in columns:
            if normalize_text(column) == keyword:
                return column
    for column in columns:
        normalized = normalize_text(column)
        if any(keyword in normalized for keyword in normalized_keywords):
            return column
    return None


def parse_date_series(values):
    iso_dates = pd.to_datetime(values, errors="coerce", format="ISO8601")
    remaining = iso_dates.isna() & values.notna()
    if remaining.any():
        flexible_dates = pd.to_datetime(
            values.loc[remaining],
            errors="coerce",
            format="mixed",
            dayfirst=True,
        )
        iso_dates = iso_dates.combine_first(flexible_dates)
    return iso_dates


def style_dashboard_chart(chart):
    return (
        chart.properties(background="#102936")
        .configure_view(strokeOpacity=0)
        .configure_axis(
            labelColor="#c5d6dc",
            titleColor="#c5d6dc",
            domainColor="#49616a",
            tickColor="#49616a",
            gridColor="#334b55",
            gridOpacity=0.65,
            labelFontSize=10,
            titleFontSize=11,
        )
        .configure_legend(
            labelColor="#d8e5e9",
            titleColor="#d8e5e9",
            orient="bottom",
            direction="horizontal",
        )
    )


def select_column(
    label, columns, keywords=(), include_none=True, fallback_column=None
):
    options = (["(Não usar)"] if include_none else []) + list(columns)
    default = suggested_column(columns, keywords) or fallback_column
    index = options.index(default) if default in options else 0
    selected = st.selectbox(label, options, index=index)
    return None if selected == "(Não usar)" else selected


def apply_value_filter(data, column, label, key):
    values = data[column].astype("string").str.strip()
    blank_mask = values.isna() | values.eq("")
    options = values.loc[~blank_mask].dropna().unique().tolist()
    blank_label = "(Células vazias)"
    while blank_label in options:
        blank_label = f"_{blank_label}"
    if blank_mask.any():
        options.append(blank_label)

    selected = st.sidebar.multiselect(label, options, default=options, key=key)
    selected_values = [value for value in selected if value != blank_label]
    keep_rows = values.isin(selected_values)
    if blank_label in selected:
        keep_rows |= blank_mask
    return data.loc[keep_rows]


def automatic_status(value):
    text = normalize_text(value)
    negative_terms = (
        "nao instalado", "nao instalada", "pendente", "aguardando",
        "nao realizado", "nao concluido", "cancelado", "falta instalacao",
    )
    positive_terms = (
        "instalado", "instalada", "concluido", "concluida",
        "finalizado", "finalizada", "realizado", "realizada",
    )
    if any(term in text for term in negative_terms):
        return False
    if any(term in text for term in positive_terms):
        return True
    return None


def format_number(value):
    if pd.isna(value):
        return "0"
    if float(value).is_integer():
        return f"{int(value):,}".replace(",", ".")
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def battery_illustration():
    return """
    <svg class="hero-art" viewBox="0 0 320 185" role="img" aria-label="Ilustração de uma bateria de lítio verde">
      <defs>
        <linearGradient id="body" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stop-color="#22d394"/><stop offset="1" stop-color="#079d70"/>
        </linearGradient>
        <linearGradient id="front" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#183b45"/><stop offset="1" stop-color="#102b34"/>
        </linearGradient>
      </defs>
      <rect x="56" y="20" width="54" height="24" rx="6" fill="#e8edf0"/>
      <rect x="211" y="20" width="54" height="24" rx="6" fill="#d7e1e4"/>
      <rect x="46" y="34" width="228" height="106" rx="14" fill="url(#body)"/>
      <path d="M46 69h228v57a14 14 0 0 1-14 14H60a14 14 0 0 1-14-14z" fill="url(#front)"/>
      <rect x="96" y="82" width="128" height="40" rx="8" fill="#ecfff6"/>
      <rect x="103" y="88" width="114" height="28" rx="5" fill="#18aa78"/>
      <text x="160" y="106" fill="#fff" font-size="12" font-family="Arial,sans-serif" font-weight="700" text-anchor="middle">LITHIUM ION</text>
      <text x="65" y="105" fill="#c8e6dc" font-size="13" font-family="Arial,sans-serif" font-weight="700">Li</text>
      <circle cx="247" cy="103" r="12" fill="none" stroke="#c8e6dc" stroke-width="2"/>
      <path d="M241 103h12" stroke="#c8e6dc" stroke-width="2"/>
      <rect x="68" y="28" width="28" height="10" rx="2" fill="#fa626a"/>
      <rect x="225" y="28" width="28" height="10" rx="2" fill="#d9e4e6"/>
      <text x="82" y="36" fill="#fff" font-size="12" font-family="Arial,sans-serif" font-weight="700" text-anchor="middle">+</text>
      <text x="239" y="36" fill="#304950" font-size="12" font-family="Arial,sans-serif" font-weight="700" text-anchor="middle">−</text>
    </svg>
    """


st.markdown(
    f"""
    <div class="hero">
      <div>
        <div class="hero-kicker">INFRAESTRUTURA CENTRO-OESTE</div>
        <h1>Acompanhamento de instalação de Bateria</h1>
      </div>
      {battery_illustration()}
    </div>
    """,
    unsafe_allow_html=True,
)

if "show_justifications" not in st.session_state:
    st.session_state.show_justifications = False
if "floating_analytics" not in st.session_state:
    st.session_state.floating_analytics = False
if "show_completion_by_uf" not in st.session_state:
    st.session_state.show_completion_by_uf = False
if "show_pending_card" not in st.session_state:
    st.session_state.show_pending_card = False


if "show_imported_data" not in st.session_state:
    st.session_state.show_imported_data = False


def hide_imported_data_on_upload_change():
    st.session_state.show_imported_data = False
    st.session_state.show_completion_by_uf = False
    st.session_state.show_pending_card = False
    st.session_state.show_justifications = False
    st.session_state.pop("analysis_period", None)


def toggle_completion_by_uf():
    st.session_state.show_completion_by_uf = (
        not st.session_state.show_completion_by_uf
    )


def toggle_pending_card():
    st.session_state.show_pending_card = not st.session_state.show_pending_card
    if not st.session_state.show_pending_card:
        st.session_state.show_justifications = False


with st.container():
    st.markdown('<div class="section-label">Importação de dados</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Pesquisar arquivo CSV ou Excel",
        type=["csv", "xlsx", "xls"],
        help="Selecione um arquivo .csv, .xlsx ou .xls para alimentar os indicadores.",
        key="battery_upload",
        label_visibility="collapsed",
        on_change=hide_imported_data_on_upload_change,
    )

if uploaded_file is None:
    st.stop()

try:
    df = read_uploaded_file(uploaded_file.getvalue(), uploaded_file.name)
except (ValueError, ImportError, OSError) as error:
    st.error(f"Erro ao abrir o arquivo: {error}")
    st.stop()

if df.empty:
    st.warning("O arquivo não contém linhas para analisar.")
    st.stop()

st.sidebar.header("Filtros e campos")
st.sidebar.caption(f"Arquivo carregado: {uploaded_file.name}")
all_columns = list(df.columns)
numeric_columns = list(df.select_dtypes(include="number").columns)
date_candidates = [
    column
    for column in all_columns
    if pd.api.types.is_datetime64_any_dtype(df[column])
    or any(word in normalize_text(column) for word in ("data", "date", "hora", "time"))
]
category_candidates = [
    column for column in all_columns
    if column not in numeric_columns and column not in date_candidates
]

with st.sidebar.expander("Mapeamento das colunas", expanded=True):
    quantity_column = select_column(
        "Quantidade", all_columns,
        ("quant", "qtd", "estoque", "saldo", "volume", "units"),
        fallback_column=next(iter(numeric_columns), None),
    )
    uf_column = select_column("UF", all_columns, ("ufs", "uf", "estado", "state"))
    planned_date_candidates = [
        column
        for column in date_candidates
        if any(
            term in normalize_text(column)
            for term in ("planejada", "planejado", "planned")
        )
    ]
    installation_date_candidates = [
        column for column in date_candidates if column not in planned_date_candidates
    ]
    installation_date_column = select_column(
        "Data da instalação", all_columns,
        ("data instalação", "data de instalação", "data efetiva instalação", "installation date"),
        fallback_column=next(iter(installation_date_candidates), None),
    )
    planned_installation_date_column = select_column(
        "Data planejada da instalação", all_columns,
        ("data planejada instalação", "data planejada de instalação", "planned installation date"),
        fallback_column=next(iter(planned_date_candidates), None),
    )
    status_column = select_column(
        "Status da instalação", all_columns,
        ("status", "condicao", "condição", "situacao", "situação"),
        fallback_column=next(iter(category_candidates), None),
    )
    justification_column = select_column(
        "Justificativa da pendência", all_columns,
        ("justificativa", "motivo", "observacao", "observação", "pendencia", "pendência"),
    )
    location_column = select_column(
        "Localização", all_columns,
        ("local", "unidade", "filial", "deposito", "depósito"),
        fallback_column=next(
            (
                column
                for column in category_candidates
                if column not in {uf_column, status_column, justification_column}
            ),
            None,
        ),
    )
    category_column = select_column(
        "Categoria para o gráfico", all_columns,
        ("tipo", "bateria", "modelo", "produto", "categoria"),
        fallback_column=next(
            (
                column for column in all_columns
                if column not in {
                    uf_column, status_column, justification_column, location_column,
                    installation_date_column, planned_installation_date_column,
                }
            ),
            status_column or location_column or uf_column,
        ),
    )

filtered = df.copy()
date_series = None
if installation_date_column:
    date_series = parse_date_series(filtered[installation_date_column])
    valid_dates = date_series.dropna()
    if not valid_dates.empty:
        first_available_date = valid_dates.min().date()
        last_available_date = valid_dates.max().date()
        period_min_date = first_available_date.replace(month=1, day=1)
        period_max_date = last_available_date.replace(month=12, day=31)
        date_range = st.sidebar.date_input(
            "Período da análise",
            value=(first_available_date, last_available_date),
            min_value=period_min_date,
            max_value=period_max_date,
            key="analysis_period",
        )
        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range
        in_period = date_series.between(
            pd.Timestamp(start_date),
            pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1),
        )
        filtered = filtered[in_period | date_series.isna()]
    else:
        st.sidebar.warning(
            "Não foi possível interpretar as datas para filtrar o período; "
            "células preenchidas ainda são contadas como instalações."
        )

if uf_column:
    filtered = apply_value_filter(filtered, uf_column, "Filtrar UFs", "filter_ufs")

if status_column:
    filtered = apply_value_filter(
        filtered, status_column, "Filtrar status", "filter_statuses"
    )

if category_column and category_column != status_column:
    category_values = (
        filtered[category_column].dropna().astype(str).str.strip().unique().tolist()
    )
    if len(category_values) <= 100:
        filtered = apply_value_filter(
            filtered, category_column, "Filtrar categoria", "filter_categories"
        )

if location_column:
    location_values = (
        filtered[location_column].dropna().astype(str).str.strip().unique().tolist()
    )
    if len(location_values) <= 100:
        filtered = apply_value_filter(
            filtered, location_column, "Filtrar localização", "filter_locations"
        )

if filtered.empty:
    st.warning("Nenhum registro corresponde aos filtros selecionados.")
    st.stop()

installed_mask = pd.Series(False, index=filtered.index)
not_installed_mask = pd.Series(False, index=filtered.index)
omr_mask = pd.Series(False, index=filtered.index)
classification_available = False

if planned_installation_date_column:
    planned_installation_values = (
        filtered[planned_installation_date_column]
        .astype("string")
        .str.strip()
        .map(normalize_text)
    )
    omr_mask = planned_installation_values.str.contains(
        "executado omr", regex=False, na=False
    )

if installation_date_column:
    raw_installation_dates = filtered[installation_date_column]
    installed_mask = parse_date_series(raw_installation_dates).notna()
    not_installed_mask = (
        raw_installation_dates.astype("string").str.strip().eq("").fillna(False)
        & ~omr_mask
    )
    classification_available = True
elif status_column:
    raw_statuses = filtered[status_column].astype(str)
    auto_labels = {
        value: automatic_status(value)
        for value in raw_statuses.dropna().unique()
    }
    installed_labels = [value for value, result in auto_labels.items() if result is True]
    not_installed_labels = [value for value, result in auto_labels.items() if result is False]
    if installed_labels or not_installed_labels:
        installed_mask = raw_statuses.isin(installed_labels)
        not_installed_mask = raw_statuses.isin(not_installed_labels)
        classification_available = True

uses_installation_entries = installation_date_column is not None
if uses_installation_entries:
    installed_total = int(installed_mask.sum())
    pending_total = int(not_installed_mask.sum())
    installed_unit_label = "instalações"
    pending_unit_label = "registros"
elif quantity_column:
    installed_total = pd.to_numeric(
        filtered.loc[installed_mask, quantity_column], errors="coerce"
    ).fillna(0).sum()
    pending_total = pd.to_numeric(
        filtered.loc[not_installed_mask, quantity_column], errors="coerce"
    ).fillna(0).sum()
    installed_unit_label = pending_unit_label = "unidades"
else:
    installed_total = int(installed_mask.sum())
    pending_total = int(not_installed_mask.sum())
    installed_unit_label = pending_unit_label = "registros"
omr_total = int(omr_mask.sum())
classified_total = installed_total + pending_total
if installation_date_column or planned_installation_date_column:
    completed_mask = installed_mask | omr_mask
    completion_rate = int(completed_mask.sum()) / len(filtered) * 100
elif classification_available and classified_total > 0:
    completion_rate = installed_total / classified_total * 100
else:
    completion_rate = None
total_analyzed = (
    pd.to_numeric(filtered[quantity_column], errors="coerce").fillna(0).sum()
    if quantity_column and not uses_installation_entries else len(filtered)
)
display_filtered = filtered.copy()
if installation_date_column:
    display_dates = parse_date_series(display_filtered[installation_date_column])
    date_only_values = display_dates.dt.strftime("%Y-%m-%d")
    display_filtered[installation_date_column] = date_only_values.where(
        display_dates.notna(), display_filtered[installation_date_column]
    )

summary_title, pending_toggle_column = st.columns([3, 1], vertical_alignment="center")
with summary_title:
    st.markdown('<div class="section-label">Resumo operacional</div>', unsafe_allow_html=True)
with pending_toggle_column:
    st.button(
        "Ocultar baterias não instaladas"
        if st.session_state.show_pending_card
        else "Mostrar baterias não instaladas",
        key="toggle_pending_card",
        on_click=toggle_pending_card,
        use_container_width=True,
    )

metric_columns = st.columns(6 if st.session_state.show_pending_card else 5)
if st.session_state.show_pending_card:
    installed_col, omr_col, pending_col, total_col, uf_col, completion_col = metric_columns
else:
    installed_col, omr_col, total_col, uf_col, completion_col = metric_columns
with installed_col:
    st.markdown(
        f'<div class="metric-card metric-card--installed"><div class="metric-card__label">'
        f'<svg class="battery-icon" viewBox="0 0 28 28" role="img" aria-label="Bateria de lítio verde">'
        f'<rect x="7" y="5" width="14" height="20" rx="3" fill="#13a878"/>'
        f'<rect x="11" y="2" width="6" height="4" rx="1" fill="#13a878"/>'
        f'<path d="M15 8l-5 8h4l-1 5 5-8h-4z" fill="#fff"/>'
        f'</svg>Baterias Instaladas</div>'
        f'<div class="metric-card__value">{format_number(installed_total)}</div></div>',
        unsafe_allow_html=True,
    )
with omr_col:
    omr_total_label = (
        format_number(omr_total) if planned_installation_date_column else "—"
    )
    st.markdown(
        f'<div class="metric-card metric-card--omr">'
        f'<div class="metric-card__label">Executado OMR</div>'
        f'<div class="metric-card__value">{omr_total_label}</div></div>',
        unsafe_allow_html=True,
    )
if st.session_state.show_pending_card:
    with pending_col:
        if st.button(
            f"🟠 **Baterias não instaladas**\n\n**{format_number(pending_total)}**",
            key="pending_card",
            use_container_width=True,
        ):
            st.session_state.show_justifications = (
                not st.session_state.show_justifications
            )
with total_col:
    st.markdown(
        f'<div class="metric-card"><div class="metric-card__label">Total analisado</div>'
        f'<div class="metric-card__value">{format_number(total_analyzed)}</div></div>',
        unsafe_allow_html=True,
    )
with uf_col:
    st.markdown(
        f'<div class="metric-card"><div class="metric-card__label">UFs na seleção</div>'
        f'<div class="metric-card__value">{filtered[uf_column].nunique() if uf_column else "—"}</div></div>',
        unsafe_allow_html=True,
    )
with completion_col:
    completion_label = (
        f'{completion_rate:.1f}%'.replace(".", ",")
        if completion_rate is not None
        else "—"
    )
    completion_width = completion_rate if completion_rate is not None else 0
    st.markdown(
        f'<div class="metric-card metric-card--completion">'
        f'<div class="metric-card__label">Taxa de conclusão</div>'
        f'<div class="metric-card__value">{completion_label}</div>'
        f'<div class="metric-progress" role="meter" aria-label="Taxa de conclusão" '
        f'aria-valuemin="0" aria-valuemax="100" '
        f'aria-valuenow="{completion_width:.1f}" aria-valuetext="{completion_label}">'
        f'<div class="metric-progress__fill" style="width: {completion_width:.1f}%"></div></div></div>',
        unsafe_allow_html=True,
    )

if not classification_available:
    st.info("Para separar instaladas e pendentes, mapeie uma coluna de status reconhecível ou uma data de instalação.")

if st.session_state.show_justifications:
    st.markdown('<div class="section-label">Justificativas das baterias não instaladas</div>', unsafe_allow_html=True)
    pending_rows = display_filtered.loc[not_installed_mask]
    if pending_rows.empty:
        st.info("Não há baterias pendentes dentro da seleção atual.")
    elif justification_column:
        details = pending_rows.copy()
        details[justification_column] = (
            details[justification_column].fillna("").astype(str).str.strip()
            .replace("", "Justificativa não informada")
        )
        selected_detail_columns = []
        for column in (
            uf_column, location_column, status_column, justification_column,
            installation_date_column,
        ):
            if column and column not in selected_detail_columns:
                selected_detail_columns.append(column)
        st.dataframe(
            details[selected_detail_columns],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("Nenhuma coluna de justificativa foi identificada. Ajuste o mapeamento na barra lateral.")
        st.dataframe(pending_rows, use_container_width=True, hide_index=True)

st.markdown('<div class="section-label">Tendências e distribuição</div>', unsafe_allow_html=True)
chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown(
        '<div class="panel"><div class="panel-title">Evolução das instalações</div>'
        '<div class="panel-subtitle">Instalações ao longo do tempo</div></div>',
        unsafe_allow_html=True,
    )
    if installation_date_column and installed_mask.any():
        granularity = st.selectbox(
            "Agrupar por", ["Dia", "Semana", "Mês"], index=2,
            key="timeline_granularity",
            label_visibility="collapsed",
        )
        frequency = {"Dia": "D", "Semana": "W", "Mês": "ME"}[granularity]
        timeline_rows = filtered.loc[installed_mask].copy()
        timeline_rows[installation_date_column] = parse_date_series(
            timeline_rows[installation_date_column]
        )
        timeline_rows = timeline_rows.dropna(subset=[installation_date_column]).set_index(
            installation_date_column
        )
        if timeline_rows.empty:
            st.info("Não há datas válidas de instalação dentro da seleção atual.")
        else:
            if not uses_installation_entries and quantity_column:
                timeline = pd.to_numeric(
                    timeline_rows[quantity_column], errors="coerce"
                ).fillna(0).resample(frequency).sum()
            else:
                timeline = timeline_rows.resample(frequency).size()
            timeline.name = "Instalações"
            timeline_frame = timeline.rename_axis("Data").reset_index()
            first_date = timeline.index.min()
            last_date = timeline.index.max()
            padding = (
                last_date - first_date
                if first_date != last_date
                else pd.Timedelta(days={"Dia": 1, "Semana": 7, "Mês": 31}[granularity])
            )
            if first_date != last_date:
                padding *= 0.05
            timeline_chart = (
                alt.Chart(timeline_frame)
                .mark_line(
                    point=alt.OverlayMarkDef(filled=True, size=55, color="#4bd4a1"),
                    color="#4bd4a1",
                    strokeWidth=3,
                )
                .encode(
                    x=alt.X(
                        "Data:T",
                        title=None,
                        axis=alt.Axis(format="%b", labelAngle=0),
                        scale=alt.Scale(
                            domain=[
                                (first_date - padding).isoformat(),
                                (last_date + padding).isoformat(),
                            ]
                        ),
                    ),
                    y=alt.Y("Instalações:Q", title=None),
                    tooltip=[
                        alt.Tooltip("Data:T", title="Data", format="%Y-%m-%d"),
                        alt.Tooltip("Instalações:Q", title="Instalações"),
                    ],
                )
                .properties(height=230)
            )
            st.altair_chart(style_dashboard_chart(timeline_chart), use_container_width=True)
    else:
        st.info("Mapeie uma coluna de data para exibir a evolução das instalações.")

with chart_right:
    st.markdown(
        '<div class="panel"><div class="panel-title">Instalações por UFs</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    distribution_column = uf_column
    if distribution_column:
        distribution_rows = (
            filtered.loc[installed_mask] if uses_installation_entries else filtered
        )
        if uses_installation_entries or not quantity_column:
            distribution_data = (
                distribution_rows[distribution_column]
                .fillna("Não informado")
                .astype(str)
                .value_counts()
                .rename("Instalações")
                .rename_axis("Grupo")
                .reset_index()
            )
        else:
            distribution_data = (
                distribution_rows.assign(
                    _count=pd.to_numeric(
                        distribution_rows[quantity_column], errors="coerce"
                    ).fillna(0)
                )
                .groupby(distribution_column, dropna=False)["_count"]
                .sum()
                .rename("Instalações")
                .rename_axis("Grupo")
                .reset_index()
                .rename(columns={distribution_column: "Grupo"})
            )
            distribution_data["Grupo"] = (
                distribution_data["Grupo"].fillna("Não informado").astype(str)
            )
        if distribution_data.empty:
            st.info("Não há instalações para distribuir na seleção atual.")
        else:
            distribution_total = distribution_data["Instalações"].sum()
            if distribution_total <= 0:
                st.info("Não há instalações com quantidade maior que zero para distribuir.")
            else:
                distribution_data["_Percentual"] = (
                    distribution_data["Instalações"] / distribution_total * 100
                )
                distribution_data["_Rotulo"] = distribution_data.apply(
                    lambda row: (
                        f'{row["Grupo"]}\n'
                        f'{format_number(row["Instalações"])}\n'
                        f'{row["_Percentual"]:.1f}%'
                    ).replace(".", ","),
                    axis=1,
                )
                chart_base = alt.Chart(distribution_data).encode(
                    theta=alt.Theta("Instalações:Q", stack=True),
                    order=alt.Order("Instalações:Q", sort="descending"),
                )
                donut_chart = alt.layer(
                    chart_base.mark_arc(
                        innerRadius=82,
                        outerRadius=132,
                        stroke="#102936",
                        strokeWidth=2,
                    ).encode(
                        color=alt.Color(
                            "Grupo:N",
                            legend=alt.Legend(
                                title=distribution_column,
                                orient="bottom",
                                direction="horizontal",
                                labelLimit=100,
                            ),
                            scale=alt.Scale(
                                range=["#25c993", "#39a9f5", "#ffad45", "#9b8cff", "#f27991", "#5bd4cf"]
                            ),
                        ),
                        tooltip=[
                            alt.Tooltip("Grupo:N", title=distribution_column),
                            alt.Tooltip("Instalações:Q", title="Quantidade"),
                            alt.Tooltip("_Percentual:Q", title="Percentual", format=".1f"),
                        ],
                    ),
                    chart_base.mark_text(
                        radius=106,
                        color="#ffffff",
                        fontSize=10,
                        fontWeight="bold",
                        lineBreak="\n",
                        lineHeight=12,
                    ).encode(
                        text=alt.Text("_Rotulo:N"),
                        color=alt.value("#ffffff"),
                    ),
                ).properties(height=370)
                st.altair_chart(
                    style_dashboard_chart(donut_chart), use_container_width=True
                )
    else:
        st.info("Mapeie uma UF para visualizar a distribuição das instalações.")

comparison_chart_column, = st.columns(1)
with comparison_chart_column:
    st.markdown(
        '<div class="panel"><div class="panel-title">Baterias instaladas x Executado OMR</div>'
        '<div class="panel-subtitle">Comparativo por UF nas colunas de instalação e data planejada</div></div>',
        unsafe_allow_html=True,
    )
    comparison_column = uf_column
    if comparison_column and (
        installation_date_column or planned_installation_date_column
    ):
        comparison_parts = []
        if installation_date_column:
            installed_rows = filtered.loc[installed_mask, [comparison_column]].copy()
            installed_rows["_StatusPainel"] = "Baterias Instaladas"
            comparison_parts.append(installed_rows)
        if planned_installation_date_column:
            omr_rows = filtered.loc[omr_mask, [comparison_column]].copy()
            omr_rows["_StatusPainel"] = "Executado OMR"
            comparison_parts.append(omr_rows)

        comparison_rows = pd.concat(comparison_parts, ignore_index=True)
        if comparison_rows.empty:
            st.info("Não há baterias instaladas ou registros OMR para comparar na seleção atual.")
        else:
            comparison_rows["_ValorPainel"] = 1
            comparison_rows["_GrupoPainel"] = (
                comparison_rows[comparison_column].fillna("Não informado").astype(str)
            )
            comparison_data = (
                comparison_rows.groupby(
                    ["_GrupoPainel", "_StatusPainel"], as_index=False
                )["_ValorPainel"]
                .sum()
                .rename(
                    columns={
                        "_GrupoPainel": "Grupo",
                        "_StatusPainel": "Status",
                        "_ValorPainel": "Registros",
                    }
                )
            )
            chart_series = [
                label
                for label, available in (
                    ("Baterias Instaladas", installation_date_column),
                    ("Executado OMR", planned_installation_date_column),
                )
                if available
            ]
            comparison_chart = (
                alt.Chart(comparison_data)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X(
                        "Grupo:N",
                        title=None,
                        axis=alt.Axis(labelAngle=0, labelOverlap=False),
                        sort="ascending",
                    ),
                    xOffset=alt.XOffset("Status:N"),
                    y=alt.Y("Registros:Q", title=None),
                    color=alt.Color(
                        "Status:N",
                        scale=alt.Scale(
                            domain=chart_series,
                            range=["#25c993", "#39a9f5"],
                        ),
                        legend=alt.Legend(title=None),
                    ),
                    tooltip=[
                        alt.Tooltip("Grupo:N", title=comparison_column),
                        alt.Tooltip("Status:N"),
                        alt.Tooltip("Registros:Q"),
                    ],
                )
                .properties(height=230)
            )
            st.altair_chart(
                style_dashboard_chart(comparison_chart), use_container_width=True
            )
    else:
        st.info(
            "Mapeie uma UF, Data Instalação e Data planejada instalação para comparar "
            "baterias instaladas e Executado OMR."
        )

st.button(
    "Ocultar percentual por UF"
    if st.session_state.show_completion_by_uf
    else "Mostrar percentual por UF",
    key="toggle_completion_by_uf",
    on_click=toggle_completion_by_uf,
)

if st.session_state.show_completion_by_uf:
    st.markdown(
        '<div class="panel"><div class="panel-title">Percentual de conclusão por UF</div>'
        '<div class="panel-subtitle">Linhas com data instalada ou Executado OMR sobre o total de cada UF</div></div>',
        unsafe_allow_html=True,
    )
if uf_column and (installation_date_column or planned_installation_date_column):
    completion_by_uf = filtered[[uf_column]].copy()
    completion_by_uf["_Concluida"] = (installed_mask | omr_mask).astype(int)
    completion_by_uf["_UF"] = (
        completion_by_uf[uf_column].fillna("Não informado").astype(str)
    )
    completion_by_uf = (
        completion_by_uf.groupby("_UF", as_index=False)
        .agg(
            Concluidas=("_Concluida", "sum"),
            Total=("_Concluida", "size"),
        )
        .rename(columns={"_UF": "UF"})
    )
    completion_by_uf["Percentual"] = (
        completion_by_uf["Concluidas"] / completion_by_uf["Total"] * 100
    )
    completion_by_uf["Rotulo"] = completion_by_uf["Percentual"].map(
        lambda value: f"{value:.1f}%".replace(".", ",")
    )
    completion_by_uf["Detalhe"] = completion_by_uf.apply(
        lambda row: f'{int(row["Concluidas"])} de {int(row["Total"])} linhas',
        axis=1,
    )
    percentage_base = alt.Chart(completion_by_uf).encode(
        x=alt.X(
            "UF:N",
            title=None,
            axis=alt.Axis(labelAngle=0, labelOverlap=False),
            sort=alt.SortField(field="Percentual", order="descending"),
        ),
        y=alt.Y(
            "Percentual:Q",
            title=None,
            scale=alt.Scale(domain=[0, 100]),
            axis=alt.Axis(format=".0f", title=None),
        ),
        tooltip=[
            alt.Tooltip("UF:N", title="UF"),
            alt.Tooltip("Percentual:Q", title="Conclusão", format=".1f"),
            alt.Tooltip("Detalhe:N", title="Linhas concluídas"),
        ],
    )
    percentage_chart = alt.layer(
        percentage_base.mark_bar(color="#39a9f5", cornerRadiusTopLeft=4, cornerRadiusTopRight=4),
        percentage_base.mark_text(
            dy=-9, color="#ffffff", fontSize=11, fontWeight="bold"
        ).encode(text=alt.Text("Rotulo:N")),
    ).properties(height=230)
    if st.session_state.show_completion_by_uf:
        st.altair_chart(
            style_dashboard_chart(percentage_chart), use_container_width=True
        )
elif st.session_state.show_completion_by_uf:
    st.info(
        "Mapeie uma UF, Data Instalação e Data planejada instalação para exibir "
        "o percentual de conclusão por UF."
    )

st.markdown('<div class="section-label">Analítico detalhado</div>', unsafe_allow_html=True)
with st.container(key="analytics_controls"):
    toggle_column, data_column, download_column = st.columns(
        [1, 1, 1], vertical_alignment="center"
    )
    with toggle_column:
        if st.button(
            "▣  Fixar painel analítico flutuante"
            if not st.session_state.floating_analytics
            else "×  Fechar painel analítico flutuante",
            key="toggle_floating_analytics",
            width="stretch",
        ):
            st.session_state.floating_analytics = not st.session_state.floating_analytics
    with data_column:
        if st.button(
            "Ocultar dados importados"
            if st.session_state.show_imported_data
            else "Mostrar dados importados",
            key="toggle_imported_data",
            width="stretch",
        ):
            st.session_state.show_imported_data = not st.session_state.show_imported_data
    with download_column:
        st.download_button(
            "Baixar análise filtrada (CSV)",
            data=display_filtered.to_csv(index=False).encode("utf-8-sig"),
            file_name="analise_baterias_filtrada.csv",
            mime="text/csv",
            width="stretch",
        )

if st.session_state.floating_analytics:
    st.markdown(
        f"""
        <div class="floating-analytics">
          <strong>Analítico · seleção atual</strong>
          <span>🟢 Instaladas: {format_number(installed_total)} {installed_unit_label}</span>
          <span>🟠 Não instaladas: {format_number(pending_total)} {pending_unit_label}</span>
          <span>📋 Registros analisados: {len(filtered):,}</span>
          <span>📍 UFs: {filtered[uf_column].nunique() if uf_column else "—"}</span>
        </div>
        """.replace(",", "."),
        unsafe_allow_html=True,
    )
if st.session_state.show_imported_data:
    st.dataframe(display_filtered, use_container_width=True, hide_index=True)
