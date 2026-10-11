"""
Script de Download e Preparação do Conjunto de Dados
Dataset Principal: GARBAGE CLASSIFICATION 3 (GC1) v2 - Roboflow Universe
Referência: https://universe.roboflow.com/material-identification/garbage-classification-3/dataset/2
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def download_garbage_classification_v2(api_key: str = None, destination: Path = DATA_DIR):
    """
    Realiza o download do dataset Garbage Classification 3 v2 (GC1) via Roboflow API
    em formato YOLOv8/YOLO11.
    """
    key = api_key or os.getenv("ROBOFLOW_API_KEY")
    if not key or key == "sua_chave_aqui":
        print("=" * 70)
        print(" [AVISO] Chave ROBOFLOW_API_KEY não configurada no arquivo .env!")
        print("=" * 70)
        print("Para baixar automaticamente o dataset oficial do projeto:")
        print("1. Crie uma conta gratuita em https://universe.roboflow.com")
        print("2. Obtenha sua API Key nas configurações do seu perfil Roboflow")
        print("3. Adicione ao arquivo .env na raiz do projeto: ROBOFLOW_API_KEY=sua_chave")
        print("4. Execute novamente: python -m src.data.download_dataset")
        print("\nOu faça o download manual:")
        print("Acesse: https://universe.roboflow.com/material-identification/garbage-classification-3/dataset/2")
        print("Clique em 'Download Dataset' -> Formato 'YOLOv8' ou 'YOLO11'")
        print(f"Extraia o arquivo .zip dentro de: {destination / 'garbage-classification-3'}")
        print("=" * 70)
        return False

    try:
        from roboflow import Roboflow
        print(f"Iniciando download do Garbage Classification 3 v2 para: {destination}")
        destination.mkdir(parents=True, exist_ok=True)
        rf = Roboflow(api_key=key)
        project = rf.workspace("material-identification").project("garbage-classification-3")
        version = project.version(2)
        dataset = version.download("yolov8", location=str(destination / "garbage-classification-3"))
        print("\nDownload concluído com sucesso!")
        print(f"Localização: {dataset.location}")
        return True
    except Exception as e:
        print(f"Erro ao baixar dataset via Roboflow: {e}")
        return False

if __name__ == "__main__":
    download_garbage_classification_v2()
