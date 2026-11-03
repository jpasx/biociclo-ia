"""
Aplicação Web Interativa - BioCiclo IA
Sistema Inteligente para Classificação e Destinação de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) - Departamento de Computação (DComp)
Disciplina: Fundamentos da Inteligência Artificial
"""

import sys
from pathlib import Path
from PIL import Image, ImageOps
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import importlib
import src.rules.destination as _destination_mod
import src.rules.cultural_analysis as _cultural_mod
import src.models.detector as _detector_mod
import app.components.ui_helpers as _ui_helpers

importlib.reload(_destination_mod)
importlib.reload(_cultural_mod)
importlib.reload(_detector_mod)
importlib.reload(_ui_helpers)

from src.models.detector import WasteDetector
from src.rules.destination import RULES_DATABASE
from src.rules.cultural_analysis import REGIONAL_BRANDS_MATRIX
from app.components.ui_helpers import (
    inject_styles,
    render_header,
    render_empty_state,
    render_no_detection_state,
    render_advice_card,
    render_info_card,
)

st.set_page_config(
    page_title="BioCiclo IA | Sistema de Triagem de Resíduos",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()


MODEL_CACHE_VERSION = "v7_rgb_calibrated"

if st.session_state.get("_active_model_ver") != MODEL_CACHE_VERSION:
    st.cache_resource.clear()
    st.session_state["_active_model_ver"] = MODEL_CACHE_VERSION


@st.cache_resource(show_spinner="Inicializando motor de inferência...")
def get_cached_detector(cache_version: str = MODEL_CACHE_VERSION):
    """Carrega e mantém o detector YOLO em cache de recursos."""
    return WasteDetector()


detector = get_cached_detector(MODEL_CACHE_VERSION)

if not detector.is_custom_model:
    fresh_det = WasteDetector()
    if fresh_det.is_custom_model:
        detector = fresh_det
        st.cache_resource.clear()


SAMPLE_DESCRIPTIONS = {
    "exemplo_plastic.jpg": "Amostra 01 — Plástico (Embalagem Rígida HDPE)",
    "exemplo_paper.jpg": "Amostra 02 — Papel (Descartáveis / Celulose)",
    "exemplo_metal.jpg": "Amostra 03 — Metal (Recipiente de Alumínio)",
    "exemplo_glass.jpg": "Amostra 04 — Vidro (Garrafa Escura)",
    "exemplo_cardboard.jpg": "Amostra 05 — Papelão (Caixa Ondulada)",
    "exemplo_biodegradable.jpg": "Amostra 06 — Orgânico / Biodegradável (Hortifruti)",
    "amostra_organico_maca.bmp": "Amostra 07 — Orgânico (Resíduo de Fruta)",
    "amostra_plastico_garrafa.bmp": "Amostra 08 — Plástico (Garrafa PET)",
    "amostra_papelao_caixa.bmp": "Amostra 09 — Papelão (Estrutura Secundária)",
}


# ==============================================================================
# BARRA LATERAL (PAINEL DE CONTROLE E PARÂMETROS)
# ==============================================================================
with st.sidebar:
    sidebar_brand = (
        '<div style="margin-bottom: 1.25rem;">'
        '<div class="header-kicker" style="margin-bottom: 0.2rem;">Sistema de Triagem</div>'
        '<div style="font-size: 1.3rem; font-weight: 700; color: #F0F6FC; letter-spacing: -0.01em;">BioCiclo IA</div>'
        '<div style="font-size: 0.8rem; color: #8B949E; margin-top: 0.15rem;">'
        'Apoio técnico ao programa BioCiclo Urbano (Aracaju / EMSURB)'
        '</div>'
        '</div>'
    )
    st.markdown(sidebar_brand, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Motor de Inferência</div>', unsafe_allow_html=True)
    if detector.is_custom_model:
        status_html = (
            f'<div class="sidebar-status-card">'
            f'<div class="status-row">'
            f'<span class="status-dot dot-online"></span>'
            f'<span class="status-label">Modelo Operacional Ativo</span>'
            f'</div>'
            f'<p class="status-sub">Pesos: {detector.model_name}</p>'
            f'<p class="status-sub" style="margin-top: 0.25rem;">'
            f'Classes: Orgânico, Papelão, Vidro, Metal, Papel e Plástico'
            f'</p>'
            f'</div>'
        )
        st.markdown(status_html, unsafe_allow_html=True)
    else:
        err_detail = getattr(detector, "load_error", None) or "Pesos customizados não carregados."
        fallback_html = (
            f'<div class="sidebar-status-card">'
            f'<div class="status-row">'
            f'<span class="status-dot dot-fallback"></span>'
            f'<span class="status-label">Modo de Contingência (COCO)</span>'
            f'</div>'
            f'<p class="status-sub">{err_detail}</p>'
            f'</div>'
        )
        st.markdown(fallback_html, unsafe_allow_html=True)
        if st.button("Recarregar Pesos do Modelo (best.pt)", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-label">Parâmetros de Detecção</div>', unsafe_allow_html=True)
    conf_thresh = st.slider(
        "Limiar de Confiança (Threshold)",
        min_value=0.05,
        max_value=0.90,
        value=0.18,
        step=0.02,
        help="Probabilidade mínima exigida para validar uma detecção na imagem.",
    )
    calibrate_bias = st.checkbox(
        "Calibração Anti-Viés de Classes (GC1)",
        value=True,
        help="Compensa o desbalanceamento de instâncias da classe BIODEGRADABLE no dataset original.",
    )
    st.caption(
        f"Limiar atual em {conf_thresh * 100:.0f}%. Predições abaixo de 45% exibem alerta preventivo de revisão."
    )

    st.markdown("---")
    st.markdown('<div class="section-label">Informações Institucionais</div>', unsafe_allow_html=True)
    inst_html = (
        '<div class="sidebar-status-card" style="margin-bottom: 0;">'
        '<p class="status-sub" style="color: #C9D1D9; font-weight: 600; margin-bottom: 0.2rem;">'
        'Universidade Federal de Sergipe (UFS)'
        '</p>'
        '<p class="status-sub">Departamento de Computação (DComp)</p>'
        '<p class="status-sub">Disciplina: Fundamentos da Inteligência Artificial</p>'
        '<p class="status-sub" style="margin-top: 0.35rem; color: #6E7681;">São Cristóvão / Aracaju &mdash; SE</p>'
        '</div>'
    )
    st.markdown(inst_html, unsafe_allow_html=True)


# ==============================================================================
# 1. CABEÇALHO E FERRAMENTA DE TRIAGEM (DIRETO AO PONTO NO TOPO)
# ==============================================================================
render_header()

col_input, col_output = st.columns([1, 1.15], gap="large")
image_to_process = None

with col_input:
    st.markdown('<div class="section-heading">1. Fonte de Imagem e Inspeção</div>', unsafe_allow_html=True)

    input_method = st.radio(
        "Selecione o método de entrada:",
        ["Catálogo de Amostras", "Upload de Arquivo", "Captura por Câmera"],
        horizontal=True,
    )

    if input_method == "Upload de Arquivo":
        uploaded_file = st.file_uploader(
            "Envie uma imagem do resíduo (formatos suportados: JPG, JPEG, PNG):",
            type=["jpg", "jpeg", "png"],
        )
        if uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)

    elif input_method == "Captura por Câmera":
        camera_file = st.camera_input("Posicione o resíduo diante da câmera para captura:")
        if camera_file is not None:
            image_to_process = Image.open(camera_file)

    elif input_method == "Catálogo de Amostras":
        samples_dir = ROOT_DIR / "data" / "samples"
        raw_files = (
            list(samples_dir.glob("*.jpg"))
            + list(samples_dir.glob("*.png"))
            + list(samples_dir.glob("*.bmp"))
        )
        sample_files = sorted(
            raw_files,
            key=lambda f: (0 if f.name.startswith("exemplo_") else 1, f.name),
        )
        if sample_files:
            file_map = {
                SAMPLE_DESCRIPTIONS.get(f.name, f.name): f
                for f in sample_files
            }
            selected_label = st.selectbox(
                "Selecione uma amostra homologada para validação imediata:",
                list(file_map.keys()),
            )
            image_to_process = Image.open(file_map[selected_label])
        else:
            st.info("Nenhuma imagem de amostra encontrada em data/samples/.")

all_dets = []
primary_det = None

if image_to_process is not None:
    try:
        image_to_process = ImageOps.exif_transpose(image_to_process)
    except Exception:
        pass

    with st.spinner("Executando inferência por visão computacional..."):
        all_dets, primary_det = detector.predict(
            image_to_process,
            conf_threshold=conf_thresh,
            calibrate_bias=calibrate_bias,
        )

    with col_input:
        st.markdown('<div class="section-label" style="margin-top: 0.75rem;">Visualização da Detecção</div>', unsafe_allow_html=True)
        if all_dets:
            annotated_img = detector.annotate_image(image_to_process, all_dets)
            st.image(
                annotated_img,
                use_container_width=True,
                caption=f"Imagem processada — {len(all_dets)} objeto(s) delimitado(s) pelo modelo.",
            )
        else:
            st.image(
                image_to_process,
                use_container_width=True,
                caption="Imagem original submetida (sem delimitações acima do limiar).",
            )

with col_output:
    st.markdown('<div class="section-heading">2. Diagnóstico e Diretriz de Destinação</div>', unsafe_allow_html=True)

    if image_to_process is None:
        render_empty_state()
    elif primary_det is not None:
        render_advice_card(primary_det.advice, primary_det.confidence)

        if len(all_dets) > 1:
            with st.expander(f"Detecções Secundárias na Mesma Imagem ({len(all_dets) - 1})", expanded=False):
                secondary_rows = []
                for idx, det in enumerate(all_dets[1:], start=2):
                    secondary_rows.append({
                        "Ordem": f"#{idx}",
                        "Material": det.advice.display_name,
                        "Grupo": det.advice.waste_type,
                        "Confiança": f"{det.confidence * 100:.1f}%",
                        "Destinação Recomendada": det.advice.destination,
                    })
                st.dataframe(secondary_rows, use_container_width=True, hide_index=True)
    else:
        render_no_detection_state(conf_thresh)


# ==============================================================================
# 2. DOCUMENTAÇÃO TÉCNICA, VISÃO GERAL E ESTUDO CULTURAL (ABAIXO DA FERRAMENTA)
# ==============================================================================
st.markdown("<div style='margin-top: 2.25rem;'></div>", unsafe_allow_html=True)

tab_overview, tab_cultural, tab_rules = st.tabs([
    "Visão Geral e Arquitetura do Projeto",
    "Questões Culturais do Dataset e Marcas Regionais (SE/NE)",
    "Matriz Oficial de Diretrizes (BioCiclo Urbano)",
])

with tab_overview:
    col_a, col_b = st.columns(2, gap="medium")
    with col_a:
        render_info_card(
            kicker="Contexto Operacional",
            title="Programa BioCiclo Urbano e Gestão de Resíduos em Aracaju",
            body=(
                "Desenvolvido em alinhamento com o programa <strong>BioCiclo Urbano</strong>, iniciativa promovida pela "
                "Prefeitura Municipal de Aracaju em articulação com a <strong>EMSURB</strong>. O projeto propõe uma "
                "ferramenta de triagem assistida por inteligência artificial para apoiar a correta separação entre "
                "frações orgânicas compostáveis (feiras livres e mercados) e materiais recicláveis secos."
            ),
            border_color="#2EA043",
        )
        render_info_card(
            kicker="Governança e Segurança de Decisão",
            title="Controle de Incerteza e Limiar de Confiança",
            body=(
                "Para mitigar falsos positivos decorrentes de oclusão, baixa luminosidade ou reflexos, "
                "o sistema incorpora uma camada de validação pós-inferência. Quando a probabilidade associada "
                "à predição é inferior ao piso de segurança, a plataforma emite um alerta preventivo orientando "
                "a revisão visual ou captura de nova imagem antes do descarte definitivo."
            ),
        )
    with col_b:
        render_info_card(
            kicker="Engenharia de Machine Learning",
            title="Arquitetura Neural YOLO e Calibração Anti-Viés",
            body=(
                "<strong>Arquitetura Base:</strong> Rede neural convolucional Ultralytics YOLO11 com Transfer Learning.<br><br>"
                "<strong>Base de Dados:</strong> <em>Garbage Classification 3 (GC1)</em> com 10.464 imagens distribuídas em 6 classes "
                "(Biodegradável, Papelão, Vidro, Metal, Papel e Plástico), acrescida de camada de calibração de <em>priors</em> "
                "para compensar a alta densidade de anotações da classe orgânica."
            ),
        )
        render_info_card(
            kicker="Créditos Acadêmicos",
            title="Universidade Federal de Sergipe (UFS)",
            body=(
                "<strong>Unidade:</strong> Departamento de Computação (DComp)<br>"
                "<strong>Disciplina:</strong> Fundamentos da Inteligência Artificial<br>"
                "<strong>Localidade:</strong> Campus Prof. José Aloísio de Campos &mdash; São Cristóvão / Aracaju, SE<br>"
                "<strong>Aplicação:</strong> Triagem Inteligente de Resíduos Sólidos Urbanos"
            ),
        )

with tab_cultural:
    st.markdown(
        '<p class="subtitle" style="margin-bottom: 1.15rem;">'
        'Avaliação técnica do fenômeno de <strong>Domain Shift (Viés Cultural e Geográfico)</strong> ao aplicar um modelo '
        'treinado na base internacional <em>Garbage Classification 3</em> (EUA/Europa/Ásia) sobre embalagens de marcas '
        'regionais comercializadas em Sergipe/Nordeste e resíduos orgânicos de feiras livres de Aracaju.'
        '</p>',
        unsafe_allow_html=True,
    )

    c_col1, c_col2, c_col3 = st.columns(3, gap="medium")
    with c_col1:
        render_info_card(
            kicker="Eixo Cultural 01",
            title="Embalagens Plásticas Flexíveis Impressas",
            body=(
                "No Nordeste há forte presença de filmes plásticos flexíveis laminados (BOPP/PEBD), como pacotes de "
                "<strong>flocão de milho/cuscuz e café (Maratá, Nordestino, São Braz)</strong>. Como o dataset estrangeiro "
                "prioriza garrafas rígidas translúcidas, a superfície fosca impressa pode induzir confusão com a classe <em>Papel</em>."
            ),
            border_color="#D29922",
        )
    with c_col2:
        render_info_card(
            kicker="Eixo Cultural 02",
            title="Copos de Água 200ml e Cartonados Tetra Pak",
            body=(
                "O <strong>copinho plástico de água mineral de 200ml com lacre de alumínio (Indaiá, Cristal)</strong> é típico "
                "do mercado regional e ausente em bases norte-americanas. Já caixas <strong>Longa Vida (Betânia, Natville)</strong> "
                "possuem geometria de papelão, mas exigem reciclagem de compósitos multicamadas."
            ),
            border_color="#3B82F6",
        )
    with c_col3:
        render_info_card(
            kicker="Eixo Cultural 03",
            title="Biomassa Tropical de Feiras Livres (EMSURB)",
            body=(
                "Enquanto a classe biodegradável do dataset original concentra frutas de clima temperado (maçãs e peras), "
                "a biomassa do <strong>BioCiclo Urbano em Aracaju</strong> destaca <strong>casca de coco verde, macaxeira, "
                "coentro, manga e jaca</strong>, cuja fibra marrom oxidada requer calibração frente à classe <em>Papelão</em>."
            ),
            border_color="#2EA043",
        )

    cultural_rows = []
    for item in REGIONAL_BRANDS_MATRIX:
        cultural_rows.append({
            "Embalagem / Resíduo Regional": item.name,
            "Marcas / Ocorrência Local (SE/NE)": item.brands_examples,
            "Classe Material Real": item.expected_display,
            "Compatibilidade Nativa GC1": f"{item.compatibility_level} ({item.compatibility_score}%)",
            "Comportamento do Modelo Estrangeiro": item.common_model_prediction,
            "Diretriz Local (Aracaju / EMSURB)": item.local_disposal_rule,
        })
    st.dataframe(cultural_rows, use_container_width=True, hide_index=True)

with tab_rules:
    st.markdown(
        '<p class="subtitle" style="margin-bottom: 1.15rem;">'
        'Correlação técnica entre as categorias materiais reconhecidas pelo modelo, seu enquadramento no padrão '
        'CONAMA nº 275/2001 e a diretriz operacional recomendada.'
        '</p>',
        unsafe_allow_html=True,
    )

    table_data = []
    for key, val in RULES_DATABASE.items():
        if key == "ORGANIC":
            continue
        table_data.append({
            "Categoria Reconhecida": val["display_name"],
            "Grupo de Resíduo": val["waste_type"],
            "Coletor CONAMA": val.get("conama_bin", "Coletor Padrão"),
            "Destinação Prioritária": val["destination"],
            "Diretriz Operacional": val["guidance"],
        })
    st.dataframe(table_data, use_container_width=True, hide_index=True)
