"""
Aplicação Web Minimalista — BioCiclo IA
Classificação e Destinação de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) — DComp
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
    render_html,
    render_header,
    render_empty_state,
    render_no_detection_state,
    render_advice_card,
)

st.set_page_config(
    page_title="BioCiclo IA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_styles()


@st.cache_resource(show_spinner="Carregando modelo de IA...")
def get_cached_detector():
    return WasteDetector()


detector = get_cached_detector()
if not detector.is_custom_model or not hasattr(detector, "_analyze_roi_material_cues"):
    detector = WasteDetector()
    st.cache_resource.clear()

SAMPLE_DESCRIPTIONS = {
    "exemplo_plastic.jpg": "Plástico — Garrafa / Galão",
    "exemplo_paper.jpg": "Papel — Celulose",
    "exemplo_metal.jpg": "Metal — Alumínio",
    "exemplo_glass.jpg": "Vidro — Garrafa",
    "exemplo_cardboard.jpg": "Papelão — Caixa",
    "exemplo_biodegradable.jpg": "Orgânico — Frutas",
}

# ==============================================================================
# 1. CABEÇALHO E FERRAMENTA PRINCIPAL (DIRETO AO PONTO)
# ==============================================================================
render_header()

col_left, col_right = st.columns([1, 1], gap="large")
image_to_process = None

with col_left:
    input_method = st.radio(
        "Fonte da imagem:",
        ["Enviar Foto", "Usar Câmera", "Exemplos Rápidos"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if input_method == "Enviar Foto":
        uploaded = st.file_uploader(
            "Selecione uma foto do resíduo (JPG ou PNG)",
            type=["jpg", "jpeg", "png"],
        )
        if uploaded is not None:
            image_to_process = Image.open(uploaded)

    elif input_method == "Usar Câmera":
        cam = st.camera_input("Tire uma foto do resíduo")
        if cam is not None:
            image_to_process = Image.open(cam)

    elif input_method == "Exemplos Rápidos":
        samples_dir = ROOT_DIR / "data" / "samples"
        sample_files = [
            samples_dir / fname
            for fname in SAMPLE_DESCRIPTIONS
            if (samples_dir / fname).exists()
        ]
        if sample_files:
            file_map = {SAMPLE_DESCRIPTIONS[f.name]: f for f in sample_files}
            chosen = st.selectbox("Escolha um exemplo para testar:", list(file_map.keys()))
            image_to_process = Image.open(file_map[chosen])

    with st.expander("Ajustes de detecção (opcional)", expanded=False):
        conf_thresh = st.slider("Sensibilidade / Confiança mínima", 0.05, 0.85, 0.18, 0.05)
        calibrate_bias = st.checkbox("Calibrar viés de classes do dataset", value=True)

all_dets = []
primary_det = None

if image_to_process is not None:
    try:
        image_to_process = ImageOps.exif_transpose(image_to_process)
    except Exception:
        pass

    all_dets, primary_det = detector.predict(
        image_to_process,
        conf_threshold=conf_thresh,
        calibrate_bias=calibrate_bias,
    )

    with col_left:
        if all_dets:
            st.image(detector.annotate_image(image_to_process, all_dets), use_container_width=True)
        else:
            st.image(image_to_process, use_container_width=True)

with col_right:
    if image_to_process is None:
        render_empty_state()
    elif primary_det is not None:
        render_advice_card(primary_det.advice, primary_det.confidence)
    else:
        render_no_detection_state(conf_thresh)


# ==============================================================================
# 2. EXPLICAÇÃO GERAL DO PROJETO
# ==============================================================================
render_html(
    """
    <div class="section-divider">
        <h2 class="sec-title">Sobre o Projeto BioCiclo IA</h2>
        <p class="sec-desc">
            Desenvolvido na disciplina de <strong>Fundamentos da Inteligência Artificial (DComp / UFS)</strong>,
            o sistema apoia a triagem de resíduos inspirado no programa <strong>BioCiclo Urbano</strong> da Prefeitura de Aracaju (EMSURB).
            Utilizando visão computacional (redes neurais <strong>YOLO11</strong> treinadas na base <em>Garbage Classification 3</em>),
            a ferramenta identifica o material na foto e orienta se ele deve seguir para a <strong>Compostagem Orgânica</strong>
            ou para a <strong>Coleta Seletiva</strong>.
        </p>
    </div>
    """
)

c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    render_html(
        """
        <div class="simple-card">
            <h4>🌱 Foco no BioCiclo Urbano</h4>
            <p>Prioriza a separação correta de restos vegetais e de feiras livres para produção de adubo orgânico em Aracaju, evitando contaminação por plásticos.</p>
        </div>
        """
    )
with c2:
    render_html(
        """
        <div class="simple-card">
            <h4>♻️ Coleta Seletiva &amp; CONAMA</h4>
            <p>Relaciona cada classe identificada (Plástico, Papel, Papelão, Vidro e Metal) ao coletor correto e às boas práticas para cooperativas de reciclagem.</p>
        </div>
        """
    )
with c3:
    render_html(
        """
        <div class="simple-card">
            <h4>🛡️ Controle de Incerteza</h4>
            <p>Quando a iluminação ou o ângulo geram baixa confiança na rede neural, o sistema emite um alerta sugerindo uma nova captura antes do descarte.</p>
        </div>
        """
    )

with st.expander("Ver tabela de regras de destinação por material", expanded=False):
    rules_rows = []
    for key, val in RULES_DATABASE.items():
        if key == "ORGANIC":
            continue
        rules_rows.append({
            "Material": val["display_name"],
            "Grupo": val["waste_type"],
            "Coletor": val["conama_bin"],
            "Destinação": val["destination"],
        })
    st.dataframe(rules_rows, use_container_width=True, hide_index=True)


# ==============================================================================
# 3. QUESTÕES CULTURAIS DO DATASET & COMPATIBILIDADE REGIONAL (SE / NE)
# ==============================================================================
render_html(
    """
    <div class="section-divider">
        <h2 class="sec-title">Questões Culturais do Dataset e Embalagens da Nossa Região</h2>
        <p class="sec-desc">
            O dataset público utilizado no treino (<em>Garbage Classification 3</em>) foi coletado nos <strong>EUA, Europa e Ásia</strong>.
            Ao testar o modelo com produtos consumidos em <strong>Sergipe e no Nordeste</strong>, identificamos três principais diferenças culturais:
        </p>
    </div>
    """
)

k1, k2, k3 = st.columns(3, gap="medium")
with k1:
    render_html(
        """
        <div class="simple-card">
            <h4>1. Embalagens Plásticas Flexíveis</h4>
            <p>No Nordeste são muito comuns pacotes plásticos laminados de <strong>flocão de milho/cuscuz e café (Maratá, Nordestino, São Braz)</strong>. Como o dataset estrangeiro tem mais garrafas rígidas, o rótulo fosco impresso às vezes faz a IA confundir plástico flexível com <em>Papel</em>.</p>
        </div>
        """
    )
with k2:
    render_html(
        """
        <div class="simple-card">
            <h4>2. Copo de Água 200ml e Tetra Pak</h4>
            <p>O <strong>copinho de água mineral com lacre de alumínio (Indaiá, Cristal)</strong> não existe nos datasets americanos. Já caixas de leite <strong>Betânia / Natville (Tetra Pak)</strong> têm formato de papelão, mas misturam papel, plástico e alumínio.</p>
        </div>
        """
    )
with k3:
    render_html(
        """
        <div class="simple-card">
            <h4>3. Orgânicos das Feiras de Aracaju</h4>
            <p>Enquanto o dataset original foca em maçãs e folhas de clima temperado, nas feiras da EMSURB predominam <strong>coco verde, casca de macaxeira, coentro, manga e jaca</strong>. O coco seco marrom pode lembrar a textura de papelão para o modelo puro.</p>
        </div>
        """
    )

st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

regional_table = []
for item in REGIONAL_BRANDS_MATRIX:
    regional_table.append({
        "Item / Embalagem Regional": item.name,
        "Exemplos de Marcas Locais": item.brands_examples,
        "Material Real": item.expected_display,
        "Compatibilidade com Dataset": f"{item.compatibility_level} ({item.compatibility_score}%)",
        "Comportamento da IA": item.common_model_prediction,
    })

st.dataframe(regional_table, use_container_width=True, hide_index=True)
