from django.contrib import admin
from .models import Documento


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nome_ficheiro', 'tipo_documento', 'estado', 'nif_extraido', 'total_extraido', 'data_upload']
    list_filter   = ['tipo_documento', 'estado']
    search_fields = ['nif_extraido']
    readonly_fields = [
        'data_upload', 'data_processamento', 'data_validacao',
        'texto_extraido_raw', 'resposta_ia_json', 'erro_detalhe',
        'imagem_processada', 'confianca_ia',
    ]
    fieldsets = (
        ('Ficheiro',          {'fields': ('ficheiro_original', 'tipo_documento', 'estado')}),
        ('Imagem Processada', {'fields': ('imagem_processada',)}),
        ('Dados Extraídos',   {'fields': ('nif_extraido', 'data_extraida', 'total_extraido', 'iva_extraido', 'confianca_ia')}),
        ('Processamento',     {'fields': ('data_upload', 'data_processamento', 'data_validacao', 'texto_extraido_raw', 'resposta_ia_json', 'erro_detalhe')}),
    )
