"""
Extração de campos estruturados via Ollama (LLM local).
Recebe texto bruto do OCR e devolve um dict com os campos extraídos.
"""
import json
import requests

def _ollama_config():
    try:
        from django.conf import settings
        return getattr(settings, 'OLLAMA_URL', 'http://localhost:11434/api/generate'), \
               getattr(settings, 'OLLAMA_MODEL', 'llama3')
    except Exception:
        return 'http://localhost:11434/api/generate', 'llama3'

PROMPT_TEMPLATE = """\
Analisa o seguinte texto extraído de um documento financeiro e devolve APENAS um objeto JSON \
com os seguintes campos. Se não conseguires extrair um campo, usa null.

{{
  "nif": "string ou null",
  "data_emissao": "YYYY-MM-DD ou null",
  "valor_total": "decimal ou null",
  "valor_iva": "decimal ou null",
  "tipo_documento": "FATURA | RECIBO | OUTRO",
  "confianca": "valor entre 0.0 e 1.0"
}}

Texto a analisar:
{texto}
"""


def extrair_campos(texto_ocr: str, modelo: str = None) -> dict:
    """
    Envia o texto OCR ao Ollama e devolve o JSON extraído como dict.
    Lança exceção se a resposta não for JSON válido.
    """
    ollama_url, ollama_model = _ollama_config()
    if modelo is None:
        modelo = ollama_model
    prompt = PROMPT_TEMPLATE.format(texto=texto_ocr)
    resposta = requests.post(
        ollama_url,
        json={'model': modelo, 'prompt': prompt, 'stream': False},
        timeout=120,
    )
    resposta.raise_for_status()

    conteudo = resposta.json().get('response', '{}').strip()
    return _parse_json(conteudo)


def _parse_json(texto: str) -> dict:
    """Extrai o primeiro objeto JSON válido da resposta, ignorando texto em volta."""
    # Caso ideal: resposta é JSON puro
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    # Caso com bloco markdown: ```json {...} ```
    if '```' in texto:
        partes = texto.split('```')
        for parte in partes:
            candidato = parte.removeprefix('json').strip()
            try:
                return json.loads(candidato)
            except json.JSONDecodeError:
                continue

    # Caso com texto antes/depois: extrair por delimitadores { }
    inicio = texto.find('{')
    fim = texto.rfind('}')
    if inicio != -1 and fim != -1:
        return json.loads(texto[inicio:fim + 1])

    raise ValueError(f'Não foi possível extrair JSON da resposta: {texto[:200]}')
