"""
Extração de texto via Tesseract OCR.
Recebe uma lista de PIL.Image e devolve o texto bruto concatenado.
"""
import pytesseract
from PIL import Image


def extrair_texto(imagens: list[Image.Image], lang: str = 'por') -> str:
    """Corre Tesseract em cada página e concatena o resultado."""
    partes = []
    for imagem in imagens:
        texto = pytesseract.image_to_string(imagem, lang=lang)
        partes.append(texto)
    return '\n'.join(partes).strip()
