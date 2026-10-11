"""
Script de Avaliação e Métricas do Modelo YOLO
Calcula Precisão, Recall, mAP@50, mAP@50:95 e Matriz de Confusão
"""

import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_MODEL = PROJECT_ROOT / "models" / "weights" / "best.pt"
DEFAULT_DATA_YAML = PROJECT_ROOT / "data" / "garbage-classification-3" / "data.yaml"

def evaluate(
    model_path: Path = DEFAULT_MODEL,
    data_yaml: Path = DEFAULT_DATA_YAML,
    split: str = "val",
):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("Erro: A biblioteca 'ultralytics' não está instalada.")
        return

    if not Path(model_path).exists():
        print(f"[ERRO] Pesos do modelo não encontrados em: {model_path}")
        return

    print("=" * 70)
    print(" AVALIAÇÃO DE DESEMPENHO - BIOCICLO IA")
    print(f" - Modelo: {model_path}")
    print(f" - Dataset: {data_yaml}")
    print(f" - Split: {split}")
    print("=" * 70)

    model = YOLO(str(model_path))
    metrics = model.val(
        data=str(data_yaml),
        split=split,
        project=str(PROJECT_ROOT / "runs" / "val"),
        name="biociclo_eval",
        exist_ok=True,
    )

    print("\n" + "=" * 70)
    print(" RESULTADOS DAS MÉTRICAS")
    print("=" * 70)
    print(f" - Precisão (mAP50-95(B)): {metrics.box.map:.4f}")
    print(f" - mAP @ 0.50:            {metrics.box.map50:.4f}")
    print(f" - mAP @ 0.75:            {metrics.box.map75:.4f}")
    print(f" - Precisão Média (P):    {metrics.box.mp:.4f}")
    print(f" - Recall Médio (R):      {metrics.box.mr:.4f}")
    print("=" * 70)
    print(f"Gráficos, curvas PR e matriz de confusão salvos em: {PROJECT_ROOT / 'runs' / 'val' / 'biociclo_eval'}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Avaliação do modelo YOLO treinado")
    parser.add_argument("--model", type=str, default=str(DEFAULT_MODEL), help="Caminho do modelo best.pt")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_YAML), help="Caminho do data.yaml")
    parser.add_argument("--split", type=str, default="val", help="Split para avaliação (val ou test)")
    args = parser.parse_args()

    evaluate(model_path=Path(args.model), data_yaml=Path(args.data), split=args.split)
