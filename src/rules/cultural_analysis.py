"""
Módulo de Análise Cultural do Dataset e Compatibilidade com Embalagens Regionais
Contexto: Aracaju / Sergipe / Nordeste Brasileiro (Programa BioCiclo Urbano - EMSURB)
Disciplina: Fundamentos da Inteligência Artificial - DComp / UFS

Avalia o fenômeno de Domain Shift (Viés Cultural e Geográfico) ao aplicar modelos
treinados na base internacional Garbage Classification 3 (GC1) sobre resíduos e
embalagens de marcas típicas do mercado regional sergipano e nordestino.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class RegionalItemProfile:
    id: str
    name: str
    brands_examples: str
    category_region: str          # Ex: 'Embalagem Flexível Regional', 'Multicamada Cartonada', 'Orgânico de Feira Livre'
    expected_class: str           # Classe correta no sistema (PLASTIC, CARDBOARD, BIODEGRADABLE, etc.)
    expected_display: str
    common_model_prediction: str  # O que o modelo estrangeiro costuma prever
    compatibility_level: str      # 'Alta', 'Média', 'Baixa'
    compatibility_score: int      # 0 a 100 (estimativa técnica de generalização zero-shot)
    cultural_gap_reason: str      # Explicação técnica e cultural do comportamento da IA
    local_disposal_rule: str      # Regra específica para Aracaju / EMSURB / Cooperativas (ex: CARE)
    recommended_fix: str          # Como mitigar no modelo/sistema


# ==============================================================================
# EIXOS DE VIÉS CULTURAL DO DATASET (GARBAGE CLASSIFICATION 3 - GC1)
# ==============================================================================
CULTURAL_BIAS_AXES: List[Dict[str, str]] = [
    {
        "title": "1. Predominância de Embalagens Rígidas (EUA/Europa) vs. Flexíveis (Nordeste/Brasil)",
        "tag": "Viés Industrial e Tipográfico",
        "color": "#F59E0B",
        "description": (
            "Datasets internacionais (como GC1, TrashNet e TACO) foram coletados majoritariamente nos "
            "Estados Unidos e na Europa, onde predominam embalagens rígidas padronizadas (garrafas HDPE de "
            "galão de leite, potes rígidos e latas norte-americanas). No consumo doméstico de Sergipe e do "
            "Nordeste, há altíssima presença de plásticos flexíveis laminados (BOPP/PEBD) com forte impressão "
            "gráfica — como pacotes de flocão de milho (cuscuz), café a vácuo/almofada, leite em saco e "
            "biscoitos. Devido ao formato retangular achatado e à textura impressa sem transparência, o modelo "
            "estrangeiro frequentemente os confunde com Papel (PAPER) ou Papelão (CARDBOARD)."
        ),
    },
    {
        "title": "2. Recipientes Exclusivos da Cultura de Consumo Brasileira",
        "tag": "Geometria e Materiais Híbridos",
        "color": "#3B82F6",
        "description": (
            "O copinho plástico termoformado de água mineral de 200ml com lacre de alumínio (muito comum em "
            "Aracaju em marcas como Indaiá e Cristal) quase não existe em bases de dados estrangeiras. Além "
            "disso, embalagens cartonadas assépticas (Tetra Pak — Leite Betânia, Natville, Sucos Maratá) têm "
            "geometria idêntica a caixas de papelão (CARDBOARD), mas são compósitos multicamadas (75% papel, "
            "20% polietileno e 5% alumínio) que exigem linha de reciclagem separada do papelão ondulado comum."
        ),
    },
    {
        "title": "3. Biomassa Tropical de Feiras Livres vs. Frutas de Clima Temperado",
        "tag": "Viés Botânico e Alimentar (BioCiclo Urbano)",
        "color": "#10B981",
        "description": (
            "Na classe BIODEGRADABLE do dataset GC1, predominam maçãs vermelhas, peras, morangos e folhas de "
            "outono de clima temperado. Já nas feiras livres de Aracaju atendidas pela EMSURB e na Orla da "
            "Atalaia, os principais resíduos orgânicos são casca de coco verde, macaxeira (mandioca), inhame, "
            "jaca, manga, maracujá, coentro, bagaço de cana e folha de bananeira. O coco verde seco/marrom "
            "e a casca de macaxeira terrosa costumam ser confundidos pelo modelo com Papelão (CARDBOARD) "
            "pela textura fibrosa marrom, enquanto objetos com dezenas de instâncias geram super-predição."
        ),
    },
    {
        "title": "4. Desbalanceamento de Densidade de Anotações no GC1",
        "tag": "Viés de Anotação (Dataset Engineering)",
        "color": "#EF4444",
        "description": (
            "No dataset Garbage Classification 3, imagens da classe BIODEGRADABLE frequentemente contêm "
            "dezenas de caixas delimitadoras (30 a 50 maçãs, folhas ou restos por foto), enquanto imagens de "
            "PLASTIC ou GLASS possuem apenas 1 ou 2 objetos isolados. Sem rebalanceamento de instâncias e "
            "calibração de limiar, a rede neural desenvolve um forte prior para chutar 'Orgânico' diante de "
            "qualquer textura complexa ou rótulo colorido de marcas regionais."
        ),
    },
]


# ==============================================================================
# MATRIZ DE COMPATIBILIDADE COM MARCAS E RESÍDUOS DA NOSSA REGIÃO (SE / NE)
# ==============================================================================
REGIONAL_BRANDS_MATRIX: List[RegionalItemProfile] = [
    RegionalItemProfile(
        id="flocao_marata",
        name="Pacote de Flocão de Milho / Cuscuz (500g)",
        brands_examples="Maratá, Nordestino, Coringa, Vitamilho, Sinhá",
        category_region="Embalagem Plástica Flexível",
        expected_class="PLASTIC",
        expected_display="Plástico (Filme BOPP / PEBD)",
        common_model_prediction="PAPER ou BIODEGRADABLE (Confusão por rótulo amarelo/impresso)",
        compatibility_level="Baixa",
        compatibility_score=38,
        cultural_gap_reason=(
            "O pacote de cuscuz é um filme plástico flexível opaco (amarelo/vermelho) com grande área "
            "tipográfica. Como o dataset GC1 associa transparência e brilho cilíndrico a PLASTIC (garrafas PET) "
            "e superfícies foscas impressas a PAPER, o modelo tende a errar a classe material."
        ),
        local_disposal_rule=(
            "Coleta Seletiva Seca (Lixeira Vermelha / Cooperativas CARE Aracaju). Sacudir restos secos de "
            "farinha/flocão antes de descartar para não atrair vetores nem contaminar o fardo plástico."
        ),
        recommended_fix=(
            "Incluir ~150 fotos de embalagens flexíveis brasileiras (fardos de flocão, arroz, feijão e biscoito) "
            "rotuladas como PLASTIC no fine-tuning regional."
        ),
    ),
    RegionalItemProfile(
        id="cafe_marata",
        name="Embalagem de Café Torrado e Moído (Vácuo / Almofada)",
        brands_examples="Café Maratá, São Braz, Santa Clara, Pilão",
        category_region="Embalagem Laminada / Metalizada",
        expected_class="PLASTIC",
        expected_display="Plástico Laminado / Rejeito",
        common_model_prediction="CARDBOARD ou PAPER (Formato de tijolo retangular)",
        compatibility_level="Baixa",
        compatibility_score=35,
        cultural_gap_reason=(
            "O pacote de café a vácuo ('tijolinho') tem quinas retas rígidas que imitam perfeitamente uma "
            "caixa de papelão ou maço de papel no detector geométrico do YOLO, enquanto o pacote almofada "
            "possui filme metalizado interno ausente no dataset original."
        ),
        local_disposal_rule=(
            "A borra de café vai 100% para a Compostagem (BioCiclo Urbano)! Já a embalagem vazia laminada "
            "deve ser limpa e encaminhada à coleta seletiva (plástico misto) ou coleta convencional caso a "
            "cooperativa local não processe BOPP metalizado."
        ),
        recommended_fix=(
            "Aumentar amostras de pacotes retangulares metalizados/laminados e separar visualmente a "
            "orientação da borra de café (orgânico) da embalagem externa."
        ),
    ),
    RegionalItemProfile(
        id="leite_betania_tetrapak",
        name="Caixa Longa Vida (Tetra Pak — Leite, Suco e Condensado)",
        brands_examples="Betânia, Natville (SE), Camponesa, Sucos Maratá, Piracanjuba",
        category_region="Embalagem Cartonada Multicamada",
        expected_class="CARDBOARD",
        expected_display="Papelão / Cartonado Multicamada",
        common_model_prediction="CARDBOARD ou PAPER (Compatibilidade geométrica, mas ambiguidade material)",
        compatibility_level="Média",
        compatibility_score=72,
        cultural_gap_reason=(
            "O modelo reconhece bem o formato prismático como CARDBOARD/PAPER, porém o dataset GC1 não "
            "distingue papelão ondulado puro de embalagem cartonada asséptica (papel + plástico PE + alumínio), "
            "muito presente nos laticínios sergipanos (Natville) e nordestinos (Betânia)."
        ),
        local_disposal_rule=(
            "Coleta Seletiva (Reciclável). Essencial enxaguar com um pouco de água para remover restos de "
            "leite/suco (que causam mau cheiro e fermentação) e achatar a caixa antes do descarte."
        ),
        recommended_fix=(
            "Manter mapeamento para Reciclável (Coleta Seletiva), adicionando regra explícita de enxágue de "
            "embalagens Tetra Pak no protocolo de manejo do sistema."
        ),
    ),
    RegionalItemProfile(
        id="copinho_agua_indaia",
        name="Copo Plástico de Água Mineral (200ml com Lacre Alumínio)",
        brands_examples="Indaiá, Cristal, São Lourenço, Dias D'Ávila",
        category_region="Plástico Termoformado + Lacre Metálico",
        expected_class="PLASTIC",
        expected_display="Plástico (PP) + Lacre de Alumínio",
        common_model_prediction="GLASS ou PLASTIC (Baixa confiança quando fotografado de topo)",
        compatibility_level="Média",
        compatibility_score=58,
        cultural_gap_reason=(
            "Formato extremamente típico do Brasil/Nordeste. Pela transparência estriada, o modelo às vezes "
            "confunde com vidro (GLASS), e quando fotografado por cima, o reflexo do lacre prateado de "
            "alumínio gera dúvida entre METAL e PLASTIC."
        ),
        local_disposal_rule=(
            "Coleta Seletiva: destacar completamente o lacre de alumínio (descartar junto aos Metais) e "
            "encaminhar o copinho vazio para os Plásticos (Polipropileno - PP)."
        ),
        recommended_fix=(
            "Incluir imagens do copo de 200ml em diferentes ângulos (lateral e topo com lacre) no dataset local."
        ),
    ),
    RegionalItemProfile(
        id="cajuina_guarana_pet",
        name="Garrafas PET e Vidro de Bebidas Regionais / Nacionais",
        brands_examples="Cajuína São Geraldo, Guaraná Antarctica, Frevo, Schin, Indaiá (1,5L/5L)",
        category_region="Embalagem Rígida Cilíndrica",
        expected_class="PLASTIC",
        expected_display="Plástico (PET) / Vidro",
        common_model_prediction="PLASTIC / GLASS (Reconhecimento consistente pelo gargalo e silhueta)",
        compatibility_level="Alta",
        compatibility_score=89,
        cultural_gap_reason=(
            "Garrafas PET (âmbar, verde ou transparente) e garrafas de vidro possuem geometria universal "
            "(gargalo, tampa roscável, brilho especular). Mesmo com rótulos de marcas nordestinas como "
            "São Geraldo ou Frevo, a rede convolucional generaliza com alta precisão."
        ),
        local_disposal_rule=(
            "Coleta Seletiva (Lixeira Vermelha para PET / Verde para Vidro). Esvaziar totalmente o líquido, "
            "amassar a PET longitudinalmente e manter a tampa rosqueada para não se perder na triagem."
        ),
        recommended_fix=(
            "Compatibilidade nativa alta; apenas garantir calibração de NMS para o rótulo impresso não gerar "
            "detecção secundária falsa de PAPER dentro da garrafa."
        ),
    ),
    RegionalItemProfile(
        id="lata_aluminio_bebidas",
        name="Latas de Alumínio e Aço (Bebidas e Conservas)",
        brands_examples="Skol, Brahma, Pitú (lata), Leite em Pó Ninho/Itambé, Sardinha Coqueiro",
        category_region="Embalagem Metálica Cilíndrica",
        expected_class="METAL",
        expected_display="Metal / Alumínio",
        common_model_prediction="METAL (Alta precisão no anel superior e brilho metálico)",
        compatibility_level="Alta",
        compatibility_score=86,
        cultural_gap_reason=(
            "A textura especular do alumínio/folha de flandres e o anel de abertura superior são feições "
            "fortes no dataset GC1. A mudança de litografia das marcas brasileiras tem baixo impacto negativo."
        ),
        local_disposal_rule=(
            "Coleta Seletiva (Lixeira Amarela). O Brasil recicla quase 100% das latas de alumínio; basta "
            "esvaziar o conteúdo. Para latas de aço de conservas, lavar e dobrar a tampa para dentro."
        ),
        recommended_fix="Manter limiar padrão; excelente transferência de aprendizado (Transfer Learning).",
    ),
    RegionalItemProfile(
        id="margarina_pote_pp",
        name="Potes de Margarina, Manteiga de Garrafa e Requeijão",
        brands_examples="Deline, Qualy, Primor, Potes de Doce/Sorvete Regionais",
        category_region="Plástico Rígido Opaco (PP)",
        expected_class="PLASTIC",
        expected_display="Plástico Rígido (Polipropileno)",
        common_model_prediction="PLASTIC ou CARDBOARD (Quando o pote tem cor creme/marrom)",
        compatibility_level="Média",
        compatibility_score=67,
        cultural_gap_reason=(
            "Potes plásticos opacos retangulares com tampas estampadas (muito comuns em margarinas vendidas "
            "no Nordeste como Deline) têm menos exemplos no GC1 do que garrafas transparentes, podendo perder "
            "confiança sob iluminação amarelada."
        ),
        local_disposal_rule=(
            "Coleta Seletiva (Plástico PP). Remover o excesso de gordura/margarina com guardanapo ou água "
            "da louça antes de enviar para a reciclagem."
        ),
        recommended_fix="Aumentar exemplos de potes plásticos opacos (PP) brancos e coloridos no dataset.",
    ),
    RegionalItemProfile(
        id="coco_verde_atalaia",
        name="Casca de Coco Verde (Inteiro ou Partido)",
        brands_examples="Feiras Livres de Aracaju, Orla de Atalaia, Mercados Municipais",
        category_region="Resíduo Orgânico Fibroso (Lignocelulósico)",
        expected_class="BIODEGRADABLE",
        expected_display="Orgânico / Biodegradável (Fibra Vegetal)",
        common_model_prediction="CARDBOARD ou BIODEGRADABLE (Confusão quando a casca está seca/marrom)",
        compatibility_level="Baixa",
        compatibility_score=42,
        cultural_gap_reason=(
            "O coco verde é um dos resíduos orgânicos mais volumosos de Aracaju, mas quase inexiste no "
            "dataset GC1 (EUA/Europa). Quando oxidado (marrom e fibroso), a textura lembra papelão rasgado "
            "(CARDBOARD), induzindo erro de classificação na rede sem fine-tuning local."
        ),
        local_disposal_rule=(
            "Compostagem Especializada (BioCiclo Urbano / EMSURB). Por ser rico em lignina e muito duro, "
            "exige trituração mecânica prévia nos pátios da EMSURB antes de compor as leiras de compostagem."
        ),
        recommended_fix=(
            "Fundamental adicionar imagens de coco verde (íntegro, cortado e oxidado) na classe BIODEGRADABLE "
            "para operação real em Aracaju."
        ),
    ),
    RegionalItemProfile(
        id="macaxeira_raizes_feira",
        name="Cascas de Macaxeira, Inhame, Batata-Doce e Abóbora",
        brands_examples="Feiras Livres de Aracaju, Mercado Thales Ferraz e Albano Franco",
        category_region="Resíduo Orgânico Amiláceo / Tubérculos",
        expected_class="BIODEGRADABLE",
        expected_display="Orgânico / Biodegradável",
        common_model_prediction="CARDBOARD ou BIODEGRADABLE (Textura terrosa marrom)",
        compatibility_level="Média",
        compatibility_score=55,
        cultural_gap_reason=(
            "Cascas de macaxeira (mandioca) e inhame possuem coloração marrom opaca e formato de tiras "
            "rígidas que se assemelham visualmente a pedaços de papelão ou madeira, diferindo das frutas "
            "coloridas (maçã, laranja, banana) do dataset estrangeiro."
        ),
        local_disposal_rule=(
            "Compostagem Prioritária (BioCiclo Urbano). Excelente fonte de carbono e energia para as leiras "
            "de compostagem quando misturada a resíduos verdes e folhosos."
        ),
        recommended_fix="Incluir fotos de bancas e restos de raízes/tubérculos tropicais no conjunto de treino.",
    ),
    RegionalItemProfile(
        id="hortifruti_tropical_aracaju",
        name="Frutas Tropicais e Folhosos (Manga, Maracujá, Jaca, Coentro, Banana)",
        brands_examples="Feiras Livres dos Bairros de Aracaju (EMSURB) e Cinturão Verde de SE",
        category_region="Resíduo Orgânico de Feira Livre",
        expected_class="BIODEGRADABLE",
        expected_display="Orgânico / Biodegradável",
        common_model_prediction="BIODEGRADABLE (Boa detecção por cor e textura orgânica)",
        compatibility_level="Alta",
        compatibility_score=85,
        cultural_gap_reason=(
            "Folhosos verdes (coentro, alface, couve, folha de bananeira) e frutas amarelas/alaranjadas "
            "(manga, banana, mamão, laranja) compartilham padrões cromáticos e texturais bem representados "
            "na classe BIODEGRADABLE do dataset GC1."
        ),
        local_disposal_rule=(
            "Compostagem Direta (BioCiclo Urbano / EMSURB). Segregar na fonte em bombonas exclusivas para "
            "orgânicos, sem sacolas plásticas comuns misturadas."
        ),
        recommended_fix="Apenas controlar o NMS para evitar excesso de caixas sobrepostas em pilhas de feira.",
    ),
]


def get_cultural_summary_metrics() -> Dict[str, Any]:
    """Calcula estatísticas agregadas da matriz de compatibilidade regional."""
    total = len(REGIONAL_BRANDS_MATRIX)
    high = sum(1 for item in REGIONAL_BRANDS_MATRIX if item.compatibility_level == "Alta")
    medium = sum(1 for item in REGIONAL_BRANDS_MATRIX if item.compatibility_level == "Média")
    low = sum(1 for item in REGIONAL_BRANDS_MATRIX if item.compatibility_level == "Baixa")
    avg_score = sum(item.compatibility_score for item in REGIONAL_BRANDS_MATRIX) / max(total, 1)

    return {
        "total_analyzed": total,
        "high_count": high,
        "medium_count": medium,
        "low_count": low,
        "avg_compatibility_score": round(avg_score, 1),
    }


def evaluate_regional_test_case(
    item_profile: RegionalItemProfile,
    detected_class: Optional[str],
    confidence: float,
) -> Dict[str, Any]:
    """
    Compara o resultado real obtido pelo detector em uma imagem de teste
    contra o perfil esperado de uma embalagem/resíduo regional.
    """
    if not detected_class:
        return {
            "status": "NÃO DETECTADO (Falso Negativo Cultural)",
            "status_color": "#EF4444",
            "is_match": False,
            "explanation": (
                f"O modelo não conseguiu delimitar '{item_profile.name}' acima do limiar de confiança. "
                f"Isso evidencia um gap de domínio (Domain Shift): {item_profile.cultural_gap_reason}"
            ),
        }

    det_upper = detected_class.strip().upper()
    exp_upper = item_profile.expected_class.strip().upper()

    if det_upper == exp_upper:
        return {
            "status": "COMPATÍVEL (Classificação Correta)",
            "status_color": "#10B981",
            "is_match": True,
            "explanation": (
                f"O modelo generalizou corretamente '{item_profile.name}' como {item_profile.expected_display} "
                f"com {confidence * 100:.1f}% de confiança, superando as diferenças de rotulagem regional."
            ),
        }

    return {
        "status": f"DIVERGÊNCIA POR VIÉS CULTURAL (Predito: {det_upper} | Real: {exp_upper})",
        "status_color": "#F59E0B",
        "is_match": False,
        "explanation": (
            f"O modelo classificou '{item_profile.name}' como '{det_upper}' ({confidence * 100:.1f}%), "
            f"mas o material real é '{exp_upper}' ({item_profile.expected_display}). "
            f"Causa técnica: {item_profile.cultural_gap_reason}"
        ),
    }
