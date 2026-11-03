"""
Regras de Negócio, Padrão CONAMA e Destinação de Resíduos
Módulo responsável por mapear a classe detectada para o tipo de resíduo,
coletor CONAMA correspondente, exemplos regionais (Sergipe/Nordeste) e
a recomendação adequada de descarte/aproveitamento (BioCiclo Urbano - EMSURB).
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class DestinationAdvice:
    raw_class: str
    display_name: str
    waste_type: str            # 'Orgânico', 'Reciclável', 'Rejeito / Comum'
    destination: str           # ex: 'Compostagem (BioCiclo Urbano)'
    action_color: str          # Hex color para badges e barras
    guidance: str              # Instrução detalhada de manejo
    tips: List[str]            # Dicas práticas de separação
    is_uncertain: bool = False # Se a confiança ficou abaixo do limiar seguro
    warning_message: Optional[str] = None
    conama_bin: str = "Coletor Padrão"
    conama_color: str = "#2EA043"
    regional_note: str = ""


# Regras baseadas na Resolução CONAMA nº 275/2001 e no programa BioCiclo Urbano (Aracaju / EMSURB)
RULES_DATABASE: Dict[str, Dict[str, Any]] = {
    "BIODEGRADABLE": {
        "display_name": "Orgânico / Biodegradável",
        "waste_type": "Orgânico",
        "destination": "Compostagem (BioCiclo Urbano)",
        "action_color": "#10B981",  # Esmeralda vivo na UI
        "conama_bin": "Coletor Marrom — Resíduos Orgânicos",
        "conama_color": "#795548",
        "guidance": (
            "Encaminhar prioritariamente para as leiras de compostagem do programa BioCiclo Urbano (EMSURB) "
            "ou composteira doméstica/comunitária. A segregação na fonte transforma restos vegetais em composto "
            "orgânico rico em nutrientes para áreas verdes de Aracaju e agricultura familiar."
        ),
        "regional_note": (
            "Em feiras livres de Aracaju e na Orla da Atalaia, resíduos fibrosos como casca de coco verde "
            "e macaxeira devem ser separados de sacolas plásticas; o coco verde requer trituração mecânica prévia."
        ),
        "tips": [
            "Restos de frutas tropicais, verduras, coentro, cascas de macaxeira/inhame, cascas de ovos e borra de café são ideais para compostagem.",
            "Não misture sacolas plásticas comuns, embalagens de flocão/café ou metais junto ao material orgânico.",
            "Fibras duras (como coco verde e bagaço de cana) devem ser encaminhadas aos pontos da EMSURB com triturador orgânico.",
        ],
    },
    "ORGANIC": {
        "display_name": "Orgânico / Biodegradável",
        "waste_type": "Orgânico",
        "destination": "Compostagem (BioCiclo Urbano)",
        "action_color": "#10B981",
        "conama_bin": "Coletor Marrom — Resíduos Orgânicos",
        "conama_color": "#795548",
        "guidance": (
            "Direcionar para o programa BioCiclo Urbano (EMSURB) ou sistemas locais de compostagem orgânica."
        ),
        "regional_note": (
            "Alta disponibilidade em feiras livres e mercados municipais de Aracaju (Thales Ferraz e Albano Franco)."
        ),
        "tips": [
            "Cascas, restos de legumes, raízes e frutas são 100% aproveitáveis na compostagem.",
            "Mantenha o recipiente de orgânicos tampado e livre de contaminantes secos ou químicos.",
        ],
    },
    "PAPER": {
        "display_name": "Papel / Celulose",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#3B82F6",  # Azul
        "conama_bin": "Coletor Azul — Papel e Papelão",
        "conama_color": "#1E88E5",
        "guidance": (
            "Destinar à coleta seletiva seca ou PEVs para encaminhamento às cooperativas de reciclagem (ex: CARE em Aracaju). "
            "O papel limpo e seco pode ser reprocessado diversas vezes na cadeia produtiva."
        ),
        "regional_note": (
            "Atenção ao Viés Cultural: pacotes plásticos foscos de cuscuz/flocão ou café (ex: Maratá, Nordestino) "
            "podem parecer papel na foto devido à impressão gráfica, mas devem ir para o coletor de Plástico!"
        ),
        "tips": [
            "O papel deve estar seco e sem gordura. Guardanapos sujos, papel toalha engordurado e papel carbono vão para o Rejeito.",
            "Evite amassar folhas em bolas compactas; papéis empilhados ou dobrados otimizam a prensagem nas cooperativas.",
            "Verifique se o item não é uma embalagem plástica flexível laminada confundida pelo rótulo impresso.",
        ],
    },
    "CARDBOARD": {
        "display_name": "Papelão / Cartonado",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#D97706",  # Âmbar/Marrom claro
        "conama_bin": "Coletor Azul — Papel e Papelão",
        "conama_color": "#1E88E5",
        "guidance": (
            "Destinar à coleta seletiva seca ou entrega em PEVs (Pontos de Entrega Voluntária). "
            "Possui altíssima demanda e taxa de reaproveitamento nas cooperativas de catadores."
        ),
        "regional_note": (
            "Inclui caixas de transporte e embalagens cartonadas Longa Vida / Tetra Pak (ex: Leite Betânia, "
            "Natville, Camponesa e Sucos Maratá), que devem ser enxaguadas antes do descarte."
        ),
        "tips": [
            "Desmonte e achate as caixas de papelão e embalagens Tetra Pak para reduzir o volume no transporte.",
            "Para caixas de leite ou suco (Longa Vida), enxágue rapidamente o interior para evitar fermentação e mau odor.",
            "Retire restos de comida ou óleo: fundos de caixa de pizza engordurados não devem ir para a reciclagem de papel.",
        ],
    },
    "PLASTIC": {
        "display_name": "Plástico (PET / PP / Flexível)",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#EF4444",  # Vermelho
        "conama_bin": "Coletor Vermelho — Plásticos",
        "conama_color": "#E53935",
        "guidance": (
            "Destinar à coleta seletiva seca. Polímeros plásticos levam séculos para se degradar no ambiente, "
            "mas possuem alto valor de reciclagem mecânica quando limpos e separados da fração orgânica."
        ),
        "regional_note": (
            "Abrange garrafas PET (Guaraná, Cajuína São Geraldo), copinhos de água mineral de 200ml (Indaiá/Cristal — "
            "retire o lacre de alumínio!), potes de margarina (Deline/Qualy) e pacotes flexíveis de flocão/arroz."
        ),
        "tips": [
            "Passe uma água rápida (água de enxágue da louça) em potes de margarina, iogurte e garrafas para remover restos orgânicos.",
            "Em copinhos de água mineral de 200ml, destaque totalmente o lacre metálico superior (que vai para o Metal).",
            "Amasse garrafas PET e mantenha a tampinha rosqueada para evitar que se perca na triagem.",
        ],
    },
    "METAL": {
        "display_name": "Metal / Alumínio e Aço",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#F59E0B",  # Amarelo Ouro
        "conama_bin": "Coletor Amarelo — Metais",
        "conama_color": "#FDD835",
        "guidance": (
            "Destinar à coleta seletiva ou cooperativas de reciclagem. O alumínio e o aço são 100% recicláveis "
            "sem perda de propriedades físicas, economizando até 95% de energia em relação à extração primária."
        ),
        "regional_note": (
            "Latas de bebidas, latas de leite em pó (Ninho/Itambé), conservas (sardinha/milho), marmitas de alumínio "
            "limpas e lacres prateados de copinhos de água mineral."
        ),
        "tips": [
            "Em latas de conserva de aço, empurre a tampa serrilhada para dentro da lata para proteger os agentes de triagem.",
            "Esvazie completamente líquidos e enxágue restos de alimentos.",
            "Latas de aerossol, tintas ou solventes exigem logística reversa específica.",
        ],
    },
    "GLASS": {
        "display_name": "Vidro",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#06B6D4",  # Ciano/Verde-água
        "conama_bin": "Coletor Verde — Vidros",
        "conama_color": "#43A047",
        "guidance": (
            "Destinar à coleta seletiva de vidro ou PEVs específicos. O vidro é 100% reciclável infinitas vezes "
            "sem perda de qualidade ou pureza."
        ),
        "regional_note": (
            "Garrafas de bebidas (Cajuína em vidro, cervejas long neck, sucos de uva/caju), potes de conserva "
            "e frascos de alimentos."
        ),
        "tips": [
            "Se o vidro estiver quebrado, envolva em jornal ou coloque dentro de uma caixa de leite/garrafa PET cortada e identifique visivelmente: 'CUIDADO: VIDRO QUEBRADO'.",
            "Retire tampas plásticas ou metálicas e descarte-as nos seus respectivos coletores.",
            "Espelhos, cerâmicas, porcelanas e lâmpadas NÃO devem ser misturados ao vidro reciclável comum.",
        ],
    },
    "CLOTH": {
        "display_name": "Tecido / Têxtil",
        "waste_type": "Rejeito / Reuso",
        "destination": "Doação, Reuso ou Coleta Convencional",
        "action_color": "#A855F7",  # Roxo
        "conama_bin": "Doação Social / Coletor Cinza",
        "conama_color": "#8E24AA",
        "guidance": (
            "Se estiver íntegro e limpo, encaminhe para doação comunitária ou projetos de artesanato/estopa. "
            "Panos contaminados com óleo ou graxa devem ir para o descarte convencional."
        ),
        "regional_note": (
            "Sacos de juta/ráfia usados em feiras livres de Sergipe para transporte de farinha, cebola e batata "
            "podem ser higienizados e reutilizados diversas vezes pelos feirantes."
        ),
        "tips": [
            "Roupas e calçados em bom estado devem ser higienizados e destinados a ações solidárias.",
            "Sacos de ráfia e algodão de feiras livres têm alto potencial de reuso direto.",
        ],
    },
    "TRASH": {
        "display_name": "Rejeito / Não Reciclável",
        "waste_type": "Rejeito",
        "destination": "Coleta Convencional / Aterro Sanitário",
        "action_color": "#64748B",  # Cinza Azulado
        "conama_bin": "Coletor Cinza — Rejeito / Não Reciclável",
        "conama_color": "#757575",
        "guidance": (
            "Destinar à coleta pública domiciliar convencional para encaminhamento a aterro sanitário licenciado. "
            "Compreende materiais que não possuem viabilidade técnica de reciclagem nem de compostagem."
        ),
        "regional_note": (
            "Manter estritamente separado das bombonas do BioCiclo Urbano e dos sacos de coleta seletiva "
            "para evitar a contaminação de lotes inteiros."
        ),
        "tips": [
            "Resíduos sanitários, esponjas de louça usadas, etiquetas adesivas e embalagens severamente contaminadas entram aqui.",
            "Acondicione em sacos resistentes e bem fechados nos horários regulares de coleta da EMSURB.",
        ],
    },
}


def get_destination_advice(
    class_name: str,
    confidence: float,
    confidence_threshold: float = 0.50
) -> DestinationAdvice:
    """
    Avalia a classe predita e o nível de confiança, retornando a orientação de destinação.
    Caso a confiança seja inferior ao threshold de segurança (ou < 50%), ativa a flag
    de incerteza recomendando revisão humana ou nova fotografia.
    """
    normalized_key = class_name.strip().upper()
    rule = RULES_DATABASE.get(normalized_key, RULES_DATABASE["TRASH"])

    safety_floor = max(confidence_threshold, 0.45)
    is_uncertain = confidence < safety_floor
    warning_msg = None

    if is_uncertain:
        warning_msg = (
            f"A confiança da detecção ({confidence * 100:.1f}%) está em faixa de atenção "
            f"(abaixo de {safety_floor * 100:.0f}%). Em embalagens de marcas regionais ou sob sombras, "
            f"verifique visualmente o símbolo de reciclagem do rótulo ou capture uma nova foto centralizada."
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
        warning_message=warning_msg,
        conama_bin=rule.get("conama_bin", "Coletor Padrão"),
        conama_color=rule.get("conama_color", rule["action_color"]),
        regional_note=rule.get("regional_note", ""),
    )
