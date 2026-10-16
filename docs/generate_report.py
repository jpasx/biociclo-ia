"""
Gerador de Relatório Técnico Acadêmico em PDF - BioCiclo IA
Compila o relatório completo de Entrega Parcial com formatação ABNT/institucional,
gráficos embutidos, tabelas, código-fonte e métricas quantitativas.
"""

import os
import base64
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "docs"
ASSETS_DIR = DOCS_DIR / "assets"
HTML_OUTPUT = DOCS_DIR / "Entrega_Parcial_BioCiclo_IA.html"
PDF_OUTPUT = ROOT_DIR / "Entrega_Parcial_BioCiclo_IA.pdf"


def image_to_base64(path: Path) -> str:
    """Converte arquivo de imagem para string base64 data URI."""
    if not path.exists():
        return ""
    suffix = path.suffix.lower().replace(".", "")
    if suffix == "jpg":
        suffix = "jpeg"
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{suffix};base64,{encoded}"


def build_html() -> str:
    # Carregar imagens em base64 para garantir independência de caminhos no PDF
    img_interface = image_to_base64(ASSETS_DIR / "app_interface.png")
    img_confusion = image_to_base64(ASSETS_DIR / "confusion_matrix.png")
    img_f1 = image_to_base64(ASSETS_DIR / "f1_curve.png")
    img_results = image_to_base64(ASSETS_DIR / "training_results.png")
    img_val_batch = image_to_base64(ASSETS_DIR / "validation_batch_pred.jpg")

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>BioCiclo IA - Relatório Técnico de Entrega Parcial</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 18mm 20mm 18mm;
            @bottom-right {{
                content: counter(page);
                font-size: 9pt;
                color: #555;
            }}
        }}

        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            font-size: 10.5pt;
            line-height: 1.55;
            color: #1a1a1a;
            background: #ffffff;
            margin: 0;
            padding: 0;
        }}

        /* Quebras de página controladas */
        .page-break {{
            page-break-after: always;
            break-after: page;
        }}
        .no-break {{
            page-break-inside: avoid;
            break-inside: avoid;
        }}

        /* Capa */
        .cover {{
            min-height: 88vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            text-align: center;
            padding: 20px 0 40px 0;
        }}
        .cover-header {{
            border-bottom: 2px solid #2e7d32;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .cover-inst {{
            font-size: 11pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #1b5e20;
            margin: 0 0 4px 0;
        }}
        .cover-dept {{
            font-size: 9.5pt;
            font-weight: 600;
            color: #444;
            margin: 0;
        }}
        .cover-center {{
            margin: 50px 0;
        }}
        .cover-title {{
            font-size: 22pt;
            font-weight: 800;
            color: #111;
            line-height: 1.25;
            margin: 0 0 15px 0;
            letter-spacing: -0.02em;
        }}
        .cover-subtitle {{
            font-size: 12.5pt;
            font-weight: 500;
            color: #2e7d32;
            line-height: 1.4;
            margin: 0 auto;
            max-width: 90%;
        }}
        .cover-tag {{
            display: inline-block;
            background: #e8f5e9;
            color: #1b5e20;
            border: 1px solid #a5d6a7;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 9pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 15px;
        }}
        .cover-details {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2e7d32;
            border-radius: 6px;
            padding: 18px 24px;
            text-align: left;
            margin-top: 30px;
            font-size: 9.5pt;
        }}
        .cover-details table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .cover-details td {{
            padding: 3px 0;
            vertical-align: top;
        }}
        .cover-details td.label {{
            font-weight: 700;
            color: #334155;
            width: 140px;
        }}
        .cover-details td.value {{
            color: #0f172a;
        }}
        .cover-footer {{
            font-size: 9pt;
            color: #64748b;
            margin-top: 30px;
            border-top: 1px solid #e2e8f0;
            padding-top: 12px;
        }}

        /* Tipografia de Seções */
        h1.section-title {{
            font-size: 15pt;
            font-weight: 800;
            color: #111827;
            border-bottom: 2px solid #2e7d32;
            padding-bottom: 6px;
            margin: 28px 0 14px 0;
            text-transform: uppercase;
            letter-spacing: -0.01em;
        }}
        h2.subsection-title {{
            font-size: 12pt;
            font-weight: 700;
            color: #1f2937;
            margin: 18px 0 8px 0;
            border-left: 3px solid #2e7d32;
            padding-left: 8px;
        }}
        h3.subsubsection-title {{
            font-size: 10.5pt;
            font-weight: 700;
            color: #374151;
            margin: 12px 0 6px 0;
        }}

        p {{
            text-align: justify;
            margin: 0 0 10px 0;
        }}

        /* Caixas de Destaque */
        .callout {{
            background-color: #f8fafc;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2e7d32;
            border-radius: 6px;
            padding: 12px 16px;
            margin: 14px 0;
            font-size: 9.5pt;
        }}
        .callout-title {{
            font-weight: 700;
            color: #1b5e20;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            font-size: 8.5pt;
        }}

        .callout-warning {{
            background-color: #fffbeb;
            border: 1px solid #fde68a;
            border-left: 4px solid #f59e0b;
        }}
        .callout-warning .callout-title {{
            color: #b45309;
        }}

        /* Tabelas */
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 14px 0;
            font-size: 9pt;
        }}
        table.data-table th {{
            background-color: #f1f5f9;
            color: #0f172a;
            font-weight: 700;
            text-align: left;
            padding: 8px 10px;
            border: 1px solid #cbd5e1;
        }}
        table.data-table td {{
            padding: 7px 10px;
            border: 1px solid #e2e8f0;
            vertical-align: top;
        }}
        table.data-table tr:nth-child(even) {{
            background-color: #f8fafc;
        }}

        /* Badges */
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 8pt;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .badge-green {{ background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }}
        .badge-blue  {{ background: #dbeafe; color: #1d4ed8; border: 1px solid #bfdbfe; }}
        .badge-yellow{{ background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }}
        .badge-gray  {{ background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }}

        /* Bloco de Código */
        pre.code-block {{
            background: #0f172a;
            color: #e2e8f0;
            padding: 12px 14px;
            border-radius: 6px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 8.5pt;
            line-height: 1.45;
            overflow-x: hidden;
            white-space: pre-wrap;
            margin: 12px 0;
            border: 1px solid #1e293b;
        }}

        /* Figuras e Imagens */
        .figure-container {{
            text-align: center;
            margin: 16px 0;
            page-break-inside: avoid;
        }}
        .figure-container img {{
            max-width: 95%;
            height: auto;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        }}
        .figure-caption {{
            font-size: 8.5pt;
            color: #475569;
            margin-top: 6px;
            font-style: italic;
        }}

        /* Grade de 2 colunas */
        .grid-2 {{
            display: flex;
            gap: 16px;
            margin: 12px 0;
        }}
        .grid-2 > div {{
            flex: 1;
        }}

        /* Lista de Métricas */
        .metric-cards {{
            display: flex;
            gap: 10px;
            margin: 12px 0;
        }}
        .metric-card {{
            flex: 1;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-top: 3px solid #2e7d32;
            border-radius: 6px;
            padding: 10px;
            text-align: center;
        }}
        .metric-val {{
            font-size: 16pt;
            font-weight: 800;
            color: #1b5e20;
            line-height: 1.1;
        }}
        .metric-label {{
            font-size: 7.5pt;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
            margin-top: 4px;
        }}
    </style>
</head>
<body>

    <!-- ============================================================== -->
    <!-- CAPA FORMAL                                                    -->
    <!-- ============================================================== -->
    <div class="cover page-break">
        <div class="cover-header">
            <div class="cover-inst">Universidade Federal de Sergipe &bull; UFS</div>
            <div class="cover-dept">Centro de Ciências Exatas e Tecnologia &bull; Departamento de Computação (DComp)</div>
            <div class="cover-dept">Disciplina: Fundamentos da Inteligência Artificial (2026.1)</div>
        </div>

        <div class="cover-center">
            <h1 class="cover-title">BioCiclo IA</h1>
            <div class="cover-subtitle">
                Sistema Inteligente para Triagem Automatizada e Recomendação de Destinação de Resíduos Sólidos Urbanos por Visão Computacional
            </div>
            <div class="cover-tag">Relatório Técnico de Entrega Parcial</div>
        </div>

        <div class="cover-details">
            <table>
                <tr>
                    <td class="label">Discente(s):</td>
                    <td class="value"><strong>João Paulo</strong> (jpasx) & Equipe BioCiclo IA</td>
                </tr>
                <tr>
                    <td class="label">Docente Responsável:</td>
                    <td class="value">Prof. da Disciplina de Fundamentos da Inteligência Artificial</td>
                </tr>
                <tr>
                    <td class="label">Repositório Oficial:</td>
                    <td class="value"><a href="https://github.com/jpasx/biociclo-ia" style="color: #2e7d32; text-decoration: none;">https://github.com/jpasx/biociclo-ia</a></td>
                </tr>
                <tr>
                    <td class="label">Aplicação em Produção:</td>
                    <td class="value"><a href="https://biociclo-ia-agdxnwg347okmwdspmfc6u.streamlit.app/" style="color: #2e7d32; text-decoration: none;">https://biociclo-ia-agdxnwg347okmwdspmfc6u.streamlit.app/</a></td>
                </tr>
                <tr>
                    <td class="label">Contexto e Parceria:</td>
                    <td class="value">Programa BioCiclo Urbano (Prefeitura Municipal de Aracaju & EMSURB)</td>
                </tr>
            </table>
        </div>

        <div class="cover-footer">
            São Cristóvão / Aracaju &mdash; Sergipe, Brasil &bull; Outubro de 2026
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- RESUMO EXECUTIVO & PAINEL DE STATUS                            -->
    <!-- ============================================================== -->
    <h1 class="section-title">Resumo Executivo do Projeto</h1>

    <p>
        O presente documento constitui o <strong>Relatório Técnico de Entrega Parcial</strong> do projeto 
        <strong>BioCiclo IA</strong>, desenvolvido no âmbito da disciplina de <em>Fundamentos da Inteligência Artificial</em> 
        do Departamento de Computação da Universidade Federal de Sergipe (UFS).
    </p>

    <p>
        O objetivo do projeto é conceber, treinar, avaliar e disponibilizar uma solução tecnológica baseada em 
        <strong>Visão Computacional e Aprendizado Profundo (Deep Learning)</strong> voltada à classificação em tempo real 
        de resíduos sólidos e à recomendação automatizada de sua destinação ambientalmente adequada. O sistema é 
        estrategicamente desenhado para apoiar as ações do programa <strong>BioCiclo Urbano</strong>, iniciativa municipal 
        conduzida pela Prefeitura de Aracaju em articulação com a Empresa Municipal de Serviços Urbanos (EMSURB), cujo 
        propósito é desviar resíduos orgânicos de feiras e mercados dos aterros sanitários e transformá-los em adubo orgânico de alta qualidade.
    </p>

    <div class="callout">
        <div class="callout-title">Painel de Entregas &bull; Status do Projeto até o Momento</div>
        A equipe concluiu com êxito todas as etapas previstas para a primeira metade do cronograma:
        <ul style="margin: 6px 0 0 16px; padding: 0;">
            <li><strong>Modelagem e Treinamento:</strong> Fine-tuning da rede neural YOLO11n concluído em GPU (Google Colab T4) em dataset com 10.464 imagens e 6 classes, gerando os pesos oficiais <code>best.pt</code> (5.5 MB).</li>
            <li><strong>Camada de Regras Especialistas:</strong> Mapeamento determinístico de destinação (Compostagem vs. Coleta Seletiva vs. Aterro) com mecanismo de segurança contra incerteza em inferências abaixo de limiar.</li>
            <li><strong>Interface Web Interativa (MVP):</strong> Aplicação Streamlit completa com triagem lado a lado, captura por câmera, catálogo de testes homologados e design escuro institucional livre de emojis.</li>
            <li><strong>Disponibilidade e Deploy:</strong> Aplicação hospedada publicamente na nuvem (Streamlit Cloud) com CI/CD integrado ao GitHub e script executável local (<code>iniciar_local.bat</code>).</li>
        </ul>
    </div>

    <div class="metric-cards">
        <div class="metric-card">
            <div class="metric-val">10.464</div>
            <div class="metric-label">Imagens no Dataset (GC1)</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">6</div>
            <div class="metric-label">Classes de Resíduos</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">92% / 90%</div>
            <div class="metric-label">Precisão Papel / Plástico</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">84.2%</div>
            <div class="metric-label">Confiança Orgânicos</div>
        </div>
        <div class="metric-card">
            <div class="metric-val">100%</div>
            <div class="metric-label">Deploy Ativo na Nuvem</div>
        </div>
    </div>

    <!-- ============================================================== -->
    <!-- 1. CONTEXTUALIZAÇÃO E FORMULAÇÃO DO PROBLEMA                   -->
    <!-- ============================================================== -->
    <h1 class="section-title">1. Contextualização e Formulação do Problema</h1>

    <h2 class="subsection-title">1.1 O Cenário do BioCiclo Urbano em Aracaju</h2>
    <p>
        A gestão de resíduos sólidos urbanos representa um dos mais prementes desafios socioambientais das capitais brasileiras. 
        Em Aracaju, a <strong>Empresa Municipal de Serviços Urbanos (EMSURB)</strong> gerencia um volume expressivo de resíduos 
        diários provenientes de feiras livres, mercados centrais, supermercados e estabelecimentos comerciais. Dentre esses, a fração 
        orgânica constitui mais de 50% do volume total descartado. Quando destinada a aterros sanitários, a matéria orgânica 
        sofre decomposição anaeróbia, gerando grandes quantidades de gás metano (CH<sub>4</sub>) &mdash; um gás de efeito estufa 
        com potencial de aquecimento mais de 25 vezes superior ao dióxido de carbono &mdash; e lixiviado (chorume), com alto risco 
        de contaminação de lençóis freáticos.
    </p>
    <p>
        Para mitigar esse impacto, a Prefeitura de Aracaju instituiu o <strong>BioCiclo Urbano</strong>, programa de compostagem 
        termófila controlada que recolhe restos de hortifrutis de feiras municipais e os converte em biofertilizante rico em 
        macro e micronutrientes, empregado na adubação de canteiros públicos, hortas comunitárias e agricultura familiar periurbana.
    </p>

    <h2 class="subsection-title">1.2 O Gargalo da Triagem e Contaminação Cruzada</h2>
    <p>
        O principal obstáculo operacional à escala do BioCiclo Urbano reside na <strong>contaminação cruzada na fonte</strong>. 
        Resíduos orgânicos raramente chegam segregados de maneira homogênea: feirantes e cidadãos frequentemente misturam cascas 
        e frutas com sacolas plásticas, fitas adesivas, copos descartáveis, latas de alumínio e embalagens de papelão. 
        A presença de apenas uma fração de plástico ou metal em pilhas de compostagem inviabiliza lotes inteiros de adubo e pode 
        avariar maquinários de trituração.
    </p>
    <p>
        Portanto, um sistema inteligente viável <strong>não pode reconhecer unicamente resíduos orgânicos</strong>. Ele deve 
        possuir a capacidade de detectar simultaneamente múltiplas categorias de lixo (recicláveis secos, rejeitos e orgânicos) e, 
        a partir do diagnóstico visual, recomendar imediatamente a rota de manejo ambiental adequada:
    </p>

    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 25%;">Categoria Identificada</th>
                <th style="width: 20%;">Grupo Operacional</th>
                <th style="width: 30%;">Destinação Recomendada</th>
                <th style="width: 25%;">Impacto Ambiental Esperado</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Orgânico / Biodegradável</strong></td>
                <td><span class="badge badge-green">Orgânico</span></td>
                <td><strong>Compostagem (BioCiclo Urbano)</strong></td>
                <td>Produção de adubo orgânico; mitigação de emissões de metano.</td>
            </tr>
            <tr>
                <td><strong>Plástico</strong></td>
                <td><span class="badge badge-blue">Reciclável</span></td>
                <td>Coleta Seletiva / Cooperativas</td>
                <td>Redução de microplásticos e economia de polímeros virgens.</td>
            </tr>
            <tr>
                <td><strong>Papel</strong></td>
                <td><span class="badge badge-blue">Reciclável</span></td>
                <td>Coleta Seletiva / Reciclagem de Celulose</td>
                <td>Economia de água e celulose industrial (se limpo e seco).</td>
            </tr>
            <tr>
                <td><strong>Papelão</strong></td>
                <td><span class="badge badge-blue">Reciclável</span></td>
                <td>Pontos de Entrega Voluntária (PEVs)</td>
                <td>Alta reciclabilidade; redução de volume em caçambas.</td>
            </tr>
            <tr>
                <td><strong>Metal / Alumínio</strong></td>
                <td><span class="badge badge-yellow">Reciclável</span></td>
                <td>Coleta Seletiva / Fundição</td>
                <td>Economia de 95% de energia em relação à bauxita primária.</td>
            </tr>
            <tr>
                <td><strong>Vidro</strong></td>
                <td><span class="badge badge-blue">Reciclável</span></td>
                <td>PEVs Especiais de Vidro</td>
                <td>100% reciclável infinitas vezes sem perda de massa.</td>
            </tr>
            <tr>
                <td><strong>Rejeito / Não Reciclável</strong></td>
                <td><span class="badge badge-gray">Rejeito</span></td>
                <td>Coleta Convencional &bull; Aterro Sanitário</td>
                <td>Destinação sanitária licenciada para materiais sem reuso.</td>
            </tr>
        </tbody>
    </table>

    <div class="page-break"></div>

    <!-- ============================================================== -->
    <!-- 2. ENGENHARIA DE DADOS E CARACTERIZAÇÃO DO DATASET             -->
    <!-- ============================================================== -->
    <h1 class="section-title">2. Engenharia de Dados e Caracterização da Base</h1>

    <h2 class="subsection-title">2.1 Base de Dados: Garbage Classification 3 (GC1)</h2>
    <p>
        Para capacitar a rede neural com alta generalização visual, selecionou-se como fonte primária o conjunto de dados 
        <strong>Garbage Classification 3 (GC1)</strong>, disponível no repositório de Visão Computacional Roboflow Universe 
        sob licença <em>Creative Commons Attribution 4.0 International (CC BY 4.0)</em>.
    </p>

    <p>
        A base é composta por <strong>10.464 imagens anotadas espacialmente</strong> no padrão nativo do YOLO. 
        Diferentemente de classificadores de imagem simples (onde a imagem inteira recebe um único rótulo), o dataset GC1 
        contém anotações no formato <em>bounding box</em> (caixa delimitadora):
    </p>
    
    <pre class="code-block">&lt;class_id&gt; &lt;x_center&gt; &lt;y_center&gt; &lt;width&gt; &lt;height&gt;
# Coordenadas normalizadas no intervalo [0.0, 1.0] em relação à largura e altura da imagem.</pre>

    <h2 class="subsection-title">2.2 Mapeamento de Classes e Estrutura dos Dados</h2>
    <p>
        A estrutura de classes configurada no arquivo de metadados <code>data.yaml</code> contempla as 6 classes operacionais 
        fundamentais ao projeto:
    </p>

    <table class="data-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Nome da Classe (YOLO)</th>
                <th>Rótulo Amigável</th>
                <th>Exemplos Comuns na Base de Dados</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><code>0</code></td>
                <td><code>BIODEGRADABLE</code></td>
                <td>Orgânico / Biodegradável</td>
                <td>Frutas, legumes, cascas de banana/maçã, verduras, restos de hortifruti.</td>
            </tr>
            <tr>
                <td><code>1</code></td>
                <td><code>CARDBOARD</code></td>
                <td>Papelão</td>
                <td>Caixas de papelão corrugado, placas onduladas, embalagens pardas.</td>
            </tr>
            <tr>
                <td><code>2</code></td>
                <td><code>GLASS</code></td>
                <td>Vidro</td>
                <td>Garrafas transparentes, frascos de conserva, copos de vidro.</td>
            </tr>
            <tr>
                <td><code>3</code></td>
                <td><code>METAL</code></td>
                <td>Metal / Alumínio</td>
                <td>Latas de refrigerante, latas de conserva, tampas metálicas, aerossóis.</td>
            </tr>
            <tr>
                <td><code>4</code></td>
                <td><code>PAPER</code></td>
                <td>Papel</td>
                <td>Copos descartáveis de papel, impressos, folhas brancas, jornais.</td>
            </tr>
            <tr>
                <td><code>5</code></td>
                <td><code>PLASTIC</code></td>
                <td>Plástico</td>
                <td>Garrafas PET, potes de iogurte, sacolas, copos plásticos descartáveis.</td>
            </tr>
        </tbody>
    </table>

    <h2 class="subsection-title">2.3 Pipeline de Pré-processamento e Aumento de Dados (Data Augmentation)</h2>
    <p>
        Com vistas a prevenir o sobreajuste (<em>overfitting</em>) e dotar o modelo de robustez frente a ângulos oblíquos e 
        variações de iluminação típicas de ambientes de triagem, foi aplicado um conjunto de técnicas de aumento de dados durante o treino:
    </p>
    <ul>
        <li><strong>Redimensionamento com preservação de aspecto:</strong> padronização das dimensões para 416&times;416 pixels.</li>
        <li><strong>Mosaic Augmentation (1.0):</strong> combinação de 4 imagens distintas em uma única matriz de treino, forçando a rede a reconhecer objetos parciais e em diferentes escalas espaciais.</li>
        <li><strong>Inversão Horizontal (Flip LR 0.5):</strong> 50% de probabilidade de espelhamento horizontal.</li>
        <li><strong>Variação no Espaço de Cores HSV:</strong> perturbação estocástica de matiz (hsv_h = 0.015), saturação (hsv_s = 0.7) e valor/brilho (hsv_v = 0.4).</li>
        <li><strong>Random Erasing (0.4):</strong> oclusão de regiões retangulares aleatórias para simular resíduos parcialmente cobertos por outros materiais.</li>
    </ul>

    <!-- ============================================================== -->
    <!-- 3. METODOLOGIA E MODELAGEM NEURAL                              -->
    <!-- ============================================================== -->
    <h1 class="section-title">3. Metodologia e Modelagem Neural</h1>

    <h2 class="subsection-title">3.1 Arquitetura Selecionada: Ultralytics YOLO11n</h2>
    <p>
        Para este trabalho, selecionou-se a mais recente geração da família YOLO &mdash; o <strong>YOLO11</strong> da Ultralytics, 
        especificamente na variante <em>nano</em> (<code>yolo11n.pt</code>). 
    </p>
    <p>
        A decisão por uma arquitetura nano fundamenta-se nos seguintes critérios técnicos:
    </p>
    <ul>
        <li><strong>Eficiência computacional extrema:</strong> o modelo possui apenas 2,6 milhões de parâmetros e tamanho final de pesos em disco de <strong>5,5 MB</strong>, permitindo inferências em dezenas de milissegundos mesmo em processadores convencionais (CPU) sem exigir aceleração dedicada em tempo de uso.</li>
        <li><strong>Arquitetura desacoplada (Decoupled Head):</strong> separação explícita entre as perdas de regressão de caixa (<em>box coordinates</em>) e as perdas de classificação (<em>class probabilities</em>), melhorando a precisão em resíduos com limites difusos.</li>
        <li><strong>Blocos C3k2 e SPPF:</strong> captura de contexto multiescala capaz de detectar tanto pequenos fragmentos de metal ou tampinhas quanto caixas volumosas de papelão no mesmo campo de visão.</li>
    </ul>

    <h2 class="subsection-title">3.2 Protocolo de Treinamento e Fine-Tuning</h2>
    <p>
        Empregou-se a estratégia de <strong>Aprendizado por Transferência (Transfer Learning)</strong>. A rede foi inicializada 
        com pesos pré-treinados na base COCO (80 classes genéricas) e posteriormente submetida a ajuste fino (<em>fine-tuning</em>) 
        supervisionado sobre o dataset GC1.
    </p>
    <p>
        O treinamento foi conduzido em ambiente em nuvem <strong>Google Colab</strong> utilizando uma GPU dedicada 
        <strong>NVIDIA Tesla T4 (16 GB GDDR6 VRAM)</strong>. A configuração de treinamento adotou:
    </p>
    <ul>
        <li><strong>Épocas de treino:</strong> 30 épocas com <em>warmup</em> inicial de 3 épocas.</li>
        <li><strong>Tamanho de lote (Batch Size):</strong> 16 imagens por passo de gradiente.</li>
        <li><strong>Otimizador:</strong> SGD com <em>momentum</em> de 0.937 e <em>weight decay</em> de 0.0005.</li>
        <li><strong>Função de Custo Combinada:</strong> CIoU (Complete Intersection over Union) para localização de caixas, Binary Cross-Entropy (BCE) para classificação e Distribution Focal Loss (DFL) para refinamento de bordas.</li>
    </ul>

    <div class="page-break"></div>

    <!-- ============================================================== -->
    <!-- 4. RESULTADOS EXPERIMENTAIS E AVALIAÇÃO QUANTITATIVA           -->
    <!-- ============================================================== -->
    <h1 class="section-title">4. Resultados Experimentais e Avaliação Quantitativa</h1>

    <h2 class="subsection-title">4.1 Desempenho por Classe Operacional</h2>
    <p>
        Após o ciclo de treinamento e validação, os pesos ótimos salvos (<code>best.pt</code>) foram submetidos a testes 
        estatísticos e inferências práticas em imagens reais de bancadas e resíduos soltos. A tabela a seguir sintetiza os 
        níveis médios de confiança e precisão observados nas classes de interesse:
    </p>

    <table class="data-table">
        <thead>
            <tr>
                <th>Classe</th>
                <th>Confiança Média Observada</th>
                <th>Comportamento Visual e Análise Qualitativa</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Papel</strong></td>
                <td><span class="badge badge-green">92,0%</span></td>
                <td>Altíssima discriminação em copos descartáveis de papel e páginas impressas.</td>
            </tr>
            <tr>
                <td><strong>Plástico</strong></td>
                <td><span class="badge badge-green">90,3%</span></td>
                <td>Excelente mapeamento de garrafas PET, embalagens translúcidas e copos plásticos.</td>
            </tr>
            <tr>
                <td><strong>Metal</strong></td>
                <td><span class="badge badge-green">89,0%</span></td>
                <td>Detecção consistente em latas de alumínio e objetos com textura metálica reflexiva.</td>
            </tr>
            <tr>
                <td><strong>Orgânico / Biodegradável</strong></td>
                <td><span class="badge badge-green">84,2%</span></td>
                <td>Reconhecimento preciso de frutas (maçãs, laranjas, bananas) e cascas vegetais.</td>
            </tr>
            <tr>
                <td><strong>Papelão</strong></td>
                <td><span class="badge badge-yellow">58,0%</span></td>
                <td>Sensível à contaminação e amassamento; pode oscilar com papéis pardos pesados.</td>
            </tr>
            <tr>
                <td><strong>Vidro</strong></td>
                <td><span class="badge badge-yellow">54,0%</span></td>
                <td>Desafio decorrente da refração de luz e transparência que absorve cores do fundo.</td>
            </tr>
        </tbody>
    </table>

    <h2 class="subsection-title">4.2 Evidências Gráficas de Validação</h2>
    <p>
        As curvas de treinamento registradas e a matriz de confusão normalizada atestam a convergência e a discriminação entre classes:
    </p>

    <div class="figure-container">
        <img src="__IMG_RESULTS__" alt="Curvas de Treinamento e Perda" style="max-height: 280px;" />
        <div class="figure-caption">Figura 1 &mdash; Evolução das perdas de caixa (box loss), classe (cls loss) e métricas mAP@50 durante o treinamento.</div>
    </div>

    <div class="grid-2">
        <div class="figure-container">
            <img src="__IMG_CONFUSION__" alt="Matriz de Confusão Normalizada" style="max-height: 240px;" />
            <div class="figure-caption">Figura 2 &mdash; Matriz de Confusão Normalizada entre as 6 classes de resíduos.</div>
        </div>
        <div class="figure-container">
            <img src="__IMG_F1__" alt="Curva BoxF1" style="max-height: 240px;" />
            <div class="figure-caption">Figura 3 &mdash; Curva F1-Score em função do Limiar de Confiança.</div>
        </div>
    </div>

    <div class="page-break"></div>

    <!-- ============================================================== -->
    <!-- 5. SISTEMA DE REGRAS DE NEGÓCIO E GOVERNANÇA DA DECISÃO        -->
    <!-- ============================================================== -->
    <h1 class="section-title">5. Sistema Especialista de Regras de Negócio e Governança</h1>

    <h2 class="subsection-title">5.1 Desacoplamento entre Visão e Decisão</h2>
    <p>
        Um princípio arquitetural chave adotado no BioCiclo IA é a <strong>estrita separação de responsabilidades</strong>: 
        o modelo de visão computacional (YOLO) restringe-se a responder <em>"qual material é este e onde ele está localizado"</em>, 
        enquanto uma camada de regras especialistas implementada no módulo <code>src/rules/destination.py</code> responde 
        <em>"para onde esse resíduo deve ir e como o operador deve manuseá-lo"</em>.
    </p>

    <h2 class="subsection-title">5.2 Tratamento Formal de Incerteza (Uncertainty Handling)</h2>
    <p>
        Em sistemas de apoio à decisão ecológica e sanitária, uma predição incorreta pode causar graves danos (ex.: encaminhar 
        um copo plástico contaminado com laticínio para a compostagem). 
    </p>
    <p>
        Para impedir que predições fracas resultem em tomadas de decisão equivocadas, implementou-se uma política de 
        <strong>bloqueio por incerteza</strong>:
    </p>
    <ul>
        <li>O operador pode configurar o <strong>Limiar de Confiança</strong> (valor padrão no MVP: 15% a 50%).</li>
        <li>Caso a confiança da maior detecção fique abaixo do patamar de segurança (50%), a classe <code>DestinationAdvice</code> aciona automaticamente a propriedade <code>is_uncertain = True</code>.</li>
        <li>Nesse caso, a interface exibe um <strong>Alerta Visual de Baixa Confiança</strong>, bloqueando a recomendação automática e instruindo expressamente o usuário a efetuar uma nova captura sob iluminação uniforme e enquadramento centralizado.</li>
    </ul>

    <pre class="code-block"># Trecho representativo de src/rules/destination.py
def get_destination_advice(class_name: str, confidence: float, confidence_threshold: float = 0.50):
    normalized_key = class_name.strip().upper()
    rule = RULES_DATABASE.get(normalized_key, RULES_DATABASE.get("TRASH"))
    is_uncertain = confidence &lt; confidence_threshold

    warning_msg = None
    if is_uncertain:
        warning_msg = (
            f"Confiança de detecção ({confidence*100:.1f}%) abaixo do limiar seguro ({confidence_threshold*100:.0f}%). "
            "Recomenda-se nova captura com melhor iluminação e enquadramento antes da destinação final."
        )

    return DestinationAdvice(
        raw_class=normalized_key,
        display_name=rule["display_name"],
        waste_type=rule["waste_type"],
        destination=rule["destination"],
        action_color=rule["action_color"],
        guidance=rule["guidance"],
        tips=rule["tips"],
        is_uncertain=is_uncertain,
        warning_message=warning_msg
    )</pre>

    <!-- ============================================================== -->
    <!-- 6. ARQUITETURA DE SOFTWARE E DESENVOLVIMENTO DO MVP            -->
    <!-- ============================================================== -->
    <h1 class="section-title">6. Arquitetura de Software e Desenvolvimento da Aplicação (MVP)</h1>

    <h2 class="subsection-title">6.1 Estrutura Modular do Repositório</h2>
    <p>
        O código-fonte do projeto segue as melhores práticas da engenharia de software para projetos de Machine Learning:
    </p>
    <pre class="code-block">biociclo-ia/
├── app/
│   ├── components/
│   │   └── ui_helpers.py       # Estilos CSS, cabeçalho e cards de laudo técnico
│   └── main.py                 # Ponto de entrada da aplicação Streamlit (layout bifocal)
├── data/
│   ├── garbage-classification-3/ # Dataset de treino (10.464 imagens + rótulos)
│   └── samples/                # Imagens de bancada homologadas para testes rápidos
├── models/
│   └── weights/
│       └── best.pt             # Pesos otimizados do modelo treinado (5.5 MB)
├── notebooks/
│   ├── 01_exploracao_dataset.ipynb
│   └── Treinamento_BioCiclo_Google_Colab.ipynb
├── src/
│   ├── config.py               # Constantes globais, caminhos e paleta cromática
│   ├── models/
│   │   └── detector.py         # Classe WasteDetector (inferência, anotação inteligente)
│   └── rules/
│       └── destination.py      # Matriz especialista BioCiclo Urbano e regras de descarte
├── .streamlit/
│   └── config.toml             # Configuração nativa de tema escuro institucional
├── iniciar_local.bat           # Executável de inicialização local com 1 clique no Windows
└── requirements.txt            # Dependências fixadas (ultralytics, streamlit, pillow)</pre>

    <h2 class="subsection-title">6.2 Interface Web Interativa (Streamlit)</h2>
    <p>
        A interface foi completamente reformulada atendendo aos mais rigorosos critérios de usabilidade institucional:
    </p>
    <ul>
        <li><strong>Design Livre de Emojis:</strong> eliminação total de símbolos informais em favor de indicadores CSS puros (pontos de status de rede, badges em caixa alta, barras de progresso lineares).</li>
        <li><strong>Layout Bifocal Paralelo:</strong> divisão da tela em duas colunas principais &mdash; à esquerda, seleção e visualização imediata da imagem anotada; à direita, laudo completo com o grupo do resíduo, porcentagem de confiança, destino oficial e lista de orientações práticas.</li>
        <li><strong>Tratamento de Cenas Densas:</strong> em imagens que contêm múltiplos resíduos juntos (como um engradado com dezenas de frutas), o método de anotação delimita todos os objetos mas exibe o rótulo de texto apenas nos 3 itens de maior confiança, eliminando a poluição visual.</li>
        <li><strong>Compatibilidade Móvel:</strong> incorporação de transposição EXIF (<code>ImageOps.exif_transpose</code>) para prevenir inversões de rotação em fotografias capturadas verticalmente por smartphones.</li>
    </ul>

    <div class="figure-container">
        <img src="__IMG_INTERFACE__" alt="Interface Web BioCiclo IA em Execução" />
        <div class="figure-caption">Figura 4 &mdash; Captura da aplicação web em execução no navegador, demonstrando a triagem paralela e a emissão do laudo de destinação.</div>
    </div>

    <div class="page-break"></div>

    <!-- ============================================================== -->
    <!-- 7. PUBLICAÇÃO, DEPLOY EM NUVEM E DISPONIBILIDADE               -->
    <!-- ============================================================== -->
    <h1 class="section-title">7. Publicação, Deploy em Nuvem e Disponibilidade</h1>

    <h2 class="subsection-title">7.1 Repositório Aberto e Versionamento</h2>
    <p>
        O código-fonte integral, histórico de commits e documentação do projeto encontram-se hospedados publicamente no 
        GitHub sob o identificador <a href="https://github.com/jpasx/biociclo-ia" style="color: #2e7d32;"><strong>github.com/jpasx/biociclo-ia</strong></a>. 
        O versionamento de arquivos binários pesados (pesos do modelo <code>best.pt</code> de 5.5 MB) foi configurado de modo a 
        garantir clone imediato sem necessidade de extensões externas.
    </p>

    <h2 class="subsection-title">7.2 Deploy Automatizado em Produção</h2>
    <p>
        Para permitir que docentes, avaliadores e colegas de turma acessem e testem a ferramenta sem necessitar instalar 
        Python ou dependências locais, o sistema foi publicado na infraestrutura de nuvem <strong>Streamlit Community Cloud</strong>:
    </p>

    <div class="callout">
        <div class="callout-title">Endereço Público de Acesso</div>
        URL Permanente do Sistema em Produção: <br>
        <a href="https://biociclo-ia-agdxnwg347okmwdspmfc6u.streamlit.app/" style="color: #2e7d32; font-weight: 700; font-size: 11pt;">
            https://biociclo-ia-agdxnwg347okmwdspmfc6u.streamlit.app/
        </a>
    </div>

    <p>
        A camada de carregamento no arquivo <code>src/models/detector.py</code> foi programada com resiliência de ambiente: 
        ela inspeciona caminhos relativos locais, os pontos de montagem do container Linux (<code>/mount/src/biociclo-ia/</code>) 
        e, caso identifique qualquer divergência de sistema operacional, realiza download autônomo e transparente dos pesos oficiais 
        diretamente do branch <code>main</code> do GitHub, garantindo disponibilidade ininterrupta do modelo treinado.
    </p>

    <!-- ============================================================== -->
    <!-- 8. PRÓXIMAS ETAPAS E CRONOGRAMA DA ENTREGA FINAL               -->
    <!-- ============================================================== -->
    <h1 class="section-title">8. Próximas Etapas e Cronograma para a Entrega Final</h1>

    <p>
        Tendo alcançado com pleno sucesso os objetivos da Entrega Parcial (modelo treinado e funcional, pipeline de regras e 
        MVP em nuvem), o plano de trabalho para a etapa final do semestre contempla:
    </p>

    <table class="data-table">
        <thead>
            <tr>
                <th style="width: 25%;">Etapa Prevista</th>
                <th style="width: 50%;">Descrição Técnica das Atividades</th>
                <th style="width: 25%;">Prazo Estimado</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Coleta de Campo em Aracaju</strong></td>
                <td>Fotografar resíduos em condições reais de feiras livres municipais (ex.: Feira do Mercado Central) para testar a robustez do modelo frente ao cenário local.</td>
                <td>Semanas 1 e 2</td>
            </tr>
            <tr>
                <td><strong>Ajuste Fino Complementar</strong></td>
                <td>Re-treino leve incorporando as novas amostras locais para mitigar falsos positivos em superfícies úmidas e embalagens plásticas amassadas.</td>
                <td>Semana 3</td>
            </tr>
            <tr>
                <td><strong>Estudo de Quantização (Edge)</strong></td>
                <td>Converter o modelo para formatos otimizados como ONNX ou OpenVINO / TensorRT, avaliando a perda de acurácia vs. ganho de FPS para embarcados.</td>
                <td>Semana 4</td>
            </tr>
            <tr>
                <td><strong>Artigo e Apresentação Final</strong></td>
                <td>Consolidação dos resultados definitivos no formato de artigo acadêmico para o DComp/UFS e montagem dos slides de demonstração.</td>
                <td>Semana 5 / Final</td>
            </tr>
        </tbody>
    </table>

    <!-- ============================================================== -->
    <!-- 9. REFERÊNCIAS BIBLIOGRÁFICAS                                  -->
    <!-- ============================================================== -->
    <h1 class="section-title">9. Referências Bibliográficas</h1>

    <p style="font-size: 9pt; line-height: 1.5;">
        [1] REDMON, J.; DIVVALA, S.; GIRSHICK, R.; FARHADI, A. <em>You Only Look Once: Unified, Real-Time Object Detection</em>. In: Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition (CVPR), 2016.<br><br>
        [2] ULTRALYTICS. <em>Ultralytics YOLO11 Documentation and Architecture Specification</em>. 2024. Disponível em: &lt;https://docs.ultralytics.com&gt;.<br><br>
        [3] THUNG, G.; YANG, M. <em>Classification of Trash for Recyclability Status</em>. Stanford University CS229 Project Report, 2016.<br><br>
        [4] ROBOFLOW UNIVERSE. <em>Garbage Classification 3 (GC1) Dataset</em>. Material Identification Project, 2023. Disponível em: &lt;https://universe.roboflow.com&gt;.<br><br>
        [5] PREFEITURA MUNICIPAL DE ARACAJU & EMSURB. <em>BioCiclo Urbano: Diretrizes para Aproveitamento de Resíduos Orgânicos e Compostagem Pública</em>. Aracaju, SE, 2024.
    </p>

</body>
</html>
"""
    html = (
        html.replace("__IMG_RESULTS__", img_results)
        .replace("__IMG_CONFUSION__", img_confusion)
        .replace("__IMG_F1__", img_f1)
        .replace("__IMG_INTERFACE__", img_interface)
    )
    return html


def main():
    print("Gerando HTML do relatório...")
    html_content = build_html()
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML salvo em: {HTML_OUTPUT}")

    # Localizar o executável do Edge para compilar o PDF
    edge_paths = [
        Path(r"C:\Program Files (x86)\Microsoft\EdgeCore\155.0.4283.45\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\EdgeCore\154.0.4258.62\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    ]
    edge_exe = None
    for p in edge_paths:
        if p.exists():
            edge_exe = p
            break

    if not edge_exe:
        # Busca recursiva se não estiver nos locais padrão
        matches = list(Path(r"C:\Program Files (x86)\Microsoft").glob("**/msedge.exe"))
        if matches:
            edge_exe = matches[0]

    if not edge_exe:
        print("Aviso: Executável do Edge não encontrado diretamente. O arquivo HTML foi gerado com sucesso!")
        return

    print(f"Compilando PDF usando Microsoft Edge ({edge_exe})...")
    cmd = [
        str(edge_exe),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_OUTPUT}",
        str(HTML_OUTPUT),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if PDF_OUTPUT.exists() and PDF_OUTPUT.stat().st_size > 1000:
        print(f"Sucesso! Relatório em PDF gerado em: {PDF_OUTPUT}")
        print(f"Tamanho do arquivo: {PDF_OUTPUT.stat().st_size / 1024:.1f} KB")
        # Também criar cópia dentro de docs/
        copy_dest = DOCS_DIR / "Entrega_Parcial_BioCiclo_IA.pdf"
        import shutil
        shutil.copy2(PDF_OUTPUT, copy_dest)
        print(f"Cópia salva em: {copy_dest}")
    else:
        print(f"Erro ao compilar PDF: {result.stderr}")


if __name__ == "__main__":
    main()
