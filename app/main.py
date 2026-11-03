"""
Aplicação Web Interativa - BioCiclo IA
Sistema Inteligente para Classificação, Triagem e Estudo Cultural de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) - Departamento de Computação (DComp)
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
from src.rules.cultural_analysis import (
    CULTURAL_BIAS_AXES,
    REGIONAL_BRANDS_MATRIX,
    get_cultural_summary_metrics,
    evaluate_regional_test_case,
)
from app.components.ui_helpers import (
    inject_styles,
    render_html,
    render_header,
    render_empty_state,
    render_no_detection_state,
    render_scene_composition,
    render_advice_card,
    render_cultural_kpi_strip,
    render_regional_item_card,
)

# Configuração da página do Streamlit
st.set_page_config(
    page_title="BioCiclo IA | Triagem Inteligente e Análise Cultural de Resíduos",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()


@st.cache_resource(show_spinner="Inicializando motor de visão computacional YOLO...")
def get_cached_detector():
    """Carrega e mantém o detector YOLO em cache de recursos."""
    return WasteDetector()


detector = get_cached_detector()

# Garantir que o detector em cache possua a assinatura atualizada (calibrate_bias)
if not detector.is_custom_model or not hasattr(detector, "_analyze_roi_material_cues"):
    fresh_det = WasteDetector()
    detector = fresh_det
    st.cache_resource.clear()


SAMPLE_DESCRIPTIONS = {
    "exemplo_plastic.jpg": "Amostra 01 — Plástico Rígido (Galão HDPE / Dataset GC1)",
    "exemplo_paper.jpg": "Amostra 02 — Papel / Celulose (Descartáveis)",
    "exemplo_metal.jpg": "Amostra 03 — Metal / Alumínio (Marmita Descartável)",
    "exemplo_glass.jpg": "Amostra 04 — Vidro (Garrafa Escura / Gargalo)",
    "exemplo_cardboard.jpg": "Amostra 05 — Papelão Ondulado (Caixa de Transporte)",
    "exemplo_biodegradable.jpg": "Amostra 06 — Orgânico / Biodegradável (Maçãs / Hortifruti)",
    "amostra_organico_maca.bmp": "Amostra 07 — Sintética: Orgânico (Fruta)",
    "amostra_plastico_garrafa.bmp": "Amostra 08 — Sintética: Plástico (Garrafa PET)",
    "amostra_papelao_caixa.bmp": "Amostra 09 — Sintética: Papelão (Caixa)",
}


# ==============================================================================
# BARRA LATERAL (PAINEL DE CONTROLE, CALIBRAÇÃO E PARÂMETROS)
# ==============================================================================
with st.sidebar:
    render_html(
        """
        <div style="margin-bottom: 1.15rem;">
            <div class="header-kicker" style="margin-bottom: 0.35rem;">🌿 BioCiclo Urbano</div>
            <div style="font-size: 1.35rem; font-weight: 800; color: #F0FDF4; letter-spacing: -0.02em;">BioCiclo IA</div>
            <div style="font-size: 0.78rem; color: #9CA3AF; margin-top: 0.15rem;">
                Triagem Inteligente &amp; Adequação Regional (Aracaju / EMSURB)
            </div>
        </div>
        """
    )

    render_html('<div class="section-label">Motor de Inferência</div>')
    if detector.is_custom_model:
        render_html(
            f"""
            <div class="sidebar-status-card">
                <div class="status-row">
                    <span class="status-dot dot-online"></span>
                    <span class="status-label">Modelo Customizado Ativo</span>
                </div>
                <p class="status-sub">Pesos: <strong>{detector.model_name}</strong></p>
                <p class="status-sub" style="margin-top: 0.25rem;">
                    Classes GC1: Orgânico, Papelão, Vidro, Metal, Papel e Plástico
                </p>
            </div>
            """
        )
    else:
        err_detail = getattr(detector, "load_error", None) or "Pesos customizados não carregados."
        render_html(
            f"""
            <div class="sidebar-status-card">
                <div class="status-row">
                    <span class="status-dot dot-fallback"></span>
                    <span class="status-label">Modo de Contingência (COCO)</span>
                </div>
                <p class="status-sub">{err_detail}</p>
            </div>
            """
        )
        if st.button("Recarregar Pesos (best.pt)", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()

    st.markdown("---")
    render_html('<div class="section-label">Calibração e Parâmetros</div>')

    calibrate_bias = st.toggle(
        "Calibração Anti-Viés GC1",
        value=True,
        help=(
            "Mitiga o desbalanceamento da classe BIODEGRADABLE no dataset Garbage Classification 3, "
            "recalibrando probabilidades para evitar que plásticos, metais e papelão sejam classificados "
            "erroneamente como orgânicos."
        ),
    )

    conf_thresh = st.slider(
        "Limiar de Confiança (Threshold)",
        min_value=0.05,
        max_value=0.90,
        value=0.18,
        step=0.02,
        help="Probabilidade mínima exigida para validar uma detecção na imagem.",
    )
    st.caption(
        f"Corte atual: **{conf_thresh * 100:.0f}%**. Predições abaixo de 45% acionam recomendação de verificação."
    )

    st.markdown("---")
    render_html('<div class="section-label">Coletores CONAMA 275/2001</div>')
    render_html(
        """
        <div class="sidebar-status-card" style="padding: 0.75rem 0.9rem;">
            <div style="font-size: 0.76rem; color: #E5E7EB; line-height: 1.75;">
                🟤 <strong>Marrom:</strong> Orgânico / Compostagem<br>
                🔴 <strong>Vermelho:</strong> Plásticos (PET, PP, Sacolas)<br>
                🔵 <strong>Azul:</strong> Papel, Papelão e Tetra Pak<br>
                🟡 <strong>Amarelo:</strong> Metais (Alumínio e Aço)<br>
                🟢 <strong>Verde:</strong> Vidros Recicláveis<br>
                ⚫ <strong>Cinza:</strong> Rejeito Não Reciclável
            </div>
        </div>
        """
    )

    render_html(
        """
        <div class="sidebar-status-card" style="margin-bottom: 0;">
            <p class="status-sub" style="color: #E5E7EB; font-weight: 700; margin-bottom: 0.15rem;">
                Universidade Federal de Sergipe (UFS)
            </p>
            <p class="status-sub">Departamento de Computação (DComp)</p>
            <p class="status-sub">Fundamentos da Inteligência Artificial</p>
            <p class="status-sub" style="margin-top: 0.25rem; color: #6EE7B7;">São Cristóvão / Aracaju &mdash; SE</p>
        </div>
        """
    )


# ==============================================================================
# CABEÇALHO E ABAS PRINCIPAIS
# ==============================================================================
render_header()

tab_pred, tab_cultural, tab_rules, tab_about = st.tabs([
    "🔍 Classificação e Triagem",
    "🌎 Questões Culturais & Marcas Regionais (SE/NE)",
    "♻️ Matriz CONAMA & BioCiclo Urbano",
    "🧠 Arquitetura, Diagnóstico do Treino & Escopo",
])


# ==============================================================================
# ABA 1: CLASSIFICAÇÃO E TRIAGEM POR IMAGEM
# ==============================================================================
with tab_pred:
    col_input, col_output = st.columns([1, 1.15], gap="large")
    image_to_process = None

    with col_input:
        render_html('<div class="section-heading"><span>1. Fonte de Imagem e Inspeção Visual</span></div>')

        input_method = st.radio(
            "Selecione o método de entrada:",
            ["Catálogo de Amostras", "Upload de Arquivo", "Captura por Câmera"],
            horizontal=True,
        )

        if input_method == "Upload de Arquivo":
            uploaded_file = st.file_uploader(
                "Envie uma fotografia do resíduo ou embalagem (JPG, JPEG, PNG):",
                type=["jpg", "jpeg", "png"],
                help="Fotografe o item centralizado e sob boa iluminação.",
            )
            if uploaded_file is not None:
                image_to_process = Image.open(uploaded_file)

        elif input_method == "Captura por Câmera":
            camera_file = st.camera_input("Posicione o resíduo ou embalagem regional diante da câmera:")
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
                    "Escolha uma amostra de referência para testar o modelo imediatamente:",
                    list(file_map.keys()),
                )
                selected_path = file_map[selected_label]
                image_to_process = Image.open(selected_path)
            else:
                st.info("Nenhuma imagem de amostra encontrada em data/samples/.")

    all_dets = []
    primary_det = None

    if image_to_process is not None:
        try:
            image_to_process = ImageOps.exif_transpose(image_to_process)
        except Exception:
            pass

        with st.spinner("Processando imagem com rede neural YOLO e calibrando classes..."):
            all_dets, primary_det = detector.predict(
                image_to_process,
                conf_threshold=conf_thresh,
                calibrate_bias=calibrate_bias,
            )

        with col_input:
            render_html('<div class="section-label" style="margin-top: 0.75rem;">Resultado da Detecção Espacial</div>')
            if all_dets:
                annotated_img = detector.annotate_image(image_to_process, all_dets)
                st.image(
                    annotated_img,
                    use_container_width=True,
                    caption=f"Imagem anotada — {len(all_dets)} objeto(s) relevante(s) identificado(s).",
                )
            else:
                st.image(
                    image_to_process,
                    use_container_width=True,
                    caption="Imagem original submetida (nenhum objeto acima do limiar).",
                )

    with col_output:
        render_html('<div class="section-heading"><span>2. Diagnóstico, Coletor CONAMA e Manejo</span></div>')

        if image_to_process is None:
            render_empty_state()
        elif primary_det is not None:
            render_scene_composition(all_dets)
            render_advice_card(
                primary_det.advice,
                primary_det.confidence,
                calibrated=primary_det.calibrated,
            )

            if len(all_dets) > 1:
                with st.expander(f"Ver Detecções Adicionais na Imagem ({len(all_dets) - 1} item(ns))", expanded=False):
                    secondary_rows = []
                    for idx, det in enumerate(all_dets[1:], start=2):
                        secondary_rows.append({
                            "Ordem": f"#{idx}",
                            "Material": det.advice.display_name,
                            "Grupo": det.advice.waste_type,
                            "Coletor CONAMA": det.advice.conama_bin,
                            "Confiança": f"{det.confidence * 100:.1f}%",
                            "Área (%)": f"{det.area_ratio * 100:.1f}%",
                        })
                    st.dataframe(secondary_rows, use_container_width=True, hide_index=True)
        else:
            render_no_detection_state(conf_thresh)


# ==============================================================================
# ABA 2: QUESTÕES CULTURAIS DO DATASET & MARCAS DA NOSSA REGIÃO (SE / NE)
# ==============================================================================
with tab_cultural:
    render_html(
        """
        <div class="section-heading">
            <span>Análise de Viés Cultural do Dataset (GC1) e Compatibilidade com Marcas Regionais (Sergipe / Nordeste)</span>
        </div>
        <p class="subtitle" style="margin-bottom: 1.25rem;">
            Estudo crítico sobre o fenômeno de <strong>Domain Shift (Deslocamento de Domínio Geográfico e Cultural)</strong>
            ao aplicar um modelo treinado no dataset internacional <em>Garbage Classification 3 (GC1)</em> sobre embalagens de marcas
            comercializadas em Sergipe/Nordeste e resíduos orgânicos das feiras livres de Aracaju.
        </p>
        """
    )

    cultural_metrics = get_cultural_summary_metrics()
    render_cultural_kpi_strip(cultural_metrics)

    # 1. Evidências concretas nas próprias imagens do dataset GC1
    render_html('<div class="section-heading" style="margin-top: 0.5rem;"><span>1. Evidências Visuais de Viés Geográfico nas Amostras do Dataset GC1</span></div>')
    ev_col1, ev_col2, ev_col3 = st.columns(3, gap="medium")

    samples_dir = ROOT_DIR / "data" / "samples"
    with ev_col1:
        p_img = samples_dir / "exemplo_plastic.jpg"
        if p_img.exists():
            st.image(str(p_img), use_container_width=True)
        render_html(
            """
            <div class="info-card">
                <div class="section-label">Amostra GC1 &bull; Classe PLASTIC</div>
                <div class="info-card-title">Galão de Leite Americano (HDPE)</div>
                <p class="info-card-body">
                    No dataset original (EUA/Europa), o plástico é amplamente representado por galões translúcidos HDPE.
                    Em Sergipe e no Nordeste, o leite e derivados populares circulam majoritariamente em <strong>pacotes plásticos flexíveis</strong>
                    ou caixas <strong>Tetra Pak (Betânia, Natville, Camponesa)</strong>, além de fardos impressos de flocão de milho (<strong>Maratá, Nordestino</strong>).
                </p>
            </div>
            """
        )

    with ev_col2:
        m_img = samples_dir / "exemplo_metal.jpg"
        if m_img.exists():
            st.image(str(m_img), use_container_width=True)
        render_html(
            """
            <div class="info-card">
                <div class="section-label">Amostra GC1 &bull; Classe METAL</div>
                <div class="info-card-title">Catálogo Atacadista Asiático (Marca d'Água)</div>
                <p class="info-card-body">
                    Muitas imagens do GC1 são fotos de estúdio com fundo branco puro e marcas d'água de e-commerce estrangeiro (ex: <em>okorder.com</em>).
                    Na triagem real em Aracaju, os resíduos apresentam amassados, rótulos coloridos nacionais, sombras e mistura com outros materiais.
                </p>
            </div>
            """
        )

    with ev_col3:
        b_img = samples_dir / "exemplo_biodegradable.jpg"
        if b_img.exists():
            st.image(str(b_img), use_container_width=True)
        render_html(
            """
            <div class="info-card">
                <div class="section-label">Amostra GC1 &bull; Classe BIODEGRADABLE</div>
                <div class="info-card-title">Maçãs de Clima Temperado (40+ Caixas)</div>
                <p class="info-card-body">
                    Enquanto o dataset estrangeiro foca em maçãs vermelhas e folhas de outono com dezenas de caixas anotadas por foto,
                    a biomassa do <strong>BioCiclo Urbano (EMSURB)</strong> nas feiras de Aracaju é dominada por <strong>coco verde, casca de macaxeira,
                    coentro, jaca, manga e folha de bananeira</strong>.
                </p>
            </div>
            """
        )

    # 2. Os 4 Eixos de Viés Cultural
    render_html('<div class="section-heading" style="margin-top: 1rem;"><span>2. Os 4 Eixos Técnicos de Viés Cultural Identificados</span></div>')
    axis_col_a, axis_col_b = st.columns(2, gap="medium")
    for idx, axis in enumerate(CULTURAL_BIAS_AXES):
        target_col = axis_col_a if idx % 2 == 0 else axis_col_b
        with target_col:
            render_html(
                f"""
                <div class="info-card" style="border-top: 3px solid {axis['color']};">
                    <div class="section-label" style="color: {axis['color']};">{axis['tag']}</div>
                    <div class="info-card-title">{axis['title']}</div>
                    <p class="info-card-body">{axis['description']}</p>
                </div>
                """
            )

    # 3. Matriz de Compatibilidade com Embalagens e Marcas da Nossa Região
    render_html('<div class="section-heading" style="margin-top: 1rem;"><span>3. Matriz de Compatibilidade: Embalagens de Marcas Regionais e Feiras de Aracaju</span></div>')

    filter_col1, filter_col2 = st.columns([1.2, 1], gap="medium")
    with filter_col1:
        selected_compat = st.radio(
            "Filtrar por nível de compatibilidade com o dataset estrangeiro:",
            ["Todos os Itens Regionais (10)", "Baixa (Forte Viés Cultural)", "Média (Ambiguidade Material)", "Alta (Boa Generalização)"],
            horizontal=True,
        )
    with filter_col2:
        search_brand = st.text_input(
            "Buscar por marca ou produto local (ex: Maratá, Betânia, Indaiá, Coco, Cuscuz):",
            placeholder="Digite para filtrar...",
        )

    filtered_items = []
    for item in REGIONAL_BRANDS_MATRIX:
        if "Baixa" in selected_compat and item.compatibility_level != "Baixa":
            continue
        if "Média" in selected_compat and item.compatibility_level != "Média":
            continue
        if "Alta" in selected_compat and item.compatibility_level != "Alta":
            continue
        if search_brand.strip():
            q = search_brand.strip().lower()
            haystack = f"{item.name} {item.brands_examples} {item.category_region} {item.cultural_gap_reason}".lower()
            if q not in haystack:
                continue
        filtered_items.append(item)

    if not filtered_items:
        st.info("Nenhum item regional encontrado para o filtro selecionado.")
    else:
        for item in filtered_items:
            render_regional_item_card(item)

    with st.expander("📊 Visualizar Tabela Sintética Completa (Para Relatório / Apresentação)", expanded=False):
        summary_rows = []
        for item in REGIONAL_BRANDS_MATRIX:
            summary_rows.append({
                "Produto / Resíduo Regional": item.name,
                "Marcas Locais (SE/NE)": item.brands_examples,
                "Classe Correta": item.expected_display,
                "Predição Comum (GC1 Puro)": item.common_model_prediction,
                "Compatibilidade": f"{item.compatibility_level} ({item.compatibility_score}%)",
                "Manejo Local (Aracaju/EMSURB)": item.local_disposal_rule,
            })
        st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    # 4. Laboratório Interativo de Teste Regional ao Vivo
    render_html('<div class="section-heading" style="margin-top: 1.25rem;"><span>4. Laboratório Prático: Testar Foto de Embalagem Regional ao Vivo</span></div>')
    render_html(
        """
        <p class="subtitle" style="margin-bottom: 1rem;">
            Utilize este laboratório durante a apresentação para submeter a foto de uma embalagem de marca regional
            (ex: pacote de flocão/café <em>Maratá</em>, caixa <em>Betânia</em>, copinho <em>Indaiá</em>, garrafa de <em>Cajuína</em> ou <em>Coco Verde</em>)
            e gerar automaticamente o <strong>Laudo de Compatibilidade Cultural</strong> confrontando o gabarito esperado com a predição da IA.
        </p>
        """
    )

    lab_col_left, lab_col_right = st.columns([1, 1.15], gap="large")
    with lab_col_left:
        profile_map = {f"{p.name} ({p.brands_examples})": p for p in REGIONAL_BRANDS_MATRIX}
        selected_profile_label = st.selectbox(
            "1. Qual embalagem/resíduo regional você vai testar?",
            list(profile_map.keys()),
        )
        chosen_profile = profile_map[selected_profile_label]

        lab_file = st.file_uploader(
            "2. Envie uma foto desta embalagem regional (JPG/PNG):",
            type=["jpg", "jpeg", "png"],
            key="cultural_lab_uploader",
        )

    with lab_col_right:
        if lab_file is None:
            render_html(
                f"""
                <div class="info-card" style="border: 1px dashed rgba(16, 185, 129, 0.35);">
                    <div class="section-label">Gabarito Regional Selecionado</div>
                    <div class="info-card-title">{chosen_profile.name}</div>
                    <p class="info-card-body" style="margin-bottom: 0.5rem;">
                        <strong>Marcas de Referência:</strong> {chosen_profile.brands_examples}<br>
                        <strong>Classe Material Esperada:</strong> {chosen_profile.expected_display} (<code>{chosen_profile.expected_class}</code>)<br>
                        <strong>Hipótese de Viés Cultural:</strong> {chosen_profile.cultural_gap_reason}
                    </p>
                    <p class="info-card-body" style="color: #6EE7B7;">
                        👈 Envie uma foto ao lado para executar o teste prático de compatibilidade regional.
                    </p>
                </div>
                """
            )
        else:
            lab_img = Image.open(lab_file)
            try:
                lab_img = ImageOps.exif_transpose(lab_img)
            except Exception:
                pass

            lab_dets, lab_primary = detector.predict(
                lab_img,
                conf_threshold=conf_thresh,
                calibrate_bias=calibrate_bias,
            )
            det_cls = lab_primary.class_name if lab_primary else None
            det_conf = lab_primary.confidence if lab_primary else 0.0
            eval_report = evaluate_regional_test_case(chosen_profile, det_cls, det_conf)

            if lab_dets:
                st.image(detector.annotate_image(lab_img, lab_dets), use_container_width=True)
            else:
                st.image(lab_img, use_container_width=True)

            render_html(
                f"""
                <div class="info-card" style="border-left: 5px solid {eval_report['status_color']};">
                    <div class="section-label" style="color: {eval_report['status_color']};">Laudo Experimental de Compatibilidade Cultural</div>
                    <div class="info-card-title">{eval_report['status']}</div>
                    <p class="info-card-body" style="margin-bottom: 0.5rem;">{eval_report['explanation']}</p>
                    <p class="info-card-body" style="color: #A7F3D0;">
                        <strong>Orientação Correta em Aracaju:</strong> {chosen_profile.local_disposal_rule}
                    </p>
                </div>
                """
            )


# ==============================================================================
# ABA 3: MATRIZ DE DIRETRIZES E DESTINAÇÃO (CONAMA & BIOCICLO URBANO)
# ==============================================================================
with tab_rules:
    render_html('<div class="section-heading"><span>Matriz Oficial de Classificação, Coletores CONAMA e Destinação</span></div>')
    render_html(
        '<p class="subtitle" style="margin-bottom: 1.25rem;">'
        'Correlação técnica entre as classes materiais identificadas pelo modelo de visão computacional, '
        'o código de cores da Resolução CONAMA nº 275/2001 e as diretrizes do programa BioCiclo Urbano (EMSURB).'
        '</p>'
    )

    table_data = []
    for key, val in RULES_DATABASE.items():
        if key == "ORGANIC":
            continue
        table_data.append({
            "Categoria Reconhecida": val["display_name"],
            "Grupo de Resíduo": val["waste_type"],
            "Coletor CONAMA 275": val["conama_bin"],
            "Destinação Prioritária": val["destination"],
            "Exemplos e Contexto Regional (SE)": val.get("regional_note", ""),
        })

    st.dataframe(table_data, use_container_width=True, hide_index=True)

    render_html(
        """
        <div class="info-card" style="border-left: 4px solid #10B981; margin-top: 1.25rem;">
            <div class="info-card-title">Articulação com o Programa BioCiclo Urbano (EMSURB) e Cooperativas de Aracaju (CARE)</div>
            <p class="info-card-body">
                A segregação precisa na fonte sustenta dois pilares ambientais de Aracaju:
                (1) a fração <strong>Orgânica / Biodegradável</strong> coletada em feiras livres e mercados municipais é encaminhada
                para compostagem no <strong>BioCiclo Urbano</strong>, gerando adubo orgânico e reduzindo emissões de metano;
                (2) a fração <strong>Seca Reciclável</strong> (plásticos, metais, vidros, papéis e embalagens cartonadas limpas) é destinada
                aos Pontos de Entrega Voluntária (PEVs) e cooperativas locais como a <strong>CARE (Cooperativa dos Agentes Autônomos de Reciclagem de Aracaju)</strong>.
            </p>
        </div>
        """
    )


# ==============================================================================
# ABA 4: ARQUITETURA, DIAGNÓSTICO DO TREINO E ESCOPO DO PROJETO
# ==============================================================================
with tab_about:
    render_html('<div class="section-heading"><span>Especificações Técnicas, Diagnóstico de Treinamento e Governança</span></div>')

    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        render_html(
            """
            <div class="info-card">
                <div class="section-label">Diagnóstico de Engenharia de Dados</div>
                <div class="info-card-title">Por que o Dataset GC1 Bruto Desbalanceia o Modelo?</div>
                <p class="info-card-body">
                    Na base pública <em>Garbage Classification 3 (GC1)</em>, embora o número de imagens seja distribuído em 6 classes,
                    o número de <strong>instâncias anotadas (bounding boxes)</strong> é severamente assimétrico: uma única fotografia de
                    resíduo orgânico frequentemente contém entre <strong>30 e 50 caixas delimitadoras</strong> (ex: pilhas de maçãs ou folhas),
                    enquanto imagens de plástico, vidro ou metal contêm apenas 1 ou 2 objetos.<br><br>
                    <strong>Solução Implementada no BioCiclo IA:</strong><br>
                    1. <strong>Calibração Pós-Inferência de Prior (No Detector):</strong> Reponderação das probabilidades preditas pelo inverso da densidade de instâncias do GC1 e filtragem de micro-caixas espúrias.<br>
                    2. <strong>Rebalanceamento Automático no Treinamento (Colab/Script):</strong> Limitação de caixas redundantes em fotos superlotadas de <code>BIODEGRADABLE</code> e aumento do ganho de perda de classe (<code>cls=1.5</code>) com <code>cos_lr=True</code>.
                </p>
            </div>
            """
        )

        render_html(
            """
            <div class="info-card">
                <div class="section-label">Governança e Segurança de Decisão</div>
                <div class="info-card-title">Controle de Incerteza e Prevenção de Contaminação</div>
                <p class="info-card-body">
                    Em sistemas de apoio à decisão ambiental, um falso positivo pode contaminar uma leira inteira de compostagem
                    (ex: descartar plástico metalizado como orgânico). Por isso, o sistema incorpora um piso de segurança
                    pós-inferência e um <strong>Alerta de Mistura de Cena</strong> quando objetos orgânicos e recicláveis são detectados
                    simultaneamente na mesma fotografia.
                </p>
            </div>
            """
        )

    with col_b:
        render_html(
            """
            <div class="info-card">
                <div class="section-label">Arquitetura de Visão Computacional</div>
                <div class="info-card-title">Pipeline Neural YOLO11 + Camada Especialista</div>
                <p class="info-card-body">
                    <strong>Detector de Estágio Único:</strong> Ultralytics YOLO11 (CNN com backbone CSPDarknet e cabeçote decoupled para localização e classificação simultâneas).<br><br>
                    <strong>Base de Treinamento:</strong> <em>Garbage Classification 3 (GC1 v2)</em> com 10.464 imagens anotadas.<br><br>
                    <strong>Módulo de Estudo Cultural:</strong> Avaliador de <em>Domain Shift</em> para 10 categorias de embalagens e resíduos típicos de Sergipe e do Nordeste brasileiro.
                </p>
            </div>
            """
        )

        render_html(
            """
            <div class="info-card">
                <div class="section-label">Créditos Acadêmicos</div>
                <div class="info-card-title">Universidade Federal de Sergipe (UFS)</div>
                <p class="info-card-body">
                    <strong>Unidade:</strong> Departamento de Computação (DComp)<br>
                    <strong>Disciplina:</strong> Fundamentos da Inteligência Artificial<br>
                    <strong>Localidade:</strong> Campus Prof. José Aloísio de Campos &mdash; São Cristóvão / Aracaju, SE
                </p>
            </div>
            """
        )
