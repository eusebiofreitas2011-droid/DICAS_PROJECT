"""
Pré-processamento de imagem: tons de cinza, aumento de contraste, normalização.
Recebe o caminho do ficheiro original (PDF ou imagem) e devolve uma PIL.Image pronta para OCR.
"""
import io
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


FORMATOS_IMAGEM = {'.png', '.jpg', '.jpeg', '.tiff', '.tif'}


def carregar_paginas(caminho: str) -> list[Image.Image]:
    """Carrega o ficheiro e devolve uma lista de PIL.Image (uma por página/frame)."""
    path = Path(caminho)
    extensao = path.suffix.lower()

    if extensao == '.pdf':
        return _pdf_para_imagens(caminho)
    elif extensao in FORMATOS_IMAGEM:
        img = Image.open(caminho)
        frames = []
        try:
            while True:
                frames.append(img.copy())
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        return frames if frames else [img]
    else:
        raise ValueError(f'Formato não suportado: {extensao}')


def _pdf_para_imagens(caminho: str) -> list[Image.Image]:
    from pdf2image import convert_from_path
    return convert_from_path(caminho, dpi=300)


def preprocessar(imagem: Image.Image) -> Image.Image:
    """Converte para tons de cinza, aumenta contraste e normaliza."""
    img = imagem.convert('L')                        # tons de cinza
    img = ImageEnhance.Contrast(img).enhance(2.0)   # aumentar contraste
    img = img.filter(ImageFilter.SHARPEN)            # nitidez
    return img


def preprocessar_ficheiro(caminho: str) -> list[Image.Image]:
    """Pipeline completo: carrega → pré-processa. Devolve lista de imagens processadas."""
    paginas = carregar_paginas(caminho)
    return [preprocessar(p) for p in paginas]
