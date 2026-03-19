"""
Extração de texto via Tesseract OCR.
Recebe uma lista de PIL.Image e devolve o texto bruto concatenado.
"""
import pytesseract
from django.conf import settings
from PIL import Image

# Configura o path do executável (necessário no Windows)
if hasattr(settings, 'TESSERACT_CMD'):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def extrair_texto(imagens: list[Image.Image], lang: str = 'por') -> str:
    """Corre Tesseract em cada página e concatena o resultado."""
    partes = []
    for imagem in imagens:
        texto = pytesseract.image_to_string(imagem, lang=lang)
        partes.append(texto)
    return '\n'.join(partes).strip()
