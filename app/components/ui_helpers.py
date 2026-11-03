"""
Componentes Visuais e Estilos Mínimos — BioCiclo IA
Construído com componentes nativos do Streamlit (st.container, st.metric)
e um único bloco enxuto de CSS complementar.
"""

from typing import List, Any
import streamlit as st
from src.rules.destination import DestinationAdvice

MINIMAL_CSS = """
<style>
.block-container {
    padding-top: 2.8rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}
.hero-kicker {
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #10B981;
    margin-bottom: 0.25rem;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #F1F5F9;
    margin: 0 0 0.4rem 0;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 0.98rem;
    color: #94A3B8;
    margin: 0 0 0.5rem 0;
    line-height: 1.55;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 1.25rem;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    padding-bottom: 0.65rem;
}
</style>
"""


def inject_styles() -> None:
    """Injeta o bloco único de CSS mínimo na aplicação."""
    st.markdown(MINIMAL_CSS, unsafe_allow_html=True)


def render_hero() -> None:
    """Renderiza a seção Hero no topo com título, descrição curta, métricas e botão de ação."""
    with st.container(border=True):
        col_text, col_cta = st.columns([2.2, 1], gap="medium", vertical_alignment="center")
        with col_text:
            st.markdown(
                '<div class="hero-kicker">UFS • DComp • Programa BioCiclo Urbano (Aracaju / EMSURB)</div>'
                '<h1 class="hero-title">BioCiclo IA</h1>'
                '<p class="hero-subtitle">'
                'Sistema inteligente de visão computacional para classificação de resíduos por imagem, '
                'apoiando a compostagem orgânica e a coleta seletiva.'
                '</p>',
                unsafe_allow_html=True,
            )
        with col_cta:
            if st.button("🌱 Testar Amostra Agora", type="primary", use_container_width=True):
                st.session_state["input_mode_radio"] = "Catálogo de Amostras"
                st.session_state["sample_select_idx"] = 5  # Amostra Orgânica / Hortifruti
                st.toast("Amostra de demonstração carregada!", icon="✅")


def render_empty_state() -> None:
    """Exibe estado inicial amigável quando nenhuma imagem foi selecionada."""
    with st.container(border=True):
        st.info(
            "👈 **Aguardando imagem para análise:** Selecione uma amostra no catálogo ao lado, "
            "envie uma foto do seu dispositivo ou utilize a câmera para visualizar o diagnóstico."
        )


def render_no_detection_state(threshold: float) -> None:
    """Exibe aviso amigável quando nenhum objeto atinge o limiar mínimo."""
    with st.container(border=True):
        st.warning(
            f"**Nenhum resíduo identificado acima do limiar de {threshold * 100:.0f}%.**\n\n"
            "- Centralize o objeto ocupando a maior parte da foto;\n"
            "- Evite sombras fortes ou reflexos de flash sobre embalagens;\n"
            "- Ou reduza o **Limiar de Confiança** na barra lateral."
        )


def render_advice_card(advice: DestinationAdvice, confidence: float, total_objects: int = 1) -> None:
    """Renderiza o resultado da classificação usando st.container(border=True) e st.metric."""
    conf_pct = confidence * 100
    conama_label = getattr(advice, "conama_bin", "Coletor Padrão")
    regional_note = getattr(advice, "regional_note", "")

    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Material Principal", advice.display_name)
        with m2:
            status_delta = "Confiável" if not advice.is_uncertain else "Revisão sugerida"
            delta_color = "normal" if not advice.is_uncertain else "off"
            st.metric("Grau de Confiança", f"{conf_pct:.1f}%", delta=status_delta, delta_color=delta_color)
        with m3:
            st.metric("Grupo / Itens", advice.waste_type, delta=f"{total_objects} objeto(s) na cena", delta_color="off")

        st.progress(min(max(confidence, 0.02), 1.0))

        if advice.is_uncertain and advice.warning_message:
            st.warning(f"**Atenção (Baixa Confiança):** {advice.warning_message}")

        if "Orgânico" in advice.waste_type:
            st.success(f"**Destinação Recomendada:** {advice.destination}  \n**Coletor CONAMA:** {conama_label}")
        elif "Reciclável" in advice.waste_type:
            st.info(f"**Destinação Recomendada:** {advice.destination}  \n**Coletor CONAMA:** {conama_label}")
        else:
            st.warning(f"**Destinação Recomendada:** {advice.destination}  \n**Coletor CONAMA:** {conama_label}")

        st.markdown(f"**Diretriz Operacional:** {advice.guidance}")

        if regional_note:
            st.caption(f"📍 **Contexto Regional (Sergipe / Nordeste):** {regional_note}")

        st.markdown("**Boas práticas de descarte:**")
        for tip in advice.tips[:3]:
            st.markdown(f"- {tip}")
