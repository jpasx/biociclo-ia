"""
Módulo de Detecção de Resíduos com YOLO e Calibração Pós-Inferência
Suporta carregamento do modelo treinado (best.pt), mitigação de viés de classe
do dataset Garbage Classification 3 (GC1) e modo fallback (pré-treinado).
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from src.config import (
    PROJECT_ROOT,
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

# Fatores de calibração suave para o modelo YOLO11s retreinado (45 épocas com dataset rebalanceado)
GC1_PRIOR_CALIBRATION = {
    "BIODEGRADABLE": 1.12,
    "CARDBOARD": 1.00,
    "GLASS": 1.00,
    "METAL": 1.00,
    "PAPER": 1.12,
    "PLASTIC": 1.05,
    "CLOTH": 1.05,
    "TRASH": 1.00,
}


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_clean = hex_color.lstrip("#")
    if len(hex_clean) != 6:
        return (16, 185, 129)
    return (
        int(hex_clean[0:2], 16),
        int(hex_clean[2:4], 16),
        int(hex_clean[4:6], 16),
    )


def _compute_iou(box_a: List[float], box_b: List[float]) -> float:
    x_a = max(box_a[0], box_b[0])
    y_a = max(box_a[1], box_b[1])
    x_b = min(box_a[2], box_b[2])
    y_b = min(box_a[3], box_b[3])

    inter_w = max(0.0, x_b - x_a)
    inter_h = max(0.0, y_b - y_a)
    inter_area = inter_w * inter_h

    area_a = max(1e-6, (box_a[2] - box_a[0]) * (box_a[3] - box_a[1]))
    area_b = max(1e-6, (box_b[2] - box_b[0]) * (box_b[3] - box_b[1]))
    return inter_area / (area_a + area_b - inter_area + 1e-6)


class WasteDetectionResult:
    def __init__(
        self,
        box: List[float],  # [x1, y1, x2, y2]
        class_name: str,
        confidence: float,
        advice: DestinationAdvice,
        area_ratio: float = 0.0,
        calibrated: bool = False,
    ):
        self.box = box
        self.class_name = class_name
        self.confidence = confidence
        self.advice = advice
        self.area_ratio = area_ratio
        self.calibrated = calibrated

    def to_dict(self) -> Dict[str, Any]:
        return {
            "box": self.box,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "display_name": self.advice.display_name,
            "waste_type": self.advice.waste_type,
            "destination": self.advice.destination,
            "conama_bin": self.advice.conama_bin,
            "is_uncertain": self.advice.is_uncertain,
            "warning_message": self.advice.warning_message,
            "area_ratio": round(self.area_ratio, 4),
            "calibrated": self.calibrated,
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
        self.load_error: Optional[str] = None

        # Verificar se ultralytics está disponível
        try:
            from ultralytics import YOLO
            self._yolo_class = YOLO
        except ImportError as err:
            self._yolo_class = None
            self.load_error = f"Ultralytics não instalado: {err}"

        self._load_model(model_path)

    def _load_model(self, model_path: Optional[str]):
        if self._yolo_class is None:
            return

        # 1. Se foi passado caminho específico e existe
        if model_path and Path(model_path).exists():
            try:
                self.model = self._yolo_class(model_path)
                self.is_custom_model = True
                self.model_name = Path(model_path).name
                self.load_error = None
                return
            except Exception as e:
                self.load_error = f"Erro ao carregar modelo customizado {model_path}: {e}"
                print(self.load_error)

        # 2. Buscar o arquivo best.pt em múltiplos locais possíveis
        candidate_paths = [
            DEFAULT_MODEL_WEIGHTS,
            PROJECT_ROOT / "models" / "weights" / "best.pt",
            Path.cwd() / "models" / "weights" / "best.pt",
            Path("models/weights/best.pt").resolve(),
            Path(__file__).resolve().parent.parent.parent / "models" / "weights" / "best.pt",
            Path("/mount/src/biociclo-ia/models/weights/best.pt"),
            Path("/app/biociclo-ia/models/weights/best.pt"),
        ]

        weights_file = None
        for p in candidate_paths:
            try:
                if p.is_file() and p.stat().st_size > 1000000:
                    weights_file = p.resolve()
                    break
            except Exception:
                pass

        # Se ainda não encontrou, busca recursiva a partir da raiz do projeto e cwd
        if not weights_file:
            try:
                for base in [PROJECT_ROOT, Path.cwd(), Path(__file__).resolve().parent.parent.parent]:
                    if base.exists():
                        for m in base.rglob("best.pt"):
                            try:
                                if m.is_file() and m.stat().st_size > 1000000:
                                    weights_file = m.resolve()
                                    break
                            except Exception:
                                pass
                    if weights_file:
                        break
            except Exception:
                pass

        # 3. Se ainda não tem o arquivo localmente no servidor da nuvem, baixa automaticamente do GitHub
        if not weights_file:
            try:
                import urllib.request
                target_dest = PROJECT_ROOT / "models" / "weights" / "best.pt"
                target_dest.parent.mkdir(parents=True, exist_ok=True)
                url = "https://raw.githubusercontent.com/jpasx/biociclo-ia/main/models/weights/best.pt"
                print(f"Baixando best.pt automaticamente do GitHub para: {target_dest}")
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=45) as resp, open(target_dest, "wb") as out_f:
                    out_f.write(resp.read())

                if target_dest.exists() and target_dest.stat().st_size > 1000000:
                    weights_file = target_dest.resolve()
            except Exception as e:
                self.load_error = f"Download falhou: {e}"
                print(f"Não foi possível baixar best.pt automaticamente: {e}")

        # 4. Tentar carregar os pesos treinados
        if weights_file and Path(weights_file).exists():
            try:
                self.model = self._yolo_class(str(weights_file))
                self.is_custom_model = True
                self.model_name = "best.pt (Modelo Treinado BioCiclo)"
                self.load_error = None
                return
            except Exception as e:
                self.load_error = f"Erro ao instanciar YOLO('{weights_file}'): {e}"
                print(self.load_error)

        # 5. Fallback para modelo base demonstrativo
        if not self.load_error:
            self.load_error = "Arquivo best.pt não localizado nos caminhos do servidor."
        try:
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

    def _analyze_roi_material_cues(self, img_np: np.ndarray, box: List[float]) -> Optional[str]:
        """
        Analisa pistas cromáticas e de luminância da Região de Interesse (ROI)
        quando o modelo treinado por poucas épocas sofre colapso para BIODEGRADABLE.
        Retorna sugestão de classe apenas quando o padrão visual for fortemente incompatível
        com biomassa orgânica (ex: superfície metálica acinzentada, papelão homogêneo, etc.).
        """
        h, w, _ = img_np.shape
        x1 = max(0, int(box[0]))
        y1 = max(0, int(box[1]))
        x2 = min(w, int(box[2]))
        y2 = min(h, int(box[3]))
        if (x2 - x1) < 16 or (y2 - y1) < 16:
            return None

        roi = img_np[y1:y2, x1:x2].astype(np.float32)
        r, g, b = roi[:, :, 0], roi[:, :, 1], roi[:, :, 2]

        max_c = np.maximum(np.maximum(r, g), b)
        min_c = np.minimum(np.minimum(r, g), b)
        diff = max_c - min_c
        sat = np.where(max_c > 1e-3, diff / (max_c + 1e-3), 0.0)
        val = max_c / 255.0

        mean_sat = float(np.mean(sat))
        mean_val = float(np.mean(val))
        std_val = float(np.std(val))
        mean_r = float(np.mean(r))
        mean_g = float(np.mean(g))
        mean_b = float(np.mean(b))

        # Presença de vermelho vivo ou verde vivo (típico de frutas/folhas orgânicas)
        vivid_organic_mask = ((r > 135) & (r > g * 1.25) & (sat > 0.32)) | (
            (g > 110) & (g > r * 1.15) & (sat > 0.28)
        )
        organic_ratio = float(np.mean(vivid_organic_mask))
        if organic_ratio > 0.22:
            return "BIODEGRADABLE"

        # Padrão de papelão (tom ocre/marrom uniforme: R > G > B com saturação moderada e baixa variância)
        if (
            135 < mean_r < 225
            and 100 < mean_g < 185
            and 65 < mean_b < 145
            and (mean_r - mean_g) > 15
            and (mean_g - mean_b) > 15
            and std_val < 0.20
        ):
            return "CARDBOARD"

        # Padrão translúcido claro / plástico fosco em fundo claro (baixa saturação, alta luminância)
        blue_cap_mask = (b > 110) & (b > r * 1.35) & (sat > 0.35)
        if mean_sat < 0.14 and mean_val > 0.62 and float(np.mean(blue_cap_mask)) > 0.008:
            return "PLASTIC"

        # Padrão metálico especular (baixa saturação global, mas alto contraste entre brilho e sombra)
        if mean_sat < 0.18 and std_val > 0.22 and 0.45 < mean_val < 0.85:
            return "METAL"

        return None

    def predict(
        self,
        image: Image.Image,
        conf_threshold: Optional[float] = None,
        calibrate_bias: bool = True,
    ) -> Tuple[List[WasteDetectionResult], Optional[WasteDetectionResult]]:
        """
        Executa a predição na imagem com suporte a calibração de prior (mitigando a
        super-predição de BIODEGRADABLE do dataset GC1) e filtragem de ruído espacial.
        """
        threshold = conf_threshold if conf_threshold is not None else self.conf_threshold
        detections: List[WasteDetectionResult] = []

        if self.model is None:
            return detections, None

        img_rgb = image.convert("RGB")
        img_np = np.array(img_rgb)
        img_h, img_w = img_np.shape[:2]
        img_area = float(max(1, img_w * img_h))

        # Usamos um limiar interno menor quando calibrate_bias=True para recuperar
        # classes recicláveis sub-representadas antes de aplicar o corte final
        query_conf = max(0.04, threshold * 0.55) if (calibrate_bias and self.is_custom_model) else threshold

        results = self.model.predict(
            img_np,
            conf=query_conf,
            iou=self.iou_threshold,
            agnostic_nms=False,
            verbose=False,
        )

        if not results or len(results) == 0:
            return detections, None

        first_res = results[0]
        boxes = first_res.boxes

        if boxes is None or len(boxes) == 0:
            return detections, None

        raw_candidates: List[Dict[str, Any]] = []
        for box in boxes:
            coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            raw_conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            raw_name = first_res.names.get(cls_id, f"class_{cls_id}")

            if not self.is_custom_model:
                mapped_class = COCO_FALLBACK_MAPPING.get(raw_name.lower(), "TRASH")
            else:
                mapped_class = raw_name.upper()

            box_w = max(0.0, coords[2] - coords[0])
            box_h = max(0.0, coords[3] - coords[1])
            area_ratio = (box_w * box_h) / img_area

            # Descartar micro-artefatos irrelevantes (< 0.25% da área total da foto)
            if area_ratio < 0.0025:
                continue

            calibrated_flag = False
            adj_conf = raw_conf

            if calibrate_bias and self.is_custom_model:
                multiplier = GC1_PRIOR_CALIBRATION.get(mapped_class, 1.0)
                adj_conf = min(0.99, raw_conf * multiplier)
                if abs(multiplier - 1.0) > 0.01:
                    calibrated_flag = True

            raw_candidates.append({
                "box": coords,
                "class_name": mapped_class,
                "raw_conf": raw_conf,
                "adj_conf": adj_conf,
                "area_ratio": area_ratio,
                "calibrated": calibrated_flag,
            })

        # NMS agnóstico espacial entre candidatos para evitar caixas duplicadas no mesmo objeto
        if calibrate_bias and self.is_custom_model and raw_candidates:
            raw_candidates.sort(key=lambda c: c["adj_conf"], reverse=True)
            filtered_candidates: List[Dict[str, Any]] = []
            for cand in raw_candidates:
                if cand["adj_conf"] < threshold and cand["raw_conf"] < threshold:
                    continue
                duplicate = False
                for kept in filtered_candidates:
                    iou_val = _compute_iou(cand["box"], kept["box"])
                    if iou_val > 0.48:
                        duplicate = True
                        break
                if not duplicate:
                    filtered_candidates.append(cand)
            active_candidates = filtered_candidates
        else:
            active_candidates = [c for c in raw_candidates if c["raw_conf"] >= threshold]

        # Construir objetos finais de resultado
        for cand in active_candidates:
            final_conf = cand["adj_conf"] if calibrate_bias else cand["raw_conf"]
            advice = get_destination_advice(cand["class_name"], final_conf, threshold)
            det = WasteDetectionResult(
                box=cand["box"],
                class_name=cand["class_name"],
                confidence=final_conf,
                advice=advice,
                area_ratio=cand["area_ratio"],
                calibrated=cand["calibrated"],
            )
            detections.append(det)

        # Ordenar combinando confiança e relevância espacial (objetos muito pequenos no canto não roubam o topo)
        detections.sort(
            key=lambda d: d.confidence * (0.75 + 0.25 * min(1.0, d.area_ratio * 4.0)),
            reverse=True,
        )

        # Limitar excesso de caixas secundárias idênticas em cenas densas (ex: feiras livres)
        if len(detections) > 15:
            detections = detections[:15]

        primary_detection = detections[0] if detections else None
        return detections, primary_detection

    def annotate_image(
        self,
        image: Image.Image,
        detections: List[WasteDetectionResult],
    ) -> Image.Image:
        """
        Desenha caixas delimitadoras com preenchimento semitransparente moderno,
        cantos destacados e rótulos dimensionados proporcionalmente à resolução da imagem.
        """
        base_rgba = image.copy().convert("RGBA")
        overlay = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
        draw_ov = ImageDraw.Draw(overlay)

        w, h = base_rgba.size
        scale = max(1.0, min(w, h) / 480.0)
        font_size = max(13, int(15 * scale))

        font = None
        for font_candidate in ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
            try:
                font = ImageFont.truetype(font_candidate, font_size)
                break
            except Exception:
                continue
        if font is None:
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

        sorted_dets = list(detections)
        max_labeled = 4 if len(sorted_dets) > 5 else len(sorted_dets)

        for idx in range(len(sorted_dets) - 1, -1, -1):
            det = sorted_dets[idx]
            x1, y1, x2, y2 = det.box
            cls_key = det.class_name.upper()
            hex_color = CLASS_COLORS.get(cls_key, "#10B981")
            r, g, b = _hex_to_rgb(hex_color)
            is_primary = idx == 0
            is_top = idx < max_labeled

            # Preenchimento translúcido suave apenas nas principais detecções
            fill_alpha = 42 if is_primary else (24 if is_top else 12)
            draw_ov.rectangle([x1, y1, x2, y2], fill=(r, g, b, fill_alpha))

            # Borda contínua
            thickness = max(2, int((3.5 if is_primary else 2.0) * scale))
            for offset in range(thickness):
                draw_ov.rectangle(
                    [x1 - offset, y1 - offset, x2 + offset, y2 + offset],
                    outline=(r, g, b, 235 if is_top else 160),
                )

            # Cantoneiras técnicas nas detecções de destaque
            if is_top:
                corner_len = min(int(20 * scale), int((x2 - x1) * 0.25), int((y2 - y1) * 0.25))
                c_thick = thickness + 1
                if corner_len > 6:
                    # Superior esquerdo
                    draw_ov.rectangle([x1 - c_thick, y1 - c_thick, x1 + corner_len, y1 + 1], fill=(r, g, b, 255))
                    draw_ov.rectangle([x1 - c_thick, y1 - c_thick, x1 + 1, y1 + corner_len], fill=(r, g, b, 255))
                    # Superior direito
                    draw_ov.rectangle([x2 - corner_len, y1 - c_thick, x2 + c_thick, y1 + 1], fill=(r, g, b, 255))
                    draw_ov.rectangle([x2 - 1, y1 - c_thick, x2 + c_thick, y1 + corner_len], fill=(r, g, b, 255))
                    # Inferior esquerdo
                    draw_ov.rectangle([x1 - c_thick, y2 - 1, x1 + corner_len, y2 + c_thick], fill=(r, g, b, 255))
                    draw_ov.rectangle([x1 - c_thick, y2 - corner_len, x1 + 1, y2 + c_thick], fill=(r, g, b, 255))
                    # Inferior direito
                    draw_ov.rectangle([x2 - corner_len, y2 - 1, x2 + c_thick, y2 + c_thick], fill=(r, g, b, 255))
                    draw_ov.rectangle([x2 - 1, y2 - corner_len, x2 + c_thick, y2 + c_thick], fill=(r, g, b, 255))

            if is_top:
                short_name = det.advice.display_name.split("/")[0].strip()
                conf_percent = f"{det.confidence * 100:.0f}%"
                rank_prefix = f"#{idx + 1} " if len(sorted_dets) > 1 else ""
                label = f"{rank_prefix}{short_name} • {conf_percent}"

                text_bbox = draw_ov.textbbox((x1, y1), label, font=font)
                text_w = text_bbox[2] - text_bbox[0]
                text_h = text_bbox[3] - text_bbox[1]
                pad_x = max(6, int(7 * scale))
                pad_y = max(4, int(4 * scale))

                tag_y1 = max(0, y1 - text_h - pad_y * 2 - 2)
                tag_y2 = tag_y1 + text_h + pad_y * 2
                tag_x1 = max(0, min(x1, w - text_w - pad_x * 2))
                tag_x2 = min(w, tag_x1 + text_w + pad_x * 2)

                draw_ov.rectangle(
                    [tag_x1, tag_y1, tag_x2, tag_y2],
                    fill=(r, g, b, 240),
                )
                draw_ov.text(
                    (tag_x1 + pad_x, tag_y1 + pad_y - 1),
                    label,
                    fill=(255, 255, 255, 255),
                    font=font,
                )

        combined = Image.alpha_composite(base_rgba, overlay)
        return combined.convert("RGB")
