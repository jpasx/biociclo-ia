"""
Componentes Visuais Minimalistas — BioCiclo IA
Design limpo, direto ao ponto e focado na experiência de uso.
"""

import streamlit as st
from src.rules.destination import DestinationAdvice


def render_html(raw_html: str) -> None:
    """Remove indentação por linha para evitar que o Markdown crie blocos de código."""
    clean_html = "\n".join(line.strip() for line in raw_html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 2.2rem;
    padding-bottom: 3rem;
    max-width: 1020px;
}

/* Cabeçalho Minimalista */
.min-header {
    margin-bottom: 1.75rem;
    padding-bottom: 1.1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.min-tag {
    font-size: 0.75rem;
    font-weight: 600;
    color: #10B981;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.3rem;
}

.min-title {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F9FAFB;
    margin: 0 0 0.3rem 0;
    letter-spacing: -0.02em;
}

.min-sub {
    font-size: 0.95rem;
    color: #9CA3AF;
    margin: 0;
}

/* Card de Resultado Limpo */
.result-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 1.5rem;
}

.result-top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.75rem;
}

.result-material {
    font-size: 1.5rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0;
}

.result-conf {
    font-size: 1.1rem;
    font-weight: 600;
    color: #10B981;
}

.result-bar-bg {
    width: 100%;
    height: 6px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 99px;
    overflow: hidden;
    margin-bottom: 1.2rem;
}

.result-bar-fill {
    height: 100%;
    border-radius: 99px;
}

.dest-box {
    background: rgba(16, 185, 129, 0.08);
    border-left: 3px solid #10B981;
    border-radius: 6px;
    padding: 0.85rem 1rem;
    margin-bottom: 1rem;
}

.dest-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9CA3AF;
    margin-bottom: 0.15rem;
}

.dest-value {
    font-size: 1.02rem;
    font-weight: 600;
    color: #F9FAFB;
}

.guide-text {
    font-size: 0.9rem;
    color: #D1D5DB;
    line-height: 1.55;
    margin: 0 0 0.9rem 0;
}

.tips-list {
    margin: 0;
    padding-left: 1.1rem;
    font-size: 0.85rem;
    color: #9CA3AF;
    line-height: 1.55;
}

.tips-list li {
    margin-bottom: 0.25rem;
}

.empty-placeholder {
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 2.5rem 1.5rem;
    text-align: center;
    color: #9CA3AF;
    font-size: 0.92rem;
}

/* Seções Explicativas Inferiores */
.section-divider {
    margin-top: 2.75rem;
    margin-bottom: 1.25rem;
    padding-top: 1.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.sec-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #F9FAFB;
    margin: 0 0 0.4rem 0;
}

.sec-desc {
    font-size: 0.92rem;
    color: #9CA3AF;
    line-height: 1.6;
    margin: 0 0 1.25rem 0;
}

.simple-card {
    background: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
    padding: 1.15rem 1.25rem;
    height: 100%;
}

.simple-card h4 {
    font-size: 0.96rem;
    font-weight: 600;
    color: #F9FAFB;
    margin: 0 0 0.4rem 0;
}

.simple-card p {
    font-size: 0.86rem;
    color: #9CA3AF;
    line-height: 1.55;
    margin: 0;
}
</style>
"""


def inject_styles():
    render_html(CUSTOM_CSS)


def render_header():
    render_html(
        """
        <div class="min-header">
            <div class="min-tag">UFS &bull; DComp &bull; BioCiclo Urbano (Aracaju)</div>
            <h1 class="min-title">BioCiclo IA</h1>
            <p class="min-sub">Classificação inteligente de resíduos por imagem para apoio à compostagem e coleta seletiva.</p>
        </div>
        """
    )


def render_empty_state():
    render_html(
        """
        <div class="empty-placeholder">
            Selecione ou envie uma imagem ao lado para ver a classificação e onde descartar.
        </div>
        """
    )


def render_no_detection_state(threshold: float):
    render_html(
        f"""
        <div class="empty-placeholder" style="border-color: rgba(245, 158, 11, 0.4); color: #FCD34D;">
            Nenhum resíduo identificado com confiança acima de <strong>{threshold * 100:.0f}%</strong>.<br>
            <span style="font-size: 0.84rem; color: #9CA3AF;">Tente centralizar melhor o objeto ou reduza o limiar de confiança nos ajustes.</span>
        </div>
        """
    )


def render_advice_card(advice: DestinationAdvice, confidence: float):
    conf_pct = confidence * 100
    bar_color = "#10B981" if not advice.is_uncertain else "#F59E0B"
    clamped = min(max(conf_pct, 4.0), 100.0)

    warning_html = ""
    if advice.is_uncertain:
        warning_html = (
            '<div style="font-size: 0.8rem; color: #FBBF24; margin-bottom: 0.85rem;">'
            '⚠️ Confiança moderada/baixa — recomenda-se confirmar visualmente ou tirar outra foto com melhor iluminação.'
            '</div>'
        )

    tips_items = "".join(f"<li>{t}</li>" for t in advice.tips[:2])

    render_html(
        f"""
        <div class="result-card">
            <div class="result-top">
                <h3 class="result-material">{advice.display_name}</h3>
                <span class="result-conf" style="color: {bar_color};">{conf_pct:.0f}% de confiança</span>
            </div>
            <div class="result-bar-bg">
                <div class="result-bar-fill" style="width: {clamped:.1f}%; background: {bar_color};"></div>
            </div>
            {warning_html}
            <div class="dest-box" style="border-left-color: {advice.action_color};">
                <div class="dest-label">Destinação Recomendada ({advice.waste_type})</div>
                <div class="dest-value">{advice.destination} &bull; {advice.conama_bin}</div>
            </div>
            <p class="guide-text">{advice.guidance}</p>
            <ul class="tips-list">{tips_items}</ul>
        </div>
        """
    )
