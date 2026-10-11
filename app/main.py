"""
Aplicação Web Interativa - BioCiclo IA
Sistema Inteligente para Classificação e Destinação de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) - Departamento de Computação
Disciplina: Fundamentos da Inteligência Artificial
"""

import sys
from pathlib import Path
from PIL import Image
import streamlit as st

# Garantir que a raiz do projeto esteja no PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.models.detector import WasteDetector
from src.rules.destination import RULES_DATABASE
from app.components.ui_helpers import inject_styles, render_advice_card

# Configuração da página do Streamlit
st.set_page_config(
    page_title="BioCiclo IA | Classificação de Resíduos",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

@st.cache_resource(show_spinner="Carregando modelo de Inteligência Artificial...")
def load_detector():
    """Carrega o detector YOLO em cache para inicialização rápida."""
    return WasteDetector()

detector = load_detector()

# ==============================================================================
# BARRA LATERAL (CONFIGURAÇÕES E CONTEXTO)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🌿 BioCiclo IA")
    st.caption("Apoio ao programa **BioCiclo Urbano** (Aracaju/EMSURB)")
    st.markdown("---")

    st.subheader("⚙️ Parâmetros do Modelo")
    conf_thresh = st.slider(
        "Limiar de Confiança (Threshold)",
        min_value=0.05,
        max_value=0.95,
        value=0.25,
        step=0.05,
        help="Detecções com probabilidade inferior a este valor serão alertadas como incertas para solicitar nova foto.",
    )

    st.markdown("---")
    st.subheader("🤖 Status do Modelo")
    if detector.is_custom_model:
        st.success(f"Modelo treinado: **{detector.model_name}**")
    else:
        st.warning("⚠️ **Modo Demonstração (COCO Pré-treinado)**")
        st.caption(
            "O modelo atual ainda é o genérico. Para reconhecer com alta precisão as 6 classes de resíduos "
            "do BioCiclo, treine o modelo com o dataset baixado!"
        )

    st.markdown("---")
    st.markdown(
        """
        **Desenvolvido para:**  
        🎓 UFS - Dep. de Computação  
        📚 Fundamentos da Inteligência Artificial  
        📍 São Cristóvão / Aracaju - SE
        """
    )


# ==============================================================================
# CABEÇALHO PRINCIPAL
# ==============================================================================
st.markdown('<h1 class="main-title">♻️ BioCiclo IA: Triagem Inteligente de Resíduos</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Identificação automática de materiais por visão computacional e direcionamento para '
    '<strong>Compostagem (BioCiclo Urbano)</strong> ou <strong>Coleta Seletiva</strong>.</p>',
    unsafe_allow_html=True,
)

tab_pred, tab_rules, tab_about = st.tabs([
    "📸 Classificação & Destinação",
    "📋 Tabela de Regras (BioCiclo Urbano)",
    "ℹ️ Sobre o Projeto & Metodologia",
])

# ==============================================================================
# ABA 1: CLASSIFICAÇÃO & PREDIÇÃO
# ==============================================================================
with tab_pred:
    st.markdown("### Envie uma fotografia do resíduo")
    
    input_method = st.radio(
        "Escolha a forma de captura:",
        ["📁 Upload de Imagem", "📷 Câmera (Webcam)", "🧪 Amostras de Teste"],
        horizontal=True,
    )

    image_to_process = None

    if input_method == "📁 Upload de Imagem":
        uploaded_file = st.file_uploader(
            "Selecione uma imagem (JPG, JPEG, PNG):",
            type=["jpg", "jpeg", "png"],
            help="Tire uma foto clara do resíduo principal sobre fundo neutro ou superfície limpa.",
        )
        if uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)

    elif input_method == "📷 Câmera (Webcam)":
        camera_file = st.camera_input("Fotografe o resíduo para análise:")
        if camera_file is not None:
            image_to_process = Image.open(camera_file)

    elif input_method == "🧪 Amostras de Teste":
        samples_dir = ROOT_DIR / "data" / "samples"
        sample_files = (
            list(samples_dir.glob("*.jpg"))
            + list(samples_dir.glob("*.png"))
            + list(samples_dir.glob("*.bmp"))
        )
        if sample_files:
            selected_sample_name = st.selectbox(
                "Selecione uma amostra para teste imediato:",
                [f.name for f in sample_files],
            )
            selected_path = samples_dir / selected_sample_name
            image_to_process = Image.open(selected_path)
        else:
            st.info("Nenhuma imagem encontrada em data/samples/. Adicione imagens de teste na pasta para visualizá-las aqui.")

    # Processamento e inferência
    if image_to_process is not None:
        st.markdown("---")
        with st.spinner("Processando imagem e executando modelo YOLO..."):
            all_dets, primary_det = detector.predict(image_to_process, conf_threshold=conf_thresh)

        col_img, col_info = st.columns([1, 1], gap="medium")

        with col_img:
            st.markdown("#### Imagem Analisada")
            if all_dets:
                annotated_img = detector.annotate_image(image_to_process, all_dets)
                st.image(annotated_img, use_container_width=True, caption=f"{len(all_dets)} objeto(s) detectado(s)")
            else:
                st.image(image_to_process, use_container_width=True, caption="Imagem original")

        with col_info:
            st.markdown("#### Resultado da Classificação")
            if primary_det is not None:
                render_advice_card(primary_det.advice, primary_det.confidence)
                
                # Se houver múltiplos objetos detectados
                if len(all_dets) > 1:
                    with st.expander(f"📦 Outros resíduos identificados ({len(all_dets) - 1})"):
                        for idx, det in enumerate(all_dets[1:], start=2):
                            st.write(
                                f"**#{idx} - {det.advice.display_name}**: "
                                f"Confiança: {det.confidence * 100:.1f}% | Destino: *{det.advice.destination}*"
                            )
            else:
                st.warning(
                    "⚠️ Nenhum resíduo foi identificado com confiança suficiente no limiar atual.\n\n"
                    "**Orientações:**\n"
                    "- Aproxime a câmera do objeto principal.\n"
                    "- Garanta uma iluminação adequada e evite sombras fortes.\n"
                    "- Você também pode diminuir ligeiramente o Limiar de Confiança na barra lateral."
                )

# ==============================================================================
# ABA 2: TABELA DE REGRAS E DESTINAÇÃO
# ==============================================================================
with tab_rules:
    st.markdown("### Diretrizes Oficiais de Destinação (BioCiclo Urbano & Coleta)")
    st.markdown(
        "A tabela a seguir reflete a metodologia aprovada para o projeto, correlacionando "
        "cada classe de material detectado ao seu grupo de resíduos e destinação prioritária:"
    )

    table_data = []
    for key, val in RULES_DATABASE.items():
        if key == "ORGANIC":  # evitar duplicata visual de display
            continue
        table_data.append({
            "Categoria Reconhecida": val["display_name"],
            "Classificação Geral": val["waste_type"],
            "Sugestão de Destinação": val["destination"],
        })

    st.table(table_data)

    st.markdown(
        """
        > 💡 **Nota sobre Resíduos Orgânicos:**  
        > A categoria **Orgânico / Biodegradável** é destinada ao **BioCiclo Urbano**, permitindo que restos de alimentos, 
        > cascas e hortifrutis de feiras e cozinhas se transformem em adubo orgânico de alta qualidade, 
        > fortalecendo a agricultura urbana e aliviando a sobrecarga dos aterros sanitários.
        """
    )

# ==============================================================================
# ABA 3: SOBRE O PROJETO & METODOLOGIA
# ==============================================================================
with tab_about:
    st.markdown(
        """
        ### 📖 Contextualização do Projeto
        Este projeto surge a partir do **BioCiclo Urbano**, iniciativa de compostagem promovida pela 
        **Prefeitura de Aracaju** e desenvolvida em articulação com a **Empresa Municipal de Serviços Urbanos (EMSURB)**. 
        A iniciativa busca ampliar o aproveitamento de resíduos orgânicos provenientes de mercados, feiras e outros 
        estabelecimentos, direcionando-os para processos de compostagem.

        Nesse contexto, este sistema atua como uma camada de apoio inteligente à identificação e à separação dos resíduos, 
        contribuindo para as etapas iniciais de sua triagem.

        ---

        ### 🧠 Abordagem Técnica e Inteligência Artificial
        - **Modelo Previsto:** Rede neural convolucional **YOLO (You Only Look Once)** da Ultralytics (variante *nano* para inferência leve e eficiente).
        - **Técnica:** Aprendizado Supervisionado por Transferência (*Transfer Learning / Fine-Tuning*).
        - **Dataset Principal:** *Garbage Classification 3 (GC1)* do Roboflow Universe (10.464 imagens anotadas em formato YOLO) e *TrashNet*.
        - **Métricas de Avaliação:** Precisão, Recall, mAP@50, mAP@50:95 e Matriz de Confusão.

        ---

        ### 👥 Equipe e Instituição
        - **Instituição:** Universidade Federal de Sergipe (UFS)
        - **Departamento:** Departamento de Computação (DComp) - São Cristóvão/SE
        - **Disciplina:** Fundamentos da Inteligência Artificial
        - **Ano de Execução:** 2026
        """
    )
