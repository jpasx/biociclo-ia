"""
Aplicação Web Interativa - BioCiclo IA
Sistema Inteligente para Classificação e Destinação de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) - Departamento de Computação
Disciplina: Fundamentos da Inteligência Artificial
"""

import sys
from pathlib import Path
from PIL import Image, ImageOps
import streamlit as st

# Garantir que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models.detector import WasteDetector
from src.rules.destination import RULES_DATABASE
from app.components.ui_helpers import (
    inject_styles,
    render_header,
    render_empty_state,
    render_no_detection_state,
    render_advice_card,
)

# Configuração da página do Streamlit
st.set_page_config(
    page_title="BioCiclo IA | Sistema de Triagem de Resíduos",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()


@st.cache_resource(show_spinner="Inicializando motor de inferência...")
def get_cached_detector():
    """Carrega e mantém o detector YOLO em cache de recursos."""
    return WasteDetector()


detector = get_cached_detector()

# Se o detector em cache não for o modelo customizado, tenta recriar
if not detector.is_custom_model:
    fresh_det = WasteDetector()
    if fresh_det.is_custom_model:
        detector = fresh_det
        st.cache_resource.clear()


# Mapeamento descritivo para o catálogo de amostras
SAMPLE_DESCRIPTIONS = {
    "exemplo_plastic.jpg": "Amostra 01 — Plástico (Garrafa PET)",
    "exemplo_paper.jpg": "Amostra 02 — Papel (Descartáveis / Celulose)",
    "exemplo_metal.jpg": "Amostra 03 — Metal (Lata de Alumínio)",
    "exemplo_glass.jpg": "Amostra 04 — Vidro (Recipiente Transparente)",
    "exemplo_cardboard.jpg": "Amostra 05 — Papelão (Caixa / Embalagem)",
    "exemplo_biodegradable.jpg": "Amostra 06 — Orgânico / Biodegradável (Hortifruti)",
    "amostra_organico_maca.bmp": "Amostra 07 — Orgânico (Resíduo de Fruta)",
    "amostra_plastico_garrafa.bmp": "Amostra 08 — Plástico (Embalagem Rígida)",
    "amostra_papelao_caixa.bmp": "Amostra 09 — Papelão (Estrutura Secundária)",
}


# ==============================================================================
# BARRA LATERAL (PAINEL DE CONTROLE E PARÂMETROS)
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <div class="header-kicker" style="margin-bottom: 0.2rem;">Sistema de Triagem</div>
            <div style="font-size: 1.3rem; font-weight: 700; color: #F0F6FC; letter-spacing: -0.01em;">BioCiclo IA</div>
            <div style="font-size: 0.8rem; color: #8B949E; margin-top: 0.15rem;">
                Apoio técnico ao programa BioCiclo Urbano (Aracaju / EMSURB)
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-label">Motor de Inferência</div>', unsafe_allow_html=True)
    if detector.is_custom_model:
        st.markdown(
            f"""
            <div class="sidebar-status-card">
                <div class="status-row">
                    <span class="status-dot dot-online"></span>
                    <span class="status-label">Modelo Operacional Ativo</span>
                </div>
                <p class="status-sub">Pesos: {detector.model_name}</p>
                <p class="status-sub" style="margin-top: 0.25rem;">
                    Classes: Orgânico, Papelão, Vidro, Metal, Papel e Plástico
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        err_detail = getattr(detector, "load_error", None) or "Pesos customizados não carregados."
        st.markdown(
            f"""
            <div class="sidebar-status-card">
                <div class="status-row">
                    <span class="status-dot dot-fallback"></span>
                    <span class="status-label">Modo de Contingência (COCO)</span>
                </div>
                <p class="status-sub">{err_detail}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Recarregar Pesos do Modelo (best.pt)", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    st.markdown("---")
    st.markdown('<div class="section-label">Parâmetros de Detecção</div>', unsafe_allow_html=True)
    conf_thresh = st.slider(
        "Limiar de Confiança (Threshold)",
        min_value=0.05,
        max_value=0.95,
        value=0.15,
        step=0.05,
        help="Define a probabilidade mínima exigida para validar uma detecção. Valores abaixo deste limiar acionam recomendação de revisão.",
    )
    st.caption(
        f"Limiar atual configurado em {conf_thresh * 100:.0f}%. Detecções abaixo de 50% exibem alerta preventivo de segurança."
    )

    st.markdown("---")
    st.markdown('<div class="section-label">Informações Institucionais</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sidebar-status-card" style="margin-bottom: 0;">
            <p class="status-sub" style="color: #C9D1D9; font-weight: 600; margin-bottom: 0.2rem;">
                Universidade Federal de Sergipe (UFS)
            </p>
            <p class="status-sub">Departamento de Computação (DComp)</p>
            <p class="status-sub">Disciplina: Fundamentos da Inteligência Artificial</p>
            <p class="status-sub" style="margin-top: 0.35rem; color: #6E7681;">São Cristóvão / Aracaju &mdash; SE</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# CABEÇALHO E NAVEGAÇÃO PRINCIPAL
# ==============================================================================
render_header()

tab_pred, tab_rules, tab_about = st.tabs([
    "Classificação e Triagem",
    "Matriz de Diretrizes (BioCiclo Urbano)",
    "Arquitetura e Escopo do Projeto",
])

# ==============================================================================
# ABA 1: CLASSIFICAÇÃO E TRIAGEM
# ==============================================================================
with tab_pred:
    col_input, col_output = st.columns([1, 1.15], gap="large")

    image_to_process = None

    with col_input:
        st.markdown('<div class="section-heading">1. Fonte de Imagem e Inspeção</div>', unsafe_allow_html=True)

        input_method = st.radio(
            "Selecione o método de entrada:",
            ["Upload de Arquivo", "Captura por Câmera", "Catálogo de Amostras"],
            horizontal=True,
        )

        if input_method == "Upload de Arquivo":
            uploaded_file = st.file_uploader(
                "Envie uma imagem do resíduo (formatos suportados: JPG, JPEG, PNG):",
                type=["jpg", "jpeg", "png"],
                help="Fotografe o resíduo de forma centralizada e sob iluminação uniforme.",
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
            # Ordenar priorizando os exemplos principais do dataset
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
                selected_path = file_map[selected_label]
                image_to_process = Image.open(selected_path)
            else:
                st.info("Nenhuma imagem de amostra encontrada no diretório data/samples/.")

    # Execução da inferência quando há imagem selecionada
    all_dets = []
    primary_det = None

    if image_to_process is not None:
        try:
            image_to_process = ImageOps.exif_transpose(image_to_process)
        except Exception:
            pass

        with st.spinner("Executando inferência por visão computacional..."):
            all_dets, primary_det = detector.predict(image_to_process, conf_threshold=conf_thresh)

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

            # Detecções adicionais na mesma imagem
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
# ABA 2: MATRIZ DE DIRETRIZES E DESTINAÇÃO
# ==============================================================================
with tab_rules:
    st.markdown('<div class="section-heading">Matriz Oficial de Classificação e Destinação de Resíduos</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle" style="margin-bottom: 1.25rem;">'
        'Correlação técnica entre as classes materiais identificadas pelo modelo de visão computacional, '
        'seu enquadramento ambiental e a recomendação prioritária de manejo.'
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
            "Destinação Prioritária": val["destination"],
            "Diretriz Operacional": val["guidance"],
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="info-card" style="border-left: 4px solid #2EA043; margin-top: 1.25rem;">
            <div class="info-card-title">Integração com o Programa BioCiclo Urbano (Aracaju / EMSURB)</div>
            <p class="info-card-body">
                A categoria <strong>Orgânico / Biodegradável</strong> possui prioridade estratégica dentro do programa 
                <strong>BioCiclo Urbano</strong>. A segregação correta na fonte evita a contaminação cruzada com recicláveis secos, 
                viabilizando a conversão de resíduos de feiras livres, mercados e cozinhas em composto orgânico certificado 
                para aplicação em áreas verdes públicas e agricultura familiar, além de reduzir o passivo ambiental em aterros sanitários.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# ABA 3: ARQUITETURA E ESCOPO DO PROJETO
# ==============================================================================
with tab_about:
    st.markdown('<div class="section-heading">Especificações Técnicas e Contextualização Institucional</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        st.markdown(
            """
            <div class="info-card">
                <div class="section-label">Contexto Operacional</div>
                <div class="info-card-title">Programa BioCiclo Urbano e Gestão de Resíduos</div>
                <p class="info-card-body">
                    Desenvolvido em alinhamento com o programa <strong>BioCiclo Urbano</strong>, iniciativa promovida pela 
                    Prefeitura Municipal de Aracaju em articulação com a <strong>Empresa Municipal de Serviços Urbanos (EMSURB)</strong>. 
                    O projeto propõe uma ferramenta de triagem assistida por inteligência artificial capaz de apoiar operadores, 
                    cidadãos e pontos de entrega na correta separação entre frações orgânicas compostáveis e materiais recicláveis secos.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <div class="section-label">Governança e Segurança de Decisão</div>
                <div class="info-card-title">Controle de Incerteza e Limiar de Confiança</div>
                <p class="info-card-body">
                    Para mitigar falsos positivos decorrentes de oclusão, baixa luminosidade ou contaminação visual do resíduo, 
                    o sistema incorpora uma camada de validação pós-inferência. Quando a probabilidade associada à predição 
                    é inferior ao limiar de segurança configurado, a plataforma emite um alerta preventivo orientando a captura 
                    de uma nova imagem sob condições controladas antes do descarte definitivo.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            """
            <div class="info-card">
                <div class="section-label">Engenharia de Machine Learning</div>
                <div class="info-card-title">Arquitetura Neural e Treinamento Supervisionado</div>
                <p class="info-card-body">
                    <strong>Arquitetura Base:</strong> Ultralytics YOLO11n (rede neural convolucional de estágio único otimizada para inferência em tempo real).<br><br>
                    <strong>Método de Aprendizado:</strong> Transfer Learning e Fine-Tuning supervisionado em GPU (Google Colab T4) por 30 épocas.<br><br>
                    <strong>Base de Dados:</strong> <em>Garbage Classification 3 (GC1)</em>, composta por 10.464 imagens anotadas com caixas delimitadoras distribuídas em 6 classes operacionais: Biodegradável, Papelão, Vidro, Metal, Papel e Plástico.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="info-card">
                <div class="section-label">Créditos Acadêmicos</div>
                <div class="info-card-title">Universidade Federal de Sergipe (UFS)</div>
                <p class="info-card-body">
                    <strong>Unidade:</strong> Departamento de Computação (DComp)<br>
                    <strong>Componente Curricular:</strong> Fundamentos da Inteligência Artificial<br>
                    <strong>Localidade:</strong> Campus Prof. José Aloísio de Campos &mdash; São Cristóvão / Aracaju, SE<br>
                    <strong>Período:</strong> 2026
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
