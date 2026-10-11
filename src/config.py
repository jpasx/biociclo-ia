"""
Configurações Globais do Projeto BioCiclo IA
Sistema Inteligente para Classificação de Resíduos por Imagem
Universidade Federal de Sergipe (UFS) - DComp
"""

from pathlib import Path
import os

# Caminhos base do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"
MODELS_DIR = PROJECT_ROOT / "models"
WEIGHTS_DIR = MODELS_DIR / "weights"
RUNS_DIR = PROJECT_ROOT / "runs"

# Caminho padrão dos pesos treinados
DEFAULT_MODEL_WEIGHTS = WEIGHTS_DIR / "best.pt"
FALLBACK_PRETRAINED_MODEL = "yolo11n.pt"  # ou yolov8n.pt

# Thresholds de Confiança
DEFAULT_CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.50"))
DEFAULT_IOU_THRESHOLD = 0.45

# Classes do Dataset Principal: GARBAGE CLASSIFICATION 3 (GC1 - Roboflow Universe)
DATASET_CLASSES = [
    "BIODEGRADABLE",
    "CARDBOARD",
    "CLOTH",
    "GLASS",
    "METAL",
    "PAPER",
    "PLASTIC",
]

# Nomes amigáveis em Português
CLASS_TRANSLATIONS = {
    "BIODEGRADABLE": "Orgânico / Biodegradável",
    "CARDBOARD": "Papelão",
    "CLOTH": "Tecido / Têxtil",
    "GLASS": "Vidro",
    "METAL": "Metal",
    "PAPER": "Papel",
    "PLASTIC": "Plástico",
    "TRASH": "Rejeito (Lixo Comum)",
    "ORGANIC": "Orgânico / Biodegradável",
}

# Cores hexadecimais para visualização de cada classe
CLASS_COLORS = {
    "BIODEGRADABLE": "#2E7D32",  # Verde floresta
    "CARDBOARD": "#8D6E63",     # Marrom claro
    "CLOTH": "#AB47BC",         # Roxo
    "GLASS": "#00ACC1",         # Ciano
    "METAL": "#FFB300",         # Amarelo/Dourado
    "PAPER": "#1E88E5",         # Azul
    "PLASTIC": "#E53935",       # Vermelho
    "TRASH": "#757575",         # Cinza
    "ORGANIC": "#2E7D32",       # Verde
}
