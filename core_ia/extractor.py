"""
Extração de campos estruturados via Ollama (LLM local).
Recebe texto bruto do OCR e devolve um dict com os campos extraídos.
"""
import json
import requests

OLLAMA_URL   = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3'  # alternativa leve: phi3:mini

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


def extrair_campos(texto_ocr: str, modelo: str = OLLAMA_MODEL) -> dict:
    """
    Envia o texto OCR ao Ollama e devolve o JSON extraído como dict.
    Lança exceção se a resposta não for JSON válido.
    """
    prompt = PROMPT_TEMPLATE.format(texto=texto_ocr)
    resposta = requests.post(
        OLLAMA_URL,
        json={'model': modelo, 'prompt': prompt, 'stream': False},
        timeout=120,
    )
    resposta.raise_for_status()

    conteudo = resposta.json().get('response', '{}').strip()
    # Remover bloco markdown se o modelo o incluir
    if conteudo.startswith('```'):
        conteudo = conteudo.split('```')[1].removeprefix('json').strip()

    return json.loads(conteudo)
