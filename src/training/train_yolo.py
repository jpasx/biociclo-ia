"""
Script de Treinamento (Fine-Tuning) do Modelo YOLO com Rebalanceamento de Classes
Disciplina: Fundamentos da Inteligência Artificial - UFS
Contexto: Projeto BioCiclo Urbano (Aracaju / EMSURB)
"""

import argparse
from pathlib import Path
import shutil
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATA_YAML = PROJECT_ROOT / "data" / "garbage-classification-3" / "data.yaml"
WEIGHTS_DIR = PROJECT_ROOT / "models" / "weights"


def rebalance_gc1_labels(data_yaml: Path, max_boxes_per_crowded_bio: int = 8) -> None:
    """
    Corrige o desbalanceamento extremo de instâncias da classe 0 (BIODEGRADABLE)
    no dataset Garbage Classification 3 (GC1), onde fotos de pilhas de maçãs/folhas
    possuem 30 a 60 caixas por imagem e dominam o gradiente de classificação.
    """
    train_labels_dir = data_yaml.parent / "train" / "labels"
    if not train_labels_dir.exists():
        return

    before_counts: Counter = Counter()
    after_counts: Counter = Counter()
    modified_files = 0

    for label_file in train_labels_dir.glob("*.txt"):
        try:
            lines = [ln.strip() for ln in label_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
        except Exception:
            continue

        if not lines:
            continue

        parsed = []
        for ln in lines:
            parts = ln.split()
            if len(parts) >= 5:
                cls_id = int(parts[0])
                before_counts[cls_id] += 1
                parsed.append((cls_id, parts, ln))

        # Se a imagem contém massivamente a classe 0 (BIODEGRADABLE) com dezenas de caixas,
        # mantemos apenas as N maiores caixas de BIODEGRADABLE e preservamos 100% das demais classes
        bio_lines = [item for item in parsed if item[0] == 0]
        other_lines = [item for item in parsed if item[0] != 0]

        if len(bio_lines) > max_boxes_per_crowded_bio:
            # Ordenar por maior área da bounding box (w * h)
            bio_lines.sort(
                key=lambda item: float(item[1][3]) * float(item[1][4]),
                reverse=True,
            )
            kept_bio = bio_lines[:max_boxes_per_crowded_bio]
            final_items = kept_bio + other_lines
            label_file.write_text(
                "\n".join(item[2] for item in final_items) + "\n",
                encoding="utf-8",
            )
            modified_files += 1
        else:
            final_items = parsed

        for cls_id, _, _ in final_items:
            after_counts[cls_id] += 1

    print("=" * 70)
    print(" REBALANCEAMENTO DE INSTÂNCIAS DO DATASET (ANTI-VIÉS GC1)")
    print(f" - Arquivos de anotação otimizados: {modified_files}")
    print(f" - Instâncias classe 0 (BIODEGRADABLE): {before_counts[0]} -> {after_counts[0]}")
    print(f" - Instâncias demais classes preservadas: {sum(v for k, v in after_counts.items() if k != 0)}")
    print("=" * 70)


def train(
    data_yaml: Path = DEFAULT_DATA_YAML,
    base_model: str = "yolo11s.pt",
    epochs: int = 50,
    batch: int = 16,
    imgsz: int = 640,
    patience: int = 15,
    device: str = "0",  # ou "cpu"
    fraction: float = 1.0,
    workers: int = 4,
    val: bool = True,
    rebalance: bool = True,
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

    if rebalance:
        rebalance_gc1_labels(Path(data_yaml))

    print("=" * 70)
    print(" INICIANDO TREINAMENTO YOLO CALIBRADO - BIOCICLO IA")
    print(f" - Modelo Base: {base_model}")
    print(f" - Arquivo de Dados: {data_yaml}")
    print(f" - Épocas: {epochs} (cos_lr=True, close_mosaic=10, cls=1.5)")
    print(f" - Batch Size: {batch}")
    print(f" - Dimensão Imagem: {imgsz}x{imgsz}")
    print(f" - Dispositivo: {device}")
    print("=" * 70)

    # Carrega modelo pré-treinado
    model = YOLO(base_model)

    # Treinamento com transfer learning e hiperparâmetros otimizados para discriminação de materiais
    model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        patience=patience,
        device=device,
        fraction=fraction,
        workers=workers,
        val=val,
        cos_lr=True,
        close_mosaic=10,
        cls=1.5,
        dropout=0.1,
        project=str(PROJECT_ROOT / "runs" / "train"),
        name="biociclo_yolo",
        exist_ok=True,
    )

    # Copiar o melhor modelo resultante para models/weights/best.pt
    WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    best_pt = PROJECT_ROOT / "runs" / "train" / "biociclo_yolo" / "weights" / "best.pt"
    last_pt = PROJECT_ROOT / "runs" / "train" / "biociclo_yolo" / "weights" / "last.pt"
    source_pt = best_pt if best_pt.exists() else last_pt

    if source_pt.exists():
        target_path = WEIGHTS_DIR / "best.pt"
        shutil.copy(source_pt, target_path)
        print("\n" + "=" * 70)
        print("[SUCESSO] Treinamento concluído com êxito!")
        print(f"Melhor modelo exportado para: {target_path}")
        print("=" * 70)
    else:
        print(f"Treinamento finalizado. Verifique os resultados em: {PROJECT_ROOT / 'runs' / 'train'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Treinamento do YOLO para Classificação de Resíduos")
    parser.add_argument("--data", type=str, default=str(DEFAULT_DATA_YAML), help="Caminho para o data.yaml")
    parser.add_argument("--model", type=str, default="yolo11s.pt", help="Modelo base (yolo11s.pt, yolo11n.pt, etc)")
    parser.add_argument("--epochs", type=int, default=50, help="Número de épocas")
    parser.add_argument("--batch", type=int, default=16, help="Tamanho do lote (batch size)")
    parser.add_argument("--imgsz", type=int, default=640, help="Tamanho das imagens")
    parser.add_argument("--device", type=str, default="cpu", help="'cpu' ou ID da GPU (ex: '0')")
    parser.add_argument("--fraction", type=float, default=1.0, help="Fração do dataset a utilizar (ex: 0.1 para 10%)")
    parser.add_argument("--workers", type=int, default=4, help="Número de workers do dataloader")
    parser.add_argument("--no-val", action="store_true", help="Pular validação por época para acelerar treino no CPU")
    parser.add_argument("--no-rebalance", action="store_true", help="Desativar rebalanceamento automático da classe 0")
    args = parser.parse_args()

    train(
        data_yaml=Path(args.data),
        base_model=args.model,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        device=args.device,
        fraction=args.fraction,
        workers=args.workers,
        val=not args.no_val,
        rebalance=not args.no_rebalance,
    )
