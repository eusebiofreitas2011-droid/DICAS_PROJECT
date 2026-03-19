from django import forms
from .models import Documento

FORMATOS_ACEITES = ('.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif')
TAMANHO_MAXIMO  = 10 * 1024 * 1024  # 10 MB


class DocumentoUploadForm(forms.ModelForm):
    class Meta:
        model  = Documento
        fields = ['ficheiro_original', 'tipo_documento']
        labels = {
            'ficheiro_original': 'Ficheiro (PDF, PNG, JPG, TIFF)',
            'tipo_documento':    'Tipo de Documento',
        }

    def clean_ficheiro_original(self):
        ficheiro = self.cleaned_data.get('ficheiro_original')
        if ficheiro:
            if not any(ficheiro.name.lower().endswith(ext) for ext in FORMATOS_ACEITES):
                raise forms.ValidationError(
                    f'Formato não suportado. Aceites: {", ".join(FORMATOS_ACEITES)}.'
                )
            if ficheiro.size > TAMANHO_MAXIMO:
                raise forms.ValidationError('O ficheiro não pode exceder 10 MB.')
        return ficheiro


class DocumentoValidacaoForm(forms.ModelForm):
    class Meta:
        model  = Documento
        fields = ['tipo_documento', 'nif_extraido', 'data_extraida', 'total_extraido', 'iva_extraido']
        labels = {
            'tipo_documento':  'Tipo de Documento',
            'nif_extraido':    'NIF',
            'data_extraida':   'Data de Emissão',
            'total_extraido':  'Valor Total (€)',
            'iva_extraido':    'IVA (€)',
        }
        widgets = {
            'data_extraida': forms.DateInput(attrs={'type': 'date'}),
        }
