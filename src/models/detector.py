"""
Módulo de Detecção de Resíduos com YOLO
Suporta carregamento do modelo treinado (best.pt) e modo fallback (demo/pré-treinado)
para que o projeto funcione imediatamente para a equipe mesmo antes do fine-tuning.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from src.config import (
    DEFAULT_MODEL_WEIGHTS,
    DEFAULT_CONFIDENCE_THRESHOLD,
    DEFAULT_IOU_THRESHOLD,
    CLASS_TRANSLATIONS,
    CLASS_COLORS,
)
from src.rules.destination import get_destination_advice, DestinationAdvice

# Mapeamento auxiliar caso seja usado um modelo YOLO COCO padrão pré-treinado
COCO_FALLBACK_MAPPING = {
    # Alimentos / orgânicos
    "banana": "BIODEGRADABLE",
    "apple": "BIODEGRADABLE",
    "sandwich": "BIODEGRADABLE",
    "orange": "BIODEGRADABLE",
    "broccoli": "BIODEGRADABLE",
    "carrot": "BIODEGRADABLE",
    "hot dog": "BIODEGRADABLE",
    "pizza": "BIODEGRADABLE",
    "donut": "BIODEGRADABLE",
    "cake": "BIODEGRADABLE",
    "potted plant": "BIODEGRADABLE",
    # Garrafas / Recicláveis
    "bottle": "PLASTIC",
    "cup": "PLASTIC",
    "wine glass": "GLASS",
    "fork": "METAL",
    "knife": "METAL",
    "spoon": "METAL",
    "bowl": "PLASTIC",
    "book": "PAPER",
    "backpack": "CLOTH",
    "handbag": "CLOTH",
    "tie": "CLOTH",
    "suitcase": "CLOTH",
    "cell phone": "METAL",
    "laptop": "METAL",
    "tv": "METAL",
}


class WasteDetectionResult:
    def __init__(
        self,
        box: List[float],  # [x1, y1, x2, y2]
        class_name: str,
        confidence: float,
        advice: DestinationAdvice,
    ):
        self.box = box
        self.class_name = class_name
        self.confidence = confidence
        self.advice = advice

    def to_dict(self) -> Dict[str, Any]:
        return {
            "box": self.box,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "display_name": self.advice.display_name,
            "waste_type": self.advice.waste_type,
            "destination": self.advice.destination,
            "is_uncertain": self.advice.is_uncertain,
            "warning_message": self.advice.warning_message,
        }


class WasteDetector:
    def __init__(
        self,
        model_path: Optional[str] = None,
        conf_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    ):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        self.is_custom_model = False
        self.model_name = ""

        # Verificar se ultralytics está disponível
        try:
            from ultralytics import YOLO
            self._yolo_class = YOLO
        except ImportError:
            self._yolo_class = None

        self._load_model(model_path)

    def _load_model(self, model_path: Optional[str]):
        if self._yolo_class is None:
            return

        # 1. Se foi passado caminho específico e existe
        if model_path and Path(model_path).exists():
            self.model = self._yolo_class(model_path)
            self.is_custom_model = True
            self.model_name = Path(model_path).name
            return

        # 2. Se existe o peso padrão treinado em models/weights/best.pt
        if DEFAULT_MODEL_WEIGHTS.exists():
            self.model = self._yolo_class(str(DEFAULT_MODEL_WEIGHTS))
            self.is_custom_model = True
            self.model_name = "best.pt (Modelo Treinado BioCiclo)"
            return

        # 3. Fallback: carregar modelo base YOLO para demonstração inicial
        try:
            # Tenta carregar yolo11n ou yolov8n
            self.model = self._yolo_class("yolo11n.pt")
            self.is_custom_model = False
            self.model_name = "YOLO11n (Modo Demonstração Pré-treinado)"
        except Exception:
            try:
                self.model = self._yolo_class("yolov8n.pt")
                self.is_custom_model = False
                self.model_name = "YOLOv8n (Modo Demonstração Pré-treinado)"
            except Exception as e:
                self.model = None
                self.model_name = f"Erro ao carregar modelo: {e}"

    def predict(
        self,
        image: Image.Image,
        conf_threshold: Optional[float] = None,
    ) -> Tuple[List[WasteDetectionResult], Optional[WasteDetectionResult]]:
        """
        Executa a predição na imagem.
        Retorna:
          - Lista de todas as detecções
          - Detecção principal (maior confiança ou maior área central)
        """
        threshold = conf_threshold if conf_threshold is not None else self.conf_threshold
        detections: List[WasteDetectionResult] = []

        if self.model is None:
            # Caso o modelo ainda não tenha pesos ou dependências
            return detections, None

        # Converter para array RGB
        img_np = np.array(image.convert("RGB"))
        results = self.model.predict(
            img_np,
            conf=threshold,
            iou=self.iou_threshold,
            verbose=False,
        )

        if not results or len(results) == 0:
            return detections, None

        first_res = results[0]
        boxes = first_res.boxes

        if boxes is None or len(boxes) == 0:
            return detections, None

        for box in boxes:
            coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            raw_name = first_res.names.get(cls_id, f"class_{cls_id}")

            # Se for modelo COCO pré-treinado, mapeamos a classe para o contexto do lixo
            if not self.is_custom_model:
                mapped_class = COCO_FALLBACK_MAPPING.get(raw_name.lower(), "TRASH")
            else:
                mapped_class = raw_name.upper()

            advice = get_destination_advice(mapped_class, conf, threshold)
            det = WasteDetectionResult(
                box=coords,
                class_name=mapped_class,
                confidence=conf,
                advice=advice,
            )
            detections.append(det)

        # Determinar resíduo principal (prioridade para maior confiança)
        primary_detection = max(detections, key=lambda d: d.confidence) if detections else None
        return detections, primary_detection

    def annotate_image(
        self,
        image: Image.Image,
        detections: List[WasteDetectionResult],
    ) -> Image.Image:
        """
        Desenha as caixas delimitadoras e rótulos na imagem com cores estilizadas.
        """
        annotated = image.copy().convert("RGB")
        draw = ImageDraw.Draw(annotated)

        # Tentar usar uma fonte TrueType ou fonte padrão do PIL
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        for det in detections:
            x1, y1, x2, y2 = det.box
            cls_key = det.class_name.upper()
            color = CLASS_COLORS.get(cls_key, "#4CAF50")
            display = det.advice.display_name
            conf_percent = f"{det.confidence * 100:.1f}%"
            label = f"{display}: {conf_percent}"

            # Desenhar retângulo espesso
            for offset in range(3):
                draw.rectangle(
                    [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                    outline=color,
                )

            # Desenhar fundo do texto
            text_bbox = draw.textbbox((x1, y1), label, font=font)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            draw.rectangle(
                [x1, max(0, y1 - text_h - 6), x1 + text_w + 10, y1],
                fill=color,
            )
            draw.text(
                (x1 + 5, max(0, y1 - text_h - 4)),
                label,
                fill="#FFFFFF",
                font=font,
            )

        return annotated
