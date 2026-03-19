import io
from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def processar_documento_task(self, documento_id):
    from .models import Documento
    from core_ia.preprocessor import preprocessar_ficheiro
    from core_ia.ocr import extrair_texto
    from core_ia.extractor import extrair_campos

    try:
        documento = Documento.objects.get(pk=documento_id)
    except Documento.DoesNotExist:
        return

    try:
        # 1. Pré-processamento
        imagens = preprocessar_ficheiro(documento.ficheiro_original.path)

        # 2. Guardar imagem processada (primeira página)
        _guardar_imagem_processada(documento, imagens[0])

        # 3. OCR
        texto = extrair_texto(imagens)
        documento.texto_extraido_raw = texto

        if not texto.strip():
            raise ValueError('O OCR não extraiu texto. Verifique a qualidade do ficheiro.')

        # 4. Extração por IA
        dados = extrair_campos(texto)
        documento.resposta_ia_json = dados

        # 5. Mapear campos extraídos
        documento.nif_extraido = dados.get('nif') or ''
        documento.tipo_documento = _mapear_tipo(dados.get('tipo_documento'))
        documento.confianca_ia = _float_seguro(dados.get('confianca'))
        documento.total_extraido = _decimal_seguro(dados.get('valor_total'))
        documento.iva_extraido = _decimal_seguro(dados.get('valor_iva'))

        if dados.get('data_emissao'):
            from datetime import date
            documento.data_extraida = date.fromisoformat(dados['data_emissao'])

        documento.estado = Documento.EstadoDocumento.A_VALIDAR
        documento.data_processamento = timezone.now()

    except Exception as exc:
        documento.estado = Documento.EstadoDocumento.ERRO
        documento.erro_detalhe = str(exc)
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            pass

    finally:
        documento.save()


# --- Helpers ---

def _guardar_imagem_processada(documento, imagem):
    from django.core.files.base import ContentFile
    from .models import Documento

    buf = io.BytesIO()
    imagem.save(buf, format='PNG')
    nome = f'proc_{documento.pk}.png'
    documento.imagem_processada.save(nome, ContentFile(buf.getvalue()), save=False)


def _mapear_tipo(valor):
    from .models import Documento
    mapa = {t.value: t for t in Documento.TipoDocumento}
    return mapa.get(str(valor).upper(), Documento.TipoDocumento.OUTRO)


def _float_seguro(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def _decimal_seguro(valor):
    from decimal import Decimal, InvalidOperation
    try:
        return Decimal(str(valor))
    except (TypeError, ValueError, InvalidOperation):
        return None
