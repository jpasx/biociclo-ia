"""
Componentes Visuais e Folha de Estilos da Interface Web (BioCiclo IA)
Design institucional, limpo e orientado à clareza de leitura.
"""

import streamlit as st
from src.rules.destination import DestinationAdvice

CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}
.app-header {
    background: linear-gradient(180deg, rgba(22, 27, 34, 0.95) 0%, rgba(13, 17, 23, 0.95) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #2EA043;
    border-radius: 8px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.75rem;
}
.header-kicker {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #3FB950;
    margin-bottom: 0.35rem;
}
.main-title {
    font-size: 1.85rem;
    font-weight: 700;
    color: #F0F6FC;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.subtitle {
    font-size: 0.95rem;
    color: #8B949E;
    margin: 0;
    line-height: 1.5;
}
.section-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #8B949E;
    margin-bottom: 0.5rem;
}
.section-heading {
    font-size: 1.15rem;
    font-weight: 600;
    color: #F0F6FC;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.diagnostic-card {
    background-color: #161B22;
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.diagnostic-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    padding-bottom: 1.1rem;
    margin-bottom: 1.1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}
.material-name {
    font-size: 1.65rem;
    font-weight: 700;
    color: #F0F6FC;
    margin: 0.2rem 0 0 0;
    letter-spacing: -0.01em;
}
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.25rem;
}
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.3rem 0.75rem;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}
.badge-organic {
    background-color: rgba(46, 160, 67, 0.15);
    color: #56D364;
    border: 1px solid rgba(46, 160, 67, 0.4);
}
.badge-recyclable {
    background-color: rgba(31, 111, 235, 0.15);
    color: #58A6FF;
    border: 1px solid rgba(31, 111, 235, 0.4);
}
.badge-trash {
    background-color: rgba(139, 148, 158, 0.15);
    color: #C9D1D9;
    border: 1px solid rgba(139, 148, 158, 0.4);
}
.confidence-box {
    text-align: right;
    min-width: 140px;
}
.confidence-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #F0F6FC;
    line-height: 1.1;
}
.confidence-status {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.conf-high {
    color: #3FB950;
}
.conf-low {
    color: #D29922;
}
.progress-track {
    width: 100%;
    height: 6px;
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 3px;
    overflow: hidden;
    margin: 0.5rem 0 1.25rem 0;
}
.progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
}
.destination-panel {
    background-color: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 3px solid #2EA043;
    border-radius: 6px;
    padding: 1rem 1.15rem;
    margin-bottom: 1.25rem;
}
.destination-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: #F0F6FC;
    margin: 0 0 0.35rem 0;
}
.destination-text {
    font-size: 0.88rem;
    color: #C9D1D9;
    margin: 0;
    line-height: 1.55;
}
.protocol-container {
    background-color: rgba(13, 17, 23, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 1rem 1.15rem;
}
.protocol-title {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #8B949E;
    margin: 0 0 0.65rem 0;
}
.protocol-list {
    margin: 0;
    padding-left: 1.15rem;
    color: #C9D1D9;
    font-size: 0.88rem;
    line-height: 1.6;
}
.protocol-list li {
    margin-bottom: 0.35rem;
}
.uncertainty-alert {
    background-color: rgba(210, 153, 34, 0.1);
    border: 1px solid rgba(210, 153, 34, 0.4);
    border-left: 4px solid #D29922;
    border-radius: 6px;
    padding: 1rem 1.15rem;
    margin-bottom: 1rem;
}
.uncertainty-title {
    font-size: 0.88rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #E3B341;
    margin: 0 0 0.3rem 0;
}
.uncertainty-desc {
    font-size: 0.86rem;
    color: #C9D1D9;
    margin: 0;
    line-height: 1.5;
}
.empty-state-box {
    background-color: #161B22;
    border: 1px dashed rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    padding: 2.5rem 1.75rem;
    text-align: center;
    margin-top: 0.5rem;
}
.empty-state-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #F0F6FC;
    margin: 0 0 0.4rem 0;
}
.empty-state-text {
    font-size: 0.88rem;
    color: #8B949E;
    max-width: 460px;
    margin: 0 auto;
    line-height: 1.55;
}
.sidebar-status-card {
    background-color: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.75rem;
}
.status-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.dot-online {
    background-color: #3FB950;
    box-shadow: 0 0 6px rgba(63, 185, 80, 0.6);
}
.dot-fallback {
    background-color: #D29922;
}
.status-label {
    font-size: 0.82rem;
    font-weight: 600;
    color: #F0F6FC;
}
.status-sub {
    font-size: 0.76rem;
    color: #8B949E;
    margin: 0;
    line-height: 1.4;
}
.info-card {
    background-color: #161B22;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 1.35rem;
    height: 100%;
    margin-bottom: 1rem;
}
.info-card-title {
    font-size: 1rem;
    font-weight: 600;
    color: #F0F6FC;
    margin: 0 0 0.6rem 0;
}
.info-card-body {
    font-size: 0.88rem;
    color: #C9D1D9;
    line-height: 1.6;
    margin: 0;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.stTabs [data-baseweb="tab"] {
    padding-top: 0.6rem;
    padding-bottom: 0.75rem;
    font-weight: 600;
    font-size: 0.92rem;
}
</style>
"""


def inject_styles():
    """Injeta a folha de estilos customizada na página."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header():
    """Renderiza o cabeçalho institucional superior."""
    html = (
        '<div class="app-header">'
        '<div class="header-kicker">Universidade Federal de Sergipe &bull; Departamento de Computação &bull; BioCiclo Urbano</div>'
        '<h1 class="main-title">BioCiclo IA &mdash; Sistema de Classificação e Triagem de Resíduos</h1>'
        '<p class="subtitle">'
        'Plataforma de visão computacional baseada em redes neurais convolucionais (YOLO) para identificação '
        'automatizada de materiais e recomendação técnica de destinação entre Compostagem e Coleta Seletiva.'
        '</p>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state():
    """Renderiza o estado inicial quando nenhuma imagem foi submetida."""
    html = (
        '<div class="empty-state-box">'
        '<h4 class="empty-state-title">Aguardando Imagem para Diagnóstico</h4>'
        '<p class="empty-state-text">'
        'Selecione um arquivo no painel lateral esquerdo, realize uma captura por câmera '
        'ou utilize o catálogo de amostras homologadas para iniciar a inferência e obter o laudo de destinação.'
        '</p>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_no_detection_state(threshold: float):
    """Renderiza aviso técnico quando nenhuma classe atinge o limiar mínimo de confiança."""
    html = (
        f'<div class="uncertainty-alert">'
        f'<div class="uncertainty-title">Nenhum Material Detectado no Limiar Atual ({threshold * 100:.0f}%)</div>'
        f'<p class="uncertainty-desc">'
        f'O modelo não identificou objetos com grau de certeza igual ou superior ao parâmetro configurado.'
        f'</p>'
        f'</div>'
        f'<div class="protocol-container">'
        f'<div class="protocol-title">Recomendações Técnicas de Captura</div>'
        f'<ul class="protocol-list">'
        f'<li>Centralize o resíduo principal ocupando a maior parte do enquadramento.</li>'
        f'<li>Utilize iluminação uniforme e evite sombras acentuadas ou reflexos diretos sobre o material.</li>'
        f'<li>Prefira superfícies ou fundos neutros para destacar os contornos do objeto.</li>'
        f'<li>Se necessário, reduza gradualmente o <strong>Limiar de Confiança</strong> no painel de controle à esquerda.</li>'
        f'</ul>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_advice_card(advice: DestinationAdvice, confidence: float):
    """
    Renderiza o painel de resultado com diagnóstico, nível de confiança,
    destinação prioritária e protocolo técnico de manejo.
    """
    if "Orgânico" in advice.waste_type:
        badge_class = "badge-organic"
    elif "Reciclável" in advice.waste_type:
        badge_class = "badge-recyclable"
    else:
        badge_class = "badge-trash"

    conf_pct = confidence * 100
    conf_status_text = "Confiabilidade Adequada" if not advice.is_uncertain else "Revisão Recomendada"
    conf_status_class = "conf-high" if not advice.is_uncertain else "conf-low"
    bar_color = "#2EA043" if not advice.is_uncertain else "#D29922"
    clamped_width = min(max(conf_pct, 2.0), 100.0)

    if advice.is_uncertain and advice.warning_message:
        alert_html = (
            f'<div class="uncertainty-alert">'
            f'<div class="uncertainty-title">Alerta de Baixa Confiança na Classificação</div>'
            f'<p class="uncertainty-desc">{advice.warning_message}</p>'
            f'</div>'
        )
        st.markdown(alert_html, unsafe_allow_html=True)

    tips_html = "".join(f"<li>{tip}</li>" for tip in advice.tips)

    card_html = (
        f'<div class="diagnostic-card">'
        f'<div class="diagnostic-header">'
        f'<div>'
        f'<div class="section-label">Material Identificado</div>'
        f'<h2 class="material-name">{advice.display_name}</h2>'
        f'</div>'
        f'<div class="confidence-box">'
        f'<div class="section-label">Grau de Confiança</div>'
        f'<div class="confidence-value">{conf_pct:.1f}%</div>'
        f'<div class="confidence-status {conf_status_class}">{conf_status_text}</div>'
        f'</div>'
        f'</div>'
        f'<div class="progress-track">'
        f'<div class="progress-fill" style="width: {clamped_width:.1f}%; background-color: {bar_color};"></div>'
        f'</div>'
        f'<div class="badge-row">'
        f'<span class="badge {badge_class}">Grupo: {advice.waste_type}</span>'
        f'<span class="badge" style="background-color: rgba(255,255,255,0.06); color: #F0F6FC; border: 1px solid {advice.action_color};">'
        f'Destino: {advice.destination}'
        f'</span>'
        f'</div>'
        f'<div class="destination-panel" style="border-left-color: {advice.action_color};">'
        f'<div class="destination-title">Diretriz de Destinação &mdash; {advice.destination}</div>'
        f'<p class="destination-text">{advice.guidance}</p>'
        f'</div>'
        f'<div class="protocol-container">'
        f'<div class="protocol-title">Protocolo de Separação e Manejo</div>'
        f'<ul class="protocol-list">{tips_html}</ul>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)
