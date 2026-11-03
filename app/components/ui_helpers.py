"""
Componentes Visuais e Folha de Estilos da Interface Web (BioCiclo IA)
Identidade visual Eco-Tech moderna, inspirada em sustentabilidade urbana,
padrão CONAMA de cores de coletores e clareza analítica.
"""

from typing import List, Dict, Any
import streamlit as st
from src.rules.destination import DestinationAdvice
from src.rules.cultural_analysis import RegionalItemProfile


def render_html(raw_html: str) -> None:
    """
    Remove indentação inicial de cada linha antes de enviar ao st.markdown,
    impedindo que o parser Markdown interprete linhas indentadas como bloco de código <pre><code>.
    """
    clean_html = "\n".join(line.strip() for line in raw_html.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3.5rem;
    max-width: 1340px;
}

/* Cabeçalho Hero Principal */
.hero-banner {
    position: relative;
    background: radial-gradient(circle at 88% 18%, rgba(16, 185, 129, 0.18) 0%, rgba(6, 78, 59, 0.10) 38%, rgba(14, 24, 19, 0.96) 100%);
    border: 1px solid rgba(16, 185, 129, 0.28);
    border-left: 5px solid #10B981;
    border-radius: 14px;
    padding: 1.65rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.45);
}

.hero-top-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.55rem;
}

.header-kicker {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.73rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #34D399;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.30);
    padding: 0.28rem 0.75rem;
    border-radius: 999px;
}

.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
}

.hero-pill {
    font-size: 0.72rem;
    font-weight: 600;
    color: #A7F3D0;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.10);
    padding: 0.24rem 0.65rem;
    border-radius: 6px;
}

.main-title {
    font-size: 1.95rem;
    font-weight: 800;
    color: #F0FDF4;
    margin: 0.25rem 0 0.45rem 0;
    letter-spacing: -0.025em;
    line-height: 1.2;
}

.subtitle {
    font-size: 0.94rem;
    color: #9CA3AF;
    margin: 0;
    line-height: 1.55;
    max-width: 960px;
}

/* Títulos de Seção */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6EE7B7;
    margin-bottom: 0.4rem;
}

.section-heading {
    font-size: 1.15rem;
    font-weight: 700;
    color: #F0FDF4;
    margin: 0 0 1rem 0;
    padding-bottom: 0.55rem;
    border-bottom: 1px solid rgba(16, 185, 129, 0.18);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Card Principal de Diagnóstico */
.diagnostic-card {
    background: linear-gradient(165deg, rgba(16, 29, 23, 0.96) 0%, rgba(10, 18, 14, 0.98) 100%);
    border: 1px solid rgba(16, 185, 129, 0.22);
    border-radius: 14px;
    padding: 1.5rem 1.65rem;
    margin-bottom: 1rem;
    box-shadow: 0 10px 28px -10px rgba(0, 0, 0, 0.5);
}

.diagnostic-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.material-name {
    font-size: 1.68rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0.15rem 0 0 0;
    letter-spacing: -0.02em;
}

.confidence-box {
    text-align: right;
    min-width: 145px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 0.55rem 0.85rem;
}

.confidence-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem;
    font-weight: 700;
    color: #F0FDF4;
    line-height: 1.15;
}

.confidence-status {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.15rem;
}

.conf-high { color: #34D399; }
.conf-low { color: #FBBF24; }

.progress-track {
    width: 100%;
    height: 8px;
    background-color: rgba(255, 255, 255, 0.07);
    border-radius: 999px;
    overflow: hidden;
    margin: 0.35rem 0 1.15rem 0;
}

.progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.35s ease;
}

/* Card Visual do Coletor Oficial CONAMA */
.conama-bin-banner {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 1.1rem;
}

.conama-bin-icon {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-weight: 800;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}

.conama-bin-meta {
    flex: 1;
}

.conama-bin-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #9CA3AF;
}

.conama-bin-title {
    font-size: 1rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0.1rem 0 0 0;
}

/* Badges */
.badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.15rem;
}

.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.32rem 0.78rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    text-transform: uppercase;
}

.badge-organic {
    background-color: rgba(16, 185, 129, 0.16);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.45);
}

.badge-recyclable {
    background-color: rgba(59, 130, 246, 0.16);
    color: #93C5FD;
    border: 1px solid rgba(59, 130, 246, 0.45);
}

.badge-trash {
    background-color: rgba(148, 163, 184, 0.16);
    color: #CBD5E1;
    border: 1px solid rgba(148, 163, 184, 0.4);
}

.badge-calibrated {
    background-color: rgba(168, 85, 247, 0.15);
    color: #D8B4FE;
    border: 1px solid rgba(168, 85, 247, 0.4);
}

/* Painéis internos do Card */
.destination-panel {
    background-color: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-left: 4px solid #10B981;
    border-radius: 8px;
    padding: 0.95rem 1.15rem;
    margin-bottom: 0.95rem;
}

.destination-title {
    font-size: 0.92rem;
    font-weight: 700;
    color: #F0FDF4;
    margin: 0 0 0.3rem 0;
}

.destination-text {
    font-size: 0.87rem;
    color: #D1D5DB;
    margin: 0;
    line-height: 1.55;
}

.regional-context-box {
    background: rgba(245, 158, 11, 0.07);
    border: 1px solid rgba(245, 158, 11, 0.28);
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.95rem;
}

.regional-context-title {
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #FBBF24;
    margin-bottom: 0.25rem;
}

.regional-context-text {
    font-size: 0.84rem;
    color: #E5E7EB;
    margin: 0;
    line-height: 1.5;
}

.protocol-container {
    background-color: rgba(7, 13, 10, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 8px;
    padding: 0.95rem 1.15rem;
}

.protocol-title {
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #6EE7B7;
    margin: 0 0 0.55rem 0;
}

.protocol-list {
    margin: 0;
    padding-left: 1.15rem;
    color: #D1D5DB;
    font-size: 0.86rem;
    line-height: 1.6;
}

.protocol-list li {
    margin-bottom: 0.35rem;
}

/* Barra de Composição Multi-Objeto */
.composition-card {
    background: rgba(14, 24, 19, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}

.comp-bar-wrap {
    display: flex;
    height: 10px;
    width: 100%;
    border-radius: 999px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.06);
    margin: 0.55rem 0;
}

/* Alertas e Estados Vazios */
.uncertainty-alert {
    background-color: rgba(245, 158, 11, 0.10);
    border: 1px solid rgba(245, 158, 11, 0.40);
    border-left: 4px solid #F59E0B;
    border-radius: 10px;
    padding: 1rem 1.15rem;
    margin-bottom: 1rem;
}

.uncertainty-title {
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #FBBF24;
    margin: 0 0 0.25rem 0;
}

.uncertainty-desc {
    font-size: 0.85rem;
    color: #E5E7EB;
    margin: 0;
    line-height: 1.5;
}

.empty-state-box {
    background: linear-gradient(180deg, rgba(16, 29, 23, 0.7) 0%, rgba(10, 18, 14, 0.7) 100%);
    border: 1px dashed rgba(16, 185, 129, 0.30);
    border-radius: 14px;
    padding: 2.75rem 1.75rem;
    text-align: center;
    margin-top: 0.35rem;
}

.empty-state-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #F0FDF4;
    margin: 0.5rem 0 0.4rem 0;
}

.empty-state-text {
    font-size: 0.88rem;
    color: #9CA3AF;
    max-width: 470px;
    margin: 0 auto;
    line-height: 1.55;
}

/* Cards de KPI e Informações */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.9rem;
    margin-bottom: 1.35rem;
}

.kpi-card {
    background: rgba(16, 29, 23, 0.88);
    border: 1px solid rgba(16, 185, 129, 0.18);
    border-radius: 12px;
    padding: 1.05rem 1.2rem;
}

.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.65rem;
    font-weight: 700;
    color: #34D399;
    line-height: 1.15;
    margin-bottom: 0.25rem;
}

.kpi-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #D1D5DB;
}

.kpi-sub {
    font-size: 0.73rem;
    color: #9CA3AF;
    margin-top: 0.15rem;
}

.info-card {
    background: rgba(16, 29, 23, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 1.35rem;
    margin-bottom: 1rem;
}

.info-card-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F0FDF4;
    margin: 0 0 0.55rem 0;
}

.info-card-body {
    font-size: 0.88rem;
    color: #D1D5DB;
    line-height: 1.6;
    margin: 0;
}

/* Sidebar */
.sidebar-status-card {
    background-color: rgba(16, 185, 129, 0.05);
    border: 1px solid rgba(16, 185, 129, 0.20);
    border-radius: 10px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
}

.status-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
}

.dot-online {
    background-color: #10B981;
    box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);
}

.dot-fallback {
    background-color: #F59E0B;
}

.status-label {
    font-size: 0.83rem;
    font-weight: 700;
    color: #F0FDF4;
}

.status-sub {
    font-size: 0.76rem;
    color: #9CA3AF;
    margin: 0;
    line-height: 1.45;
}

/* Abas do Streamlit */
.stTabs [data-baseweb="tab-list"] {
    gap: 1.1rem;
    border-bottom: 1px solid rgba(16, 185, 129, 0.20);
}

.stTabs [data-baseweb="tab"] {
    padding-top: 0.65rem;
    padding-bottom: 0.8rem;
    font-weight: 700;
    font-size: 0.92rem;
}
</style>
"""


def inject_styles():
    """Injeta a folha de estilos customizada na página."""
    render_html(CUSTOM_CSS)


def render_header():
    """Renderiza o cabeçalho institucional superior com estilo Eco-Tech."""
    html = """
    <div class="hero-banner">
        <div class="hero-top-row">
            <div class="header-kicker">
                <span>UFS &bull; DComp &bull; Programa BioCiclo Urbano (Aracaju / EMSURB)</span>
            </div>
            <div class="hero-pills">
                <span class="hero-pill">YOLO11 Computer Vision</span>
                <span class="hero-pill">Padrão CONAMA 275</span>
                <span class="hero-pill">Análise Cultural SE/NE</span>
            </div>
        </div>
        <h1 class="main-title">BioCiclo IA &mdash; Classificação Inteligente e Destinação de Resíduos</h1>
        <p class="subtitle">
            Plataforma de triagem assistida por visão computacional para segregação entre resíduos orgânicos compostáveis
            e recicláveis secos, com calibração para embalagens e biomassa típicas de Aracaju e do Nordeste brasileiro.
        </p>
    </div>
    """
    render_html(html)


def render_empty_state():
    """Renderiza o estado inicial quando nenhuma imagem foi submetida."""
    html = """
    <div class="empty-state-box">
        <div style="font-size: 2.2rem; margin-bottom: 0.25rem;">♻️</div>
        <h4 class="empty-state-title">Pronto para Inspeção e Triagem Visual</h4>
        <p class="empty-state-text">
            Envie uma fotografia, capture pela câmera ou selecione um item do catálogo à esquerda para
            identificar o material, visualizar o coletor CONAMA indicado e consultar as diretrizes do BioCiclo Urbano.
        </p>
    </div>
    """
    render_html(html)


def render_no_detection_state(threshold: float):
    """Renderiza aviso técnico quando nenhuma classe atinge o limiar mínimo de confiança."""
    html = f"""
    <div class="uncertainty-alert">
        <div class="uncertainty-title">Nenhum Objeto Detectado Acima do Limiar ({threshold * 100:.0f}%)</div>
        <p class="uncertainty-desc">
            O detector não encontrou resíduos com confiança igual ou superior ao corte selecionado.
        </p>
    </div>
    <div class="protocol-container">
        <div class="protocol-title">Protocolo Recomendado para Nova Captura</div>
        <ul class="protocol-list">
            <li>Posicione o resíduo ou embalagem no centro da imagem ocupando pelo menos 40% do quadro.</li>
            <li>Em embalagens flexíveis de marcas locais (ex: pacotes de flocão, café ou biscoito), evite reflexos fortes de flash sobre o plástico.</li>
            <li>Prefira superfícies neutras para destacar os contornos do material.</li>
            <li>Se desejar inspecionar predições de menor confiança, reduza o <strong>Limiar de Confiança</strong> na barra lateral.</li>
        </ul>
    </div>
    """
    render_html(html)


def render_scene_composition(all_dets: List[Any]):
    """
    Exibe um resumo visual da composição da cena (Orgânico vs. Reciclável vs. Rejeito)
    e alerta caso haja mistura que possa gerar contaminação cruzada.
    """
    if not all_dets:
        return

    total = len(all_dets)
    org_count = sum(1 for d in all_dets if "Orgânico" in d.advice.waste_type)
    rec_count = sum(1 for d in all_dets if "Reciclável" in d.advice.waste_type)
    oth_count = total - org_count - rec_count

    org_pct = (org_count / total) * 100
    rec_pct = (rec_count / total) * 100
    oth_pct = (oth_count / total) * 100

    mixed_warning = ""
    if org_count > 0 and rec_count > 0:
        mixed_warning = """
        <div style="margin-top: 0.55rem; font-size: 0.8rem; color: #FBBF24; font-weight: 600;">
            ⚠️ Mistura Detectada (Orgânico + Reciclável na mesma cena): Segregue os materiais imediatamente para evitar contaminação cruzada!
        </div>
        """

    html = f"""
    <div class="composition-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="section-label" style="margin: 0;">Composição da Cena ({total} item(ns) detectado(s))</span>
            <span style="font-size: 0.78rem; color: #D1D5DB;">
                🟢 Orgânico: <strong>{org_count}</strong> &nbsp;|&nbsp; 🔵 Reciclável Seco: <strong>{rec_count}</strong> &nbsp;|&nbsp; ⚪ Outros: <strong>{oth_count}</strong>
            </span>
        </div>
        <div class="comp-bar-wrap">
            <div style="width: {org_pct:.1f}%; background-color: #10B981;"></div>
            <div style="width: {rec_pct:.1f}%; background-color: #3B82F6;"></div>
            <div style="width: {oth_pct:.1f}%; background-color: #64748B;"></div>
        </div>
        {mixed_warning}
    </div>
    """
    render_html(html)


def render_advice_card(advice: DestinationAdvice, confidence: float, calibrated: bool = False):
    """
    Renderiza o painel de resultado com diagnóstico, coletor oficial CONAMA,
    nível de confiança, contexto regional (Aracaju/SE) e protocolo de manejo.
    """
    if "Orgânico" in advice.waste_type:
        badge_class = "badge-organic"
    elif "Reciclável" in advice.waste_type:
        badge_class = "badge-recyclable"
    else:
        badge_class = "badge-trash"

    conf_pct = confidence * 100
    conf_status_text = "Confiabilidade Alta" if not advice.is_uncertain else "Atenção / Revisão"
    conf_status_class = "conf-high" if not advice.is_uncertain else "conf-low"
    bar_color = "#10B981" if not advice.is_uncertain else "#F59E0B"
    clamped_width = min(max(conf_pct, 4.0), 100.0)

    if advice.is_uncertain and advice.warning_message:
        alert_html = f"""
        <div class="uncertainty-alert">
            <div class="uncertainty-title">Alerta Preventivo de Incerteza na Triagem</div>
            <p class="uncertainty-desc">{advice.warning_message}</p>
        </div>
        """
        render_html(alert_html)

    calibrated_badge = (
        '<span class="badge badge-calibrated">Calibração Anti-Viés GC1 Ativa</span>'
        if calibrated
        else ""
    )

    regional_html = ""
    if advice.regional_note:
        regional_html = f"""
        <div class="regional-context-box">
            <div class="regional-context-title">Nota de Contexto Regional (Aracaju / Sergipe)</div>
            <p class="regional-context-text">{advice.regional_note}</p>
        </div>
        """

    tips_html = "".join(f"<li>{tip}</li>" for tip in advice.tips)

    card_html = f"""
    <div class="diagnostic-card">
        <div class="diagnostic-header">
            <div>
                <div class="section-label">Material Principal Identificado</div>
                <h2 class="material-name">{advice.display_name}</h2>
            </div>
            <div class="confidence-box">
                <div class="section-label" style="margin-bottom: 0.1rem;">Confiança</div>
                <div class="confidence-value">{conf_pct:.1f}%</div>
                <div class="confidence-status {conf_status_class}">{conf_status_text}</div>
            </div>
        </div>
        <div class="progress-track">
            <div class="progress-fill" style="width: {clamped_width:.1f}%; background-color: {bar_color};"></div>
        </div>
        <div class="conama-bin-banner" style="border-left: 4px solid {advice.conama_color};">
            <div class="conama-bin-icon" style="background-color: {advice.conama_color};">
                ♻
            </div>
            <div class="conama-bin-meta">
                <div class="conama-bin-label">Padrão Oficial CONAMA 275/2001 &bull; Destinação</div>
                <div class="conama-bin-title">{advice.conama_bin} &rarr; {advice.destination}</div>
            </div>
        </div>
        <div class="badge-row">
            <span class="badge {badge_class}">Grupo: {advice.waste_type}</span>
            <span class="badge" style="background-color: rgba(255,255,255,0.05); color: #F0FDF4; border: 1px solid {advice.action_color};">
                Destino: {advice.destination}
            </span>
            {calibrated_badge}
        </div>
        <div class="destination-panel" style="border-left-color: {advice.action_color};">
            <div class="destination-title">Diretriz Técnica &mdash; {advice.destination}</div>
            <p class="destination-text">{advice.guidance}</p>
        </div>
        {regional_html}
        <div class="protocol-container">
            <div class="protocol-title">Protocolo Operacional de Separação e Manejo</div>
            <ul class="protocol-list">{tips_html}</ul>
        </div>
    </div>
    """
    render_html(card_html)


def render_cultural_kpi_strip(metrics: Dict[str, Any]):
    """Renderiza os cartões de KPI do estudo de viés cultural e marcas regionais."""
    html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-value">{metrics['total_analyzed']} Grupos</div>
            <div class="kpi-label">Embalagens e Resíduos Regionais</div>
            <div class="kpi-sub">Mapeados no mercado de Aracaju / SE e Nordeste</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value">{metrics['avg_compatibility_score']}%</div>
            <div class="kpi-label">Compatibilidade Média (GC1 Puro)</div>
            <div class="kpi-sub">Taxa média de generalização do dataset estrangeiro</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color: #FBBF24;">{metrics['medium_count'] + metrics['low_count']} Casos</div>
            <div class="kpi-label">Sensíveis a Viés Cultural (Domain Shift)</div>
            <div class="kpi-sub">Plásticos flexíveis (cuscuz/café), Tetra Pak e coco verde</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-value" style="color: #60A5FA;">{metrics['high_count']} Grupos</div>
            <div class="kpi-label">Alta Invariância Geométrica</div>
            <div class="kpi-sub">Garrafas PET/Vidro (Cajuína/Guaraná), latas e folhosos</div>
        </div>
    </div>
    """
    render_html(html)


def render_regional_item_card(item: RegionalItemProfile):
    """Renderiza um card analítico detalhado para um item/marca regional."""
    if item.compatibility_level == "Alta":
        lvl_color = "#10B981"
        lvl_bg = "rgba(16, 185, 129, 0.14)"
    elif item.compatibility_level == "Média":
        lvl_color = "#F59E0B"
        lvl_bg = "rgba(245, 158, 11, 0.14)"
    else:
        lvl_color = "#EF4444"
        lvl_bg = "rgba(239, 68, 68, 0.14)"

    html = f"""
    <div class="info-card" style="border-left: 4px solid {lvl_color}; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.6rem;">
            <div>
                <div class="section-label" style="margin-bottom: 0.15rem;">{item.category_region}</div>
                <div class="info-card-title" style="font-size: 1.1rem; margin-bottom: 0.15rem;">{item.name}</div>
                <div style="font-size: 0.82rem; color: #9CA3AF;">
                    <strong>Marcas / Ocorrência Local:</strong> {item.brands_examples}
                </div>
            </div>
            <div style="text-align: right;">
                <span style="background: {lvl_bg}; color: {lvl_color}; border: 1px solid {lvl_color}; padding: 0.28rem 0.7rem; border-radius: 999px; font-size: 0.74rem; font-weight: 700; text-transform: uppercase;">
                    Compatibilidade GC1: {item.compatibility_level} ({item.compatibility_score}%)
                </span>
            </div>
        </div>
        <div class="progress-track" style="height: 6px; margin: 0.4rem 0 0.85rem 0;">
            <div class="progress-fill" style="width: {item.compatibility_score}%; background-color: {lvl_color};"></div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.75rem; margin-bottom: 0.8rem; background: rgba(0,0,0,0.25); padding: 0.75rem 0.9rem; border-radius: 8px;">
            <div>
                <div style="font-size: 0.7rem; text-transform: uppercase; color: #9CA3AF; font-weight: 700;">Material Real (Gabarito)</div>
                <div style="font-size: 0.88rem; color: #34D399; font-weight: 700;">{item.expected_display} ({item.expected_class})</div>
            </div>
            <div>
                <div style="font-size: 0.7rem; text-transform: uppercase; color: #9CA3AF; font-weight: 700;">Comportamento do Modelo Estrangeiro (GC1)</div>
                <div style="font-size: 0.86rem; color: #FBBF24; font-weight: 600;">{item.common_model_prediction}</div>
            </div>
        </div>
        <p class="info-card-body" style="margin-bottom: 0.55rem;">
            <strong>Por que ocorre essa diferença cultural/técnica?</strong> {item.cultural_gap_reason}
        </p>
        <p class="info-card-body" style="margin-bottom: 0.45rem; color: #A7F3D0;">
            <strong>Diretriz Local (Aracaju / EMSURB / CARE):</strong> {item.local_disposal_rule}
        </p>
        <p class="info-card-body" style="font-size: 0.82rem; color: #9CA3AF;">
            <strong>Mitigação Recomendada no Projeto:</strong> {item.recommended_fix}
        </p>
    </div>
    """
    render_html(html)
