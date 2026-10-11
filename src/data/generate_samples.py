"""
Script utilitário para gerar imagens BMP simples sem necessidade de bibliotecas externas.
Garante que a aplicação tenha amostras na pasta data/samples/ mesmo antes de pip install.
"""

from pathlib import Path
import struct

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

def write_bmp(filename: Path, width: int, height: int, draw_fn):
    """Escreve um arquivo BMP 24-bit em RGB puro usando apenas standard library."""
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    image_size = (row_bytes + padding) * height
    file_size = 54 + image_size

    header = struct.pack(
        "<2sIHHI",
        b"BM",
        file_size,
        0,
        0,
        54,
    )
    dib_header = struct.pack(
        "<IiiHHIIiiII",
        40,
        width,
        height,
        1,
        24,
        0,
        image_size,
        2835,
        2835,
        0,
        0,
    )

    with open(filename, "wb") as f:
        f.write(header)
        f.write(dib_header)
        for y in range(height):
            row = bytearray()
            for x in range(width):
                r, g, b = draw_fn(x, y, width, height)
                # BMP armazena em formato BGR
                row.extend([b, g, r])
            row.extend(b"\x00" * padding)
            f.write(row)

def draw_apple(x, y, w, h):
    cx, cy = w // 2, h // 2
    dx = x - cx
    dy = y - cy
    # Maçã vermelha no centro
    if (dx*dx) / (120*120) + (dy*dy) / (130*130) <= 1.0:
        return (211, 47, 47)
    # Folha verde
    if abs(x - (cx + 30)) < 25 and 100 < y < 140:
        return (56, 142, 60)
    # Fundo cinza claro
    return (240, 240, 240)

def draw_bottle(x, y, w, h):
    cx = w // 2
    # Gargalo
    if abs(x - cx) < 25 and 150 <= y <= 230:
        return (100, 181, 246)
    # Corpo da garrafa
    if abs(x - cx) < 65 and 230 <= y <= 450:
        return (144, 202, 249)
    # Tampa
    if abs(x - cx) < 20 and 130 <= y < 150:
        return (229, 57, 53)
    # Fundo
    return (245, 245, 245)

def draw_cardboard(x, y, w, h):
    cx = w // 2
    # Caixa retangular marrom
    if abs(x - cx) < 140 and 200 <= y <= 440:
        if abs(x - cx) < 5 or abs(y - 320) < 5:
            return (141, 110, 99) # Linhas de dobra
        return (205, 163, 118) # Papelão
    return (240, 240, 240)

def generate():
    write_bmp(SAMPLES_DIR / "amostra_organico_maca.bmp", 500, 500, draw_apple)
    write_bmp(SAMPLES_DIR / "amostra_plastico_garrafa.bmp", 500, 500, draw_bottle)
    write_bmp(SAMPLES_DIR / "amostra_papelao_caixa.bmp", 500, 500, draw_cardboard)
    print("Amostras BMP criadas com sucesso em data/samples/!")

if __name__ == "__main__":
    generate()
