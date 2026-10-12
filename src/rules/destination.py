"""
Regras de Negócio e Destinação de Resíduos
Módulo responsável por mapear a classe detectada para o tipo de resíduo
e a recomendação adequada de descarte/aproveitamento (ex: BioCiclo Urbano).
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DestinationAdvice:
    raw_class: str
    display_name: str
    waste_type: str            # 'Orgânico', 'Reciclável', 'Rejeito / Comum'
    destination: str           # ex: 'Compostagem (BioCiclo Urbano)'
    action_color: str          # Hex color para badges
    guidance: str              # Instrução detalhada de manejo
    tips: list[str]            # Dicas práticas de separação
    is_uncertain: bool = False # Se a confiança ficou abaixo do limiar seguro
    warning_message: Optional[str] = None


# Regras baseadas na Tabela 1 do projeto e no programa BioCiclo Urbano
RULES_DATABASE: Dict[str, Dict[str, Any]] = {
    "BIODEGRADABLE": {
        "display_name": "Orgânico / Biodegradável",
        "waste_type": "Orgânico",
        "destination": "Compostagem (BioCiclo Urbano)",
        "action_color": "#2E7D32",  # Verde
        "guidance": (
            "Encaminhar prioritariamente para os processos de compostagem do BioCiclo Urbano "
            "ou composteira local. Resíduos orgânicos transformam-se em adubo rico em nutrientes "
            "e reduzem a emissão de gases de efeito estufa nos aterros."
        ),
        "tips": [
            "Restos de frutas, verduras, cascas de ovos, borra de café e podas são ideais para compostagem.",
            "Não misture sacolas plásticas, embalagens ou metais com o material orgânico.",
            "Evite misturar grandes volumes de carnes, laticínios ou óleos em compostagem simples sem tratamento adequado.",
        ],
    },
    "ORGANIC": {
        "display_name": "Orgânico / Biodegradável",
        "waste_type": "Orgânico",
        "destination": "Compostagem (BioCiclo Urbano)",
        "action_color": "#2E7D32",
        "guidance": (
            "Direcionar para o programa BioCiclo Urbano ou sistemas de compostagem orgânica."
        ),
        "tips": [
            "Cascas, restos de legumes e frutas são 100% aproveitáveis.",
            "Mantenha o recipiente de orgânicos tampado e separado de contaminantes recicláveis.",
        ],
    },
    "PAPER": {
        "display_name": "Papel",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#1E88E5",  # Azul
        "guidance": (
            "Destinar à coleta seletiva para cooperativas de reciclagem. O papel limpo e seco pode ser reciclado várias vezes."
        ),
        "tips": [
            "O papel deve estar limpo e seco. Papéis engordurados (guardanapos usados, caixas de pizza com óleo) devem ir para o lixo comum.",
            "Não amasse excessivamente se possível; folhas dobradas facilitam a triagem manual nas cooperativas.",
        ],
    },
    "CARDBOARD": {
        "display_name": "Papelão",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#8D6E63",  # Marrom
        "guidance": (
            "Destinar à coleta seletiva ou entrega em PEVs (Pontos de Entrega Voluntária). Alta taxa de reaproveitamento industrial."
        ),
        "tips": [
            "Desmonte as caixas de papelão para otimizar espaço de armazenamento e transporte.",
            "Retire fitas adesivas excessivas e grampos grossos sempre que possível.",
            "Papelão molhado ou contaminado com graxa perde o valor de reciclagem.",
        ],
    },
    "PLASTIC": {
        "display_name": "Plástico",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#E53935",  # Vermelho
        "guidance": (
            "Destinar à coleta seletiva. O plástico leva centenas de anos para se decompor na natureza se descartado incorretamente."
        ),
        "tips": [
            "Enxágue rapidamente embalagens para remover resíduos orgânicos líquidos ou pastosos.",
            "Amasse garrafas PET para reduzir o volume ocupado.",
            "Tampinhas plásticas também são recicláveis e muito valorizadas por projetos sociais.",
        ],
    },
    "METAL": {
        "display_name": "Metal / Alumínio",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#F9A825",  # Amarelo
        "guidance": (
            "Destinar à coleta seletiva ou cooperativas. Latas de alumínio e metais possuem altíssimo índice de reciclabilidade no Brasil."
        ),
        "tips": [
            "Pressione as tampas para dentro de latas pontiagudas para evitar acidentes com catadores.",
            "Retire restos de alimentos antes de descartar.",
            "Latas de tinta ou produtos químicos necessitam de descarte especial ou logística reversa.",
        ],
    },
    "GLASS": {
        "display_name": "Vidro",
        "waste_type": "Reciclável",
        "destination": "Coleta Seletiva / Reciclagem",
        "action_color": "#00897B",  # Verde água/Ciano
        "guidance": (
            "Destinar à coleta seletiva de vidro ou PEVs específicos. O vidro é 100% reciclável infinitas vezes."
        ),
        "tips": [
            "Em caso de vidros quebrados, embale em caixas de leite/papelão ou garrafas PET cortadas e identifique como 'CUIDADO: VIDRO QUEBRADO' para proteger os coletores.",
            "Espelhos, cerâmicas e lâmpadas NÃO vão para a reciclagem comum de vidro.",
        ],
    },
    "CLOTH": {
        "display_name": "Tecido / Têxtil",
        "waste_type": "Rejeito / Reuso",
        "destination": "Doação ou Coleta Convencional",
        "action_color": "#8E24AA",  # Roxo
        "guidance": (
            "Se estiver em bom estado, direcione para doação ou bancos de roupas. Retalhos danificados devem ser avaliados para artesanato ou descarte comum."
        ),
        "tips": [
            "Roupas utilizáveis devem ser lavadas e doadas para campanhas comunitárias.",
            "Retalhos industriais limpos podem ser destinados a logística reversa têxtil.",
        ],
    },
    "TRASH": {
        "display_name": "Rejeito / Não Reciclável",
        "waste_type": "Rejeito",
        "destination": "Coleta Convencional / Aterro Sanitário",
        "action_color": "#616161",  # Cinza
        "guidance": (
            "Destinar à coleta convencional pública para encaminhamento a aterro sanitário licenciado. Materiais não recicláveis nem compostáveis."
        ),
        "tips": [
            "Itens higiênicos, fitas adesivas sujas e resíduos contaminados entram nesta categoria.",
            "Mantenha em sacos resistentes e bem fechados.",
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
    Caso a confiança seja inferior ao threshold, ativa a flag de incerteza recomendando
    uma nova imagem em vez de tomar decisão precipitada.
    """
    normalized_key = class_name.strip().upper()
    rule = RULES_DATABASE.get(normalized_key, RULES_DATABASE.get("TRASH"))

    is_uncertain = confidence < confidence_threshold
    warning_msg = None

    if is_uncertain:
        warning_msg = (
            f"A confiança da detecção ({confidence * 100:.1f}%) está abaixo do limiar de segurança "
            f"({confidence_threshold * 100:.1f}%). Recomenda-se tirar uma nova fotografia com melhor "
            f"iluminação, enquadramento centralizado e sem reflexos antes de efetuar a destinação final."
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
    )
