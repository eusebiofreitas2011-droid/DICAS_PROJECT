from django.db import models


class Documento(models.Model):

    class TipoDocumento(models.TextChoices):
        FATURA = 'FATURA', 'Fatura'
        RECIBO = 'RECIBO', 'Recibo'
        OUTRO  = 'OUTRO',  'Outro'

    class EstadoDocumento(models.TextChoices):
        A_PROCESSAR = 'A_PROCESSAR', 'A Processar'
        A_VALIDAR   = 'A_VALIDAR',   'Aguardando Validação'
        VALIDADO    = 'VALIDADO',    'Validado'
        ERRO        = 'ERRO',        'Erro no Processamento'

    # --- Ficheiro original ---
    ficheiro_original  = models.FileField(upload_to='documentos/%Y/%m/')
    tipo_documento     = models.CharField(
        max_length=10,
        choices=TipoDocumento.choices,
        default=TipoDocumento.OUTRO,
    )

    # --- Imagem pré-processada (gerada pelo pipeline) ---
    imagem_processada = models.ImageField(
        upload_to='processadas/%Y/%m/',
        null=True, blank=True,
    )

    # --- Resultado OCR ---
    texto_extraido_raw = models.TextField(blank=True)

    # --- Resposta completa do LLM ---
    resposta_ia_json = models.JSONField(default=dict, blank=True)

    # --- Estado e datas ---
    estado              = models.CharField(
        max_length=15,
        choices=EstadoDocumento.choices,
        default=EstadoDocumento.A_PROCESSAR,
    )
    data_upload         = models.DateTimeField(auto_now_add=True)
    data_processamento  = models.DateTimeField(null=True, blank=True)
    data_validacao      = models.DateTimeField(null=True, blank=True)

    # --- Campos extraídos pela IA ---
    nif_extraido    = models.CharField(max_length=20, blank=True)
    data_extraida   = models.DateField(null=True, blank=True)
    total_extraido  = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    iva_extraido    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    confianca_ia    = models.FloatField(null=True, blank=True)

    # --- Erro ---
    erro_detalhe = models.TextField(blank=True)

    class Meta:
        ordering = ['-data_upload']
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'

    def __str__(self):
        return f"{self.get_tipo_documento_display()} #{self.pk} — {self.get_estado_display()}"

    @property
    def nome_ficheiro(self):
        return self.ficheiro_original.name.split('/')[-1] if self.ficheiro_original else ''
