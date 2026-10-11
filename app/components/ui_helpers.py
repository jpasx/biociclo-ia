"""
Componentes e Estilos Visuais para o Streamlit
"""

import streamlit as st
from src.rules.destination import DestinationAdvice

CUSTOM_CSS = """
<style>
    /* Estilos gerais */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1b5e20;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.05rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
    .card-result {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 6px solid #2e7d32;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
        margin-right: 0.5rem;
    }
    .badge-organic {
        background-color: #2e7d32;
    }
    .badge-recyclable {
        background-color: #1976d2;
    }
    .badge-trash {
        background-color: #616161;
    }
    .destination-box {
        background: #e8f5e9;
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 0.8rem;
    }
    .warning-box {
        background: #fff8e1;
        border-left: 5px solid #ffb300;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #795548;
    }
    .tip-item {
        margin-bottom: 0.3rem;
        font-size: 0.92rem;
        color: #374151;
    }
</style>
"""

def inject_styles():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

def render_advice_card(advice: DestinationAdvice, confidence: float):
    """
    Renderiza o card principal com o diagnóstico do resíduo e a destinação recomendada.
    """
    # Determinar badge do tipo de resíduo
    if "Orgânico" in advice.waste_type:
        badge_class = "badge-organic"
        icon = "🌱"
    elif "Reciclável" in advice.waste_type:
        badge_class = "badge-recyclable"
        icon = "♻️"
    else:
        badge_class = "badge-trash"
        icon = "🗑️"

    # Se houver incerteza, exibir alerta destacado
    if advice.is_uncertain:
        st.markdown(
            f"""
            <div class="warning-box">
                <h4>⚠️ Detecção com Baixa Certeza</h4>
                <p>{advice.warning_message}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Card Principal
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            f"""
            <div class="card-result" style="border-left-color: {advice.action_color};">
                <span class="badge {badge_class}">{advice.waste_type}</span>
                <span class="badge" style="background-color: {advice.action_color};">{advice.display_name}</span>
                <h3 style="margin-top: 0.8rem; color: #1e293b;">{icon} Destinação Recomendada:</h3>
                <h4 style="color: {advice.action_color}; margin-top: -0.5rem;">{advice.destination}</h4>
                <p style="color: #4b5563; font-size: 0.95rem;">{advice.guidance}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.metric(
            label="Nível de Confiança da IA",
            value=f"{confidence * 100:.1f}%",
            delta="Confiável" if not advice.is_uncertain else "Incerteza",
            delta_color="normal" if not advice.is_uncertain else "inverse",
        )
        st.progress(float(min(max(confidence, 0.0), 1.0)))

    # Dicas de manuseio e descarte correto
    with st.expander("💡 Dicas Práticas de Separação e Manejo", expanded=True):
        for tip in advice.tips:
            st.markdown(f"- {tip}")
