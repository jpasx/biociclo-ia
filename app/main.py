"""
Aplicação Web Interativa — BioCiclo IA
Sistema Inteligente para Classificação e Destinação de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) — Departamento de Computação (DComp)
Disciplina: Fundamentos da Inteligência Artificial
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image, ImageOps
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models.detector import WasteDetector
from src.rules.destination import RULES_DATABASE
from src.rules.cultural_analysis import REGIONAL_BRANDS_MATRIX
from app.components.ui_helpers import (
    inject_styles,
    render_hero,
    render_empty_state,
    render_no_detection_state,
    render_advice_card,
)

MODEL_CACHE_VERSION = "v9_six_samples"

SAMPLE_DESCRIPTIONS: Dict[str, str] = {
    "exemplo_plastic.jpg": "Amostra 01 — Plástico (Embalagem Termoformada PET)",
    "exemplo_paper.jpg": "Amostra 02 — Papel (Impresso / Folheto Celulósico)",
    "exemplo_metal.jpg": "Amostra 03 — Metal (Lata de Aço / Folha de Flandres)",
    "exemplo_glass.jpg": "Amostra 04 — Vidro (Garrafa de Vidro Âmbar)",
    "exemplo_cardboard.jpg": "Amostra 05 — Papelão (Caixa de Papelão Ondulado)",
    "exemplo_biodegradable.jpg": "Amostra 06 — Orgânico / Biodegradável (Resíduo de Frutas)",
}


# ==============================================================================
# FUNÇÕES DE CACHE (PERFORMANCE)
# ==============================================================================
@st.cache_resource(show_spinner="Carregando modelo de visão computacional YOLO...")
def get_cached_detector(cache_version: str = MODEL_CACHE_VERSION) -> WasteDetector:
    """Instancia e mantém o detector YOLO em cache de recursos."""
    return WasteDetector()


@st.cache_data
def get_sample_catalog(cache_version: str = MODEL_CACHE_VERSION) -> Dict[str, str]:
    """Retorna o mapeamento ordenado das 6 amostras (1 de cada classe) em data/samples."""
    samples_dir = ROOT_DIR / "data" / "samples"
    catalog: Dict[str, str] = {}
    for fname, label in SAMPLE_DESCRIPTIONS.items():
        fpath = samples_dir / fname
        if fpath.exists():
            catalog[label] = str(fpath)
    return catalog


@st.cache_data
def get_cultural_table_data() -> List[Dict[str, str]]:
    """Retorna os dados formatados da matriz de compatibilidade regional."""
    rows = []
    for item in REGIONAL_BRANDS_MATRIX:
        rows.append({
            "Embalagem / Resíduo Regional": item.name,
            "Marcas Locais (SE/NE)": item.brands_examples,
            "Classe Material Real": item.expected_display,
            "Compatibilidade GC1": f"{item.compatibility_level} ({item.compatibility_score}%)",
            "Comportamento do Modelo Base": item.common_model_prediction,
            "Diretriz Local (Aracaju / EMSURB)": item.local_disposal_rule,
        })
    return rows


@st.cache_data
def get_rules_table_data() -> List[Dict[str, str]]:
    """Retorna a tabela oficial de regras de destinação e coletores CONAMA."""
    rows = []
    for key, val in RULES_DATABASE.items():
        if key == "ORGANIC":
            continue
        rows.append({
            "Categoria Reconhecida": val["display_name"],
            "Grupo de Resíduo": val["waste_type"],
            "Coletor CONAMA": val.get("conama_bin", "Coletor Padrão"),
            "Destinação Prioritária": val["destination"],
            "Diretriz Operacional": val["guidance"],
        })
    return rows


# ==============================================================================
# BARRA LATERAL (CONFIGURAÇÕES E STATUS DO MOTOR)
# ==============================================================================
def render_sidebar(detector: WasteDetector) -> Tuple[float, bool]:
    """Renderiza a barra lateral com status do modelo e parâmetros de inferência."""
    with st.sidebar:
        st.subheader("🌿 BioCiclo IA")
        st.caption("Apoio técnico ao programa BioCiclo Urbano (Aracaju / EMSURB)")

        with st.container(border=True):
            if detector.is_custom_model:
                st.markdown("🟢 **Modelo Operacional Ativo**")
                st.caption(f"Pesos: `{detector.model_name}`")
            else:
                st.markdown("🟡 **Modo de Contingência (COCO)**")
                err_msg = getattr(detector, "load_error", None) or "Pesos customizados não carregados."
                st.caption(err_msg)
                if st.button("Recarregar Modelo (best.pt)", use_container_width=True):
                    st.cache_resource.clear()
                    st.rerun()

        st.subheader("Parâmetros de Detecção")
        conf_thresh = st.slider(
            "Limiar de Confiança",
            min_value=0.05,
            max_value=0.90,
            value=0.18,
            step=0.02,
            help="Probabilidade mínima exigida para validar uma detecção na imagem.",
        )
        calibrate_bias = st.checkbox(
            "Calibração Regional e Anti-Viés",
            value=True,
            help="Ativa o consenso de cena e a adaptação para embalagens flexíveis e sacos plásticos.",
        )
        st.caption(f"Corte atual: **{conf_thresh * 100:.0f}%**. Abaixo de 45% exibe aviso de revisão.")

        st.divider()
        st.caption("**Universidade Federal de Sergipe (UFS)**  \nDepartamento de Computação (DComp)  \nFundamentos da Inteligência Artificial")

    return conf_thresh, calibrate_bias


# ==============================================================================
# ABA 1: DEMONSTRAÇÃO (CLASSIFICAÇÃO E TRIAGEM)
# ==============================================================================
def render_tab_demo(detector: WasteDetector, conf_thresh: float, calibrate_bias: bool) -> None:
    """Renderiza a aba principal de demonstração e diagnóstico por imagem."""
    col_input, col_output = st.columns([1, 1.15], gap="large")
    image_to_process = None

    with col_input:
        with st.container(border=True):
            st.subheader("1. Entrada e Inspeção da Imagem")

            input_method = st.radio(
                "Selecione o método de entrada:",
                ["Catálogo de Amostras", "Upload de Arquivo", "Captura por Câmera"],
                horizontal=True,
                key="input_mode_radio",
            )

            if input_method == "Upload de Arquivo":
                uploaded_file = st.file_uploader(
                    "Envie uma foto do resíduo (JPG, JPEG, PNG):",
                    type=["jpg", "jpeg", "png"],
                )
                if uploaded_file is not None:
                    try:
                        image_to_process = Image.open(uploaded_file)
                    except Exception:
                        st.error("Não foi possível ler o arquivo enviado. Envie uma imagem JPG ou PNG válida.")

            elif input_method == "Captura por Câmera":
                camera_file = st.camera_input("Posicione o resíduo diante da câmera:")
                if camera_file is not None:
                    try:
                        image_to_process = Image.open(camera_file)
                    except Exception:
                        st.error("Erro ao processar a captura da câmera. Tente novamente.")

            elif input_method == "Catálogo de Amostras":
                file_map = get_sample_catalog()
                if file_map:
                    labels = list(file_map.keys())
                    default_idx = min(st.session_state.get("sample_select_idx", 0), len(labels) - 1)
                    selected_label = st.selectbox(
                        "Escolha uma amostra homologada para teste imediato:",
                        labels,
                        index=default_idx,
                    )
                    try:
                        image_to_process = Image.open(file_map[selected_label])
                    except Exception:
                        st.error("Não foi possível abrir a imagem de amostra selecionada.")
                else:
                    st.info("Nenhuma imagem de amostra encontrada em `data/samples/`.")

    all_dets = []
    primary_det = None

    if image_to_process is not None:
        try:
            image_to_process = ImageOps.exif_transpose(image_to_process)
        except Exception:
            pass

        try:
            with st.spinner("Analisando materiais na imagem com YOLO11..."):
                all_dets, primary_det = detector.predict(
                    image_to_process,
                    conf_threshold=conf_thresh,
                    calibrate_bias=calibrate_bias,
                )
        except Exception as err:
            st.error(f"Ocorreu um erro durante a análise da imagem: {err}")

        with col_input:
            with st.container(border=True):
                st.caption("**Visualização da Detecção**")
                if all_dets:
                    annotated_img = detector.annotate_image(image_to_process, all_dets)
                    st.image(
                        annotated_img,
                        use_container_width=True,
                        caption=f"Imagem processada — {len(all_dets)} objeto(s) identificado(s).",
                    )
                else:
                    st.image(
                        image_to_process,
                        use_container_width=True,
                        caption="Imagem original (nenhum objeto acima do limiar configurado).",
                    )

    with col_output:
        st.subheader("2. Diagnóstico e Recomendação de Descarte")

        if image_to_process is None:
            render_empty_state()
        elif primary_det is not None:
            render_advice_card(
                primary_det.advice,
                primary_det.confidence,
                total_objects=len(all_dets),
            )

            if len(all_dets) > 1:
                with st.expander(f"Ver detecções secundárias na mesma imagem ({len(all_dets) - 1})", expanded=False):
                    secondary_rows = [
                        {
                            "Ordem": f"#{idx}",
                            "Material": det.advice.display_name,
                            "Grupo": det.advice.waste_type,
                            "Confiança": f"{det.confidence * 100:.1f}%",
                            "Destinação": det.advice.destination,
                        }
                        for idx, det in enumerate(all_dets[1:], start=2)
                    ]
                    st.dataframe(secondary_rows, use_container_width=True, hide_index=True)
        else:
            render_no_detection_state(conf_thresh)


# ==============================================================================
# ABA 2: SOBRE O PROJETO & QUESTÕES CULTURAIS (SE / NE)
# ==============================================================================
def render_tab_sobre() -> None:
    """Renderiza a aba explicativa sobre o projeto e a análise cultural/regional."""
    st.subheader("Motivação e Alinhamento com o BioCiclo Urbano")
    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        with st.container(border=True):
            st.markdown("#### 🌱 O Programa BioCiclo Urbano (Aracaju / EMSURB)")
            st.write(
                "Inspirado na iniciativa promovida pela Prefeitura de Aracaju em articulação com a **EMSURB**, "
                "o **BioCiclo IA** atua na triagem prévia de resíduos sólidos urbanos. O foco central é segregar "
                "a fração orgânica gerada em feiras livres e mercados municipais para produção de composto orgânico, "
                "evitando sua contaminação por plásticos, vidros e metais."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("#### ♻️ Articulação com a Coleta Seletiva e Cooperativas")
            st.write(
                "Quando o resíduo é identificado como reciclável seco (Plástico, Papel, Papelão, Metal ou Vidro), "
                "o sistema indica o coletor correspondente pelo padrão **CONAMA nº 275/2001** e orienta a higienização "
                "básica para envio aos Pontos de Entrega Voluntária (PEVs) e cooperativas locais (como a **CARE** em Aracaju)."
            )

    st.divider()
    st.subheader("Questões Culturais do Dataset e Marcas da Nossa Região (SE / NE)")
    st.write(
        "O dataset público *Garbage Classification 3 (GC1)* contém 10.464 imagens coletadas nos **EUA, Europa e Ásia**. "
        "Ao avaliar a compatibilidade do modelo com embalagens de marcas consumidas em **Sergipe e no Nordeste**, "
        "mapeamos três eixos de diferença cultural (*Domain Shift*):"
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        with st.container(border=True):
            st.markdown("##### 1. Plásticos Flexíveis Impressos")
            st.write(
                "Pacotes laminados de **flocão de milho/cuscuz e café (Maratá, Nordestino, São Braz)** possuem formato "
                "achatado e alta densidade gráfica. No dataset estrangeiro predominam garrafas rígidas, exigindo "
                "calibração cromática para não confundi-los com *Papel*."
            )
    with c2:
        with st.container(border=True):
            st.markdown("##### 2. Copo 200ml e Cartonados")
            st.write(
                "O **copinho plástico de água mineral de 200ml com lacre de alumínio (Indaiá, Cristal)** é exclusivo "
                "do mercado brasileiro. Já caixas **Longa Vida (Betânia, Natville)** têm formato de papelão, mas "
                "são embalagens multicamadas (papel, polietileno e alumínio)."
            )
    with c3:
        with st.container(border=True):
            st.markdown("##### 3. Biomassa das Feiras de Aracaju")
            st.write(
                "Enquanto o dataset original foca em maçãs e folhas temperadas, nas feiras da EMSURB predominam "
                "**casca de coco verde, macaxeira, coentro, manga e jaca**. A fibra marrom do coco requer atenção "
                "para não ser confundida com *Papelão*."
            )

    st.dataframe(get_cultural_table_data(), use_container_width=True, hide_index=True)


# ==============================================================================
# ABA 3: COMO FUNCIONA (PIPELINE TÉCNICO E REGRAS)
# ==============================================================================
def render_tab_como_funciona() -> None:
    """Renderiza o funcionamento técnico da IA, métricas do modelo e tabela de regras."""
    st.subheader("Indicadores Técnicos do Modelo")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        with st.container(border=True):
            st.metric("Arquitetura Neural", "YOLO11s", delta="Transfer Learning")
    with k2:
        with st.container(border=True):
            st.metric("Base de Treinamento", "10.464 fotos", delta="Garbage Classification 3")
    with k3:
        with st.container(border=True):
            st.metric("Treinamento GPU", "45 Épocas", delta="Dataset Balanceado")
    with k4:
        with st.container(border=True):
            st.metric("Classes Ativas", "6 Materiais", delta="Padrão CONAMA 275")

    st.subheader("Pipeline de Processamento em 4 Etapas")
    s1, s2, s3, s4 = st.columns(4, gap="medium")
    with s1:
        with st.container(border=True):
            st.markdown("**1. Captura e Padronização**")
            st.caption(
                "Corrige a orientação EXIF da fotografia e preserva o espaço de cores RGB nativo para evitar distorções cromáticas."
            )
    with s2:
        with st.container(border=True):
            st.markdown("**2. Detecção Espacial YOLO**")
            st.caption(
                "Localiza múltiplos resíduos na cena com caixas delimitadoras e estima a probabilidade entre as 6 classes materiais."
            )
    with s3:
        with st.container(border=True):
            st.markdown("**3. Consenso e Calibração**")
            st.caption(
                "Aplica supressão de ruído espacial (NMS), consenso de cena e adaptação para embalagens flexíveis regionais."
            )
    with s4:
        with st.container(border=True):
            st.markdown("**4. Regra de Negócio e Alerta**")
            st.caption(
                "Consulta a matriz de destinação CONAMA/BioCiclo e aciona alerta preventivo caso a confiança fique abaixo de 45%."
            )

    st.subheader("Estudo Experimental: Variação de Épocas, Erro (Loss) e Taxa de Aprendizado")
    exp_rows = [
        {
            "Experimento / Épocas": "Exp 01 — 3 Épocas (Baseline Inicial)",
            "Dataset (Balanceamento)": "Desbalanceado (10.464 imgs / ~13k orgânicos)",
            "Learning Rate (lr0 → atual)": "0.00100 (Warmup inicial)",
            "box_loss (Treino)": "1.2908",
            "cls_loss (Treino)": "5.8594",
            "dfl_loss (Treino)": "1.5606",
            "Erro Total (Loss ↓)": "8.7108",
            "Precisão (%)": "38.0%",
            "mAP@50 (%)": "24.5%",
        },
        {
            "Experimento / Épocas": "Exp 02 — 15 Épocas (Intermediário I)",
            "Dataset (Balanceamento)": "Rebalanceado (Subamostragem máx. 2.200/classe)",
            "Learning Rate (lr0 → atual)": "0.00078 (Cosine Decay)",
            "box_loss (Treino)": "1.0558",
            "cls_loss (Treino)": "4.1112",
            "dfl_loss (Treino)": "1.3895",
            "Erro Total (Loss ↓)": "6.5565",
            "Precisão (%)": "53.7%",
            "mAP@50 (%)": "39.1%",
        },
        {
            "Experimento / Épocas": "Exp 03 — 30 Épocas (Intermediário II)",
            "Dataset (Balanceamento)": "Rebalanceado (Subamostragem máx. 2.200/classe)",
            "Learning Rate (lr0 → atual)": "0.00029 (Cosine Decay)",
            "box_loss (Treino)": "0.9317",
            "cls_loss (Treino)": "3.0734",
            "dfl_loss (Treino)": "1.2877",
            "Erro Total (Loss ↓)": "5.2928",
            "Precisão (%)": "57.6%",
            "mAP@50 (%)": "46.0%",
        },
        {
            "Experimento / Épocas": "Exp 04 — 45 Épocas (Modelo Final YOLO11s)",
            "Dataset (Balanceamento)": "Rebalanceado + Filtro de Ruído Espacial",
            "Learning Rate (lr0 → atual)": "0.00001 (Convergência fina)",
            "box_loss (Treino)": "0.8584",
            "cls_loss (Treino)": "2.3060",
            "dfl_loss (Treino)": "1.2411",
            "Erro Total (Loss ↓)": "4.4055",
            "Precisão (%)": "61.5%",
            "mAP@50 (%)": "79.1% (Val. Limpa)",
        },
    ]
    st.dataframe(exp_rows, use_container_width=True, hide_index=True)

    assets_dir = ROOT_DIR / "docs" / "assets"
    comp_chart = assets_dir / "comparativo_epocas_erro.png"
    loss_chart = assets_dir / "training_results.png"
    cm_chart = assets_dir / "confusion_matrix.png"

    if comp_chart.exists():
        with st.container(border=True):
            st.markdown("**Gráfico Comparativo: Queda do Erro Total, Evolução por Épocas e Taxa de Aprendizado**")
            st.image(str(comp_chart), use_container_width=True)

    c_left, c_right = st.columns([1.35, 1], gap="medium")
    with c_left:
        if loss_chart.exists():
            with st.container(border=True):
                st.markdown("**Curvas Completas de Erro (Box, Cls, DFL Loss) e Métricas — 45 Épocas**")
                st.image(str(loss_chart), use_container_width=True)
    with c_right:
        if cm_chart.exists():
            with st.container(border=True):
                st.markdown("**Matriz de Confusão Normalizada (45 Épocas)**")
                st.image(str(cm_chart), use_container_width=True)

    st.subheader("Matriz Oficial de Classificação e Destinação")
    st.dataframe(get_rules_table_data(), use_container_width=True, hide_index=True)


# ==============================================================================
# ABA 4: CONTATO E FICHA INSTITUCIONAL
# ==============================================================================
def render_tab_contato() -> None:
    """Renderiza as informações institucionais, equipe e links do projeto."""
    st.subheader("Ficha Institucional e Equipe Desenvolvedora")
    col_team, col_inst, col_links = st.columns(3, gap="medium")

    with col_team:
        with st.container(border=True):
            st.markdown("#### 👥 Equipe Desenvolvedora")
            st.markdown(
                "- **Anderson Oliveira Rocha**\n"
                "- **Esther Kelre Nogueira Protázio**\n"
                "- **Igor Kawã Ribeiro de Jesus**\n"
                "- **João Paulo Andrade Santos**\n"
                "- **Raíssa Tanazio Santos**\n"
                "- **Ricardo Gomes Miranda**"
            )

    with col_inst:
        with st.container(border=True):
            st.markdown("#### 🏛️ Instituição Acadêmica")
            st.markdown(
                "- **Universidade:** Universidade Federal de Sergipe (UFS)\n"
                "- **Unidade:** Departamento de Computação (DComp)\n"
                "- **Disciplina:** Fundamentos da Inteligência Artificial\n"
                "- **Localização:** Campus Prof. José Aloísio de Campos — São Cristóvão / Aracaju, SE"
            )

    with col_links:
        with st.container(border=True):
            st.markdown("#### 🔗 Recursos e Repositório Oficial")
            st.markdown(
                "- **Código-Fonte (GitHub):** [github.com/jpasx/biociclo-ia](https://github.com/jpasx/biociclo-ia)\n"
                "- **Dataset Base:** [Garbage Classification 3 (Roboflow Universe)](https://universe.roboflow.com/material-identification/garbage-classification-3/dataset/2)\n"
                "- **Referência Local:** Programa BioCiclo Urbano — Prefeitura de Aracaju & EMSURB\n"
                "- **Licença:** MIT License (Código Aberto para Fins Acadêmicos)"
            )


# ==============================================================================
# PONTO DE ENTRADA PRINCIPAL
# ==============================================================================
def main() -> None:
    st.set_page_config(
        page_title="BioCiclo IA | Classificação Inteligente de Resíduos",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()

    if st.session_state.get("_active_model_ver") != MODEL_CACHE_VERSION:
        st.cache_resource.clear()
        st.session_state["_active_model_ver"] = MODEL_CACHE_VERSION

    detector = get_cached_detector(MODEL_CACHE_VERSION)
    conf_thresh, calibrate_bias = render_sidebar(detector)

    render_hero()

    tab_demo, tab_sobre, tab_como_funciona, tab_contato = st.tabs([
        "🎯 Demonstração",
        "🌿 Sobre o Projeto & Análise Regional",
        "⚙️ Como Funciona",
        "📬 Contato e Instituição",
    ])

    with tab_demo:
        render_tab_demo(detector, conf_thresh, calibrate_bias)

    with tab_sobre:
        render_tab_sobre()

    with tab_como_funciona:
        render_tab_como_funciona()

    with tab_contato:
        render_tab_contato()


if __name__ == "__main__":
    main()
