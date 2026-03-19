import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Documento
from .forms import DocumentoUploadForm, DocumentoValidacaoForm


@staff_member_required
def redirecionar_inicio(request):
    return redirect('documentos:upload')


@staff_member_required
def upload_documento(request):
    if request.method == 'POST':
        form = DocumentoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.estado = Documento.EstadoDocumento.A_PROCESSAR
            documento.save()
            from .tasks import processar_documento_task
            processar_documento_task.delay(documento.pk)
            messages.info(request, f'"{documento.nome_ficheiro}" submetido. A processar em background...')
            return redirect('documentos:detalhe', pk=documento.pk)
    else:
        form = DocumentoUploadForm()
    return render(request, 'documentos/upload.html', {'form': form})


@staff_member_required
def lista_documentos(request):
    documentos = Documento.objects.all()
    contexto = {
        'documentos':  documentos,
        'total':       documentos.count(),
        'a_processar': documentos.filter(estado=Documento.EstadoDocumento.A_PROCESSAR).count(),
        'a_validar':   documentos.filter(estado=Documento.EstadoDocumento.A_VALIDAR).count(),
        'validados':   documentos.filter(estado=Documento.EstadoDocumento.VALIDADO).count(),
        'com_erro':    documentos.filter(estado=Documento.EstadoDocumento.ERRO).count(),
    }
    return render(request, 'documentos/lista.html', contexto)


@staff_member_required
def detalhe_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    pode_validar = documento.estado == Documento.EstadoDocumento.A_VALIDAR
    form = DocumentoValidacaoForm(instance=documento) if pode_validar else None
    return render(request, 'documentos/detalhe.html', {
        'documento':   documento,
        'form':        form,
        'pode_validar': pode_validar,
    })


@staff_member_required
@require_POST
def validar_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    if documento.estado != Documento.EstadoDocumento.A_VALIDAR:
        messages.error(request, 'Este documento não está em estado de validação.')
        return redirect('documentos:detalhe', pk=pk)

    form = DocumentoValidacaoForm(request.POST, instance=documento)
    if form.is_valid():
        doc = form.save(commit=False)
        doc.estado = Documento.EstadoDocumento.VALIDADO
        doc.data_validacao = timezone.now()
        doc.save()
        messages.success(request, 'Documento validado com sucesso.')
    else:
        messages.error(request, 'Erro na validação. Verifique os campos.')
    return redirect('documentos:detalhe', pk=pk)


@staff_member_required
def estado_documento(request, pk):
    documento = get_object_or_404(Documento, pk=pk)
    return JsonResponse({
        'estado':       documento.estado,
        'estado_label': documento.get_estado_display(),
        'erro_detalhe': documento.erro_detalhe,
    })
