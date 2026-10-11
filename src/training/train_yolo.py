"""
Script de Treinamento (Fine-Tuning) do Modelo YOLO
Disciplina: Fundamentos da Inteligência Artificial - UFS
Contexto: Projeto BioCiclo Urbano
"""

import argparse
from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_YAML = PROJECT_ROOT / "data" / "garbage-classification-3" / "data.yaml"
WEIGHTS_DIR = PROJECT_ROOT / "models" / "weights"

def train(
    data_yaml: Path = DEFAULT_DATA_YAML,
    base_model: str = "yolo11n.pt",
    epochs: int = 50,
    batch: int = 16,
    imgsz: int = 640,
    patience: int = 15,
    device: str = "0",  # ou "cpu"
):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Erro: A biblioteca 'ultralytics' não está instalada.")
        print("Instale com: pip install ultralytics")
        return

    if not Path(data_yaml).exists():
        print("=" * 70)
        print(f"[ERRO] Arquivo de dados não encontrado em: {data_yaml}")
        print("=" * 70)
        print("Antes de treinar, certifique-se de baixar o dataset:")
        print("  python -m src.data.download_dataset")
        print("Ou indique o caminho correto com o parâmetro --data")
        print("=" * 70)
        return

    print("=" * 70)
    print(" INICIANDO TREINAMENTO YOLO - BIOCICLO IA")
    print(f" - Modelo Base: {base_model}")
    print(f" - Arquivo de Dados: {data_yaml}")
    print(f" - Épocas: {epochs}")
    print(f" - Batch Size: {batch}")
    print(f" - Dimensão Imagem: {imgsz}x{imgsz}")
    print(f" - Dispositivo: {device}")
    print("=" * 70)

    # Carrega modelo pré-treinado
    model = YOLO(base_model)

    # Treinamento com transfer learning
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        patience=patience,
        device=device,
        project=str(PROJECT_ROOT / "runs" / "train"),
        name="biociclo_yolo",
        exist_ok=True,
    )

    # Copiar o melhor modelo resultante para models/weights/best.pt
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    best_pt = PROJECT_ROOT / "runs" / "train" / "biociclo_yolo" / "weights" / "best.pt"
    if best_pt.exists():
        target_path = WEIGHTS_DIR / "best.pt"
        shutil.copy(best_pt, target_path)
        print("\n" + "=" * 70)
        print(f"[SUCESSO] Treinamento concluído com êxito!")
        print(f"Melhor modelo exportado para: {target_path}")
        print("=" * 70)
    else:
        print(f"Treinamento finalizado. Verifique os resultados em: {PROJECT_ROOT / 'runs' / 'train'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treinamento do YOLO para Classificação de Resíduos")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_YAML), help="Caminho para o data.yaml")
    parser.add_argument("--model", type=str, default="yolo11n.pt", help="Modelo base (yolo11n.pt, yolov8n.pt, etc)")
    parser.add_argument("--epochs", type=int, default=50, help="Número de épocas")
    parser.add_argument("--batch", type=int, default=16, help="Tamanho do lote (batch size)")
    parser.add_argument("--imgsz", type=int, default=640, help="Tamanho das imagens")
    parser.add_argument("--device", type=str, default="cpu", help="'cpu' ou ID da GPU (ex: '0')")
    args = parser.parse_args()

    train(
        data_yaml=Path(args.data),
        base_model=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
    )
