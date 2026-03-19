# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DICAS** (Document Intelligence & Classification Autonomous System) é um projeto piloto de aprendizagem para testar OCR e IA na leitura automática de faturas e recibos em PDF.

- **Stack:** Django 5, Python 3.11, Tesseract OCR, Ollama (LLM local), Celery, Redis, SQLite
- **Utilizador:** apenas o administrador (sem sistema de registo/autenticação de utilizadores externos)
- **Sem integração** com GitHub ou SIGAP

Encontra-se em fase inicial de desenvolvimento — ainda não existem apps Django personalizadas além da configuração padrão do admin.

## Commands

Activate the virtual environment before running any commands:

```bash
source venv/Scripts/activate  # Windows (Git Bash)
# or
venv\Scripts\activate.bat     # Windows CMD
```

Common management commands:

```bash
python manage.py runserver          # Start development server
python manage.py migrate            # Apply migrations
python manage.py makemigrations     # Generate migrations from model changes
python manage.py createsuperuser    # Create admin user
python manage.py test               # Run tests
python manage.py test <app>.tests.TestClass.test_method  # Run a single test
```

## Architecture

- `DICAS_PROJECT/settings.py` — Django settings (DEBUG=True, SQLite, UTC)
- `DICAS_PROJECT/urls.py` — URL routing (currently only `/admin/`)
- `DICAS_PROJECT/wsgi.py` / `asgi.py` — WSGI/ASGI entry points

New Django apps should be created with `python manage.py startapp <name>` and registered in `INSTALLED_APPS` in `settings.py`. App URLs should be included in `DICAS_PROJECT/urls.py` via `include()`.

When adding packages, update `requirements.txt` with `pip freeze > requirements.txt`.
SPEC DO PROJETO
DICAS PROJECT
Document Intelligence & Classification Autonomous System
Especificação Técnica — Versão 1.0
Projeto Piloto de Aprendizagem · DRADR


Natureza do documento
Este documento descreve um projeto piloto de aprendizagem, de âmbito pessoal e experimental.
Não é um módulo do SIGAP. Não partilha base de dados, autenticação nem infraestrutura com o SIGAP.
Objetivo: validar tecnologias de OCR e IA para leitura automática de documentos financeiros,
como prova de conceito para o futuro módulo SIGAP-ANALISE_PP.


1. Finalidade e Âmbito
O DICAS é uma aplicação web autónoma, desenvolvida como prova de conceito (PoC), cujo objetivo é validar uma arquitetura tecnológica capaz de automatizar a extração de dados-chave de documentos financeiros digitalizados — faturas e recibos em formato PDF ou imagem.

O utilizador único desta aplicação é o ADMINISTRADOR_SISTEMA (o próprio autor do projeto), que submete documentos manualmente, valida os resultados extraídos pela IA e observa o comportamento do sistema.

Objetivos específicos
1. Automatizar a extração de campos essenciais: NIF, data de emissão, valor total e IVA.
2. Validar ferramentas open-source gratuitas: Tesseract OCR + Ollama (LLM local).
3. Construir um pipeline robusto que lide com diferentes layouts e qualidade de digitalização.
4. Fornecer uma interface de validação humana para correção dos dados extraídos.
5. Servir de base de aprendizagem para o futuro módulo SIGAP-ANALISE_PP.


2. Âmbito e Exclusões Explícitas
Incluído no âmbito	Excluído do âmbito
Upload manual de PDF ou imagem	Integração com o SIGAP
Extração automática via OCR + IA local	Autenticação de múltiplos utilizadores
Validação e correção humana dos dados	Regras de negócio regulamentares
Persistência local dos resultados (SQLite)	Deploy em produção / ambiente partilhado
Interface web simples (Django + templates)	API pública ou endpoints externos


3. Arquitetura da Solução
A aplicação segue uma arquitetura de 3 camadas, implementada com o framework Django:

3.1. Camada de Apresentação (Frontend)
•	Tecnologia: Templates Django (HTML, CSS, JavaScript)
•	Página de upload: formulário simples para submissão de ficheiro PDF ou imagem
•	Página de listagem: tabela com todos os documentos submetidos e o seu estado de processamento
•	Página de detalhe: visualização do documento original lado a lado com formulário editável dos dados extraídos

3.2. Camada de Lógica de Negócio (Backend)
•	Tecnologia: Django 5.0+ com Python 3.11+
•	Views & URLs: gestão das rotas /upload, /documentos, /documentos/<id>
•	Models: estrutura da base de dados (ver Secção 5)
•	Forms: formulário de upload e formulário de edição dos dados extraídos
•	Celery + Redis: processamento assíncrono do OCR e da IA em background, evitando bloqueio da interface

3.3. Camada de Processamento (Core de Inteligência)
Módulo Python desacoplado, invocado pelo Celery, que executa o pipeline de análise:

#	Etapa	Descrição
1	Pré-processamento	Pillow + OpenCV: conversão para tons de cinza, aumento de contraste, normalização da imagem para melhorar a qualidade do OCR
2	Extração de texto (OCR)	Tesseract 5.x via pytesseract: converte a imagem em texto bruto, preservando coordenadas de cada palavra
3	Interpretação por IA	Ollama (LLM local): recebe o texto bruto via prompt estruturado e devolve os campos extraídos em formato JSON
4	Persistência	Os dados extraídos (JSON) são guardados na base de dados, associados ao documento original



4. Stack Tecnológica
Componente	Tecnologia	Notas
IDE	Visual Studio Code	Extensões: Python, Pylance, Django, Docker
Linguagem	Python 3.11+	
Framework web	Django 5.0+	
Base de dados (dev)	SQLite	Ficheiro local, sem instalação adicional
Base de dados (prod)	PostgreSQL	Para eventual deploy futuro
Motor OCR	Tesseract 5.x	Instalação separada do sistema operativo
IA local	Ollama	Modelo sugerido: phi3:mini (leve) ou llama3:8b (mais preciso)
Fila assíncrona	Celery	Gestão de tarefas em background
Broker de mensagens	Redis	Suporte ao Celery
Gestão de dependências	pip + requirements.txt	


5. Modelo de Dados
5.1. Enumerações
Estado do documento:
Valor técnico	Rótulo de apresentação	Descrição
A_PROCESSAR	A Processar	Documento submetido, a aguardar processamento pelo Celery
A_VALIDAR	Aguardando Validação	OCR e IA concluídos; aguarda revisão humana
VALIDADO	Validado	Dados confirmados pelo utilizador
ERRO	Erro no Processamento	Falha no OCR ou na resposta da IA

Tipo de documento:
Valor técnico	Descrição
FATURA	Fatura emitida por fornecedor
RECIBO	Recibo de pagamento
OUTRO	Documento não classificado

5.2. Objeto Documento
Campo	Tipo	Obrigatório	Descrição
id	AutoField (PK)	sim	Identificador único do documento
ficheiro_original	FileField	sim	Ficheiro submetido pelo utilizador (PDF ou imagem)
tipo_documento	enum TIPO_DOCUMENTO	não	Classificação do tipo de documento
imagem_processada	ImageField	não	Imagem após pré-processamento (tons de cinza, contraste)
texto_extraido_raw	TextField	não	Texto bruto devolvido pelo Tesseract
resposta_ia_json	JSONField	não	Resposta completa devolvida pelo LLM em formato JSON
estado	enum ESTADO_DOCUMENTO	sim	Estado atual do processamento
erro_detalhe	TextField	não	Mensagem de erro em caso de estado ERRO
data_upload	DateTimeField	sim	Data e hora de submissão (auto)
data_processamento	DateTimeField	não	Data e hora de conclusão do processamento pela IA
data_validacao	DateTimeField	não	Data e hora de validação pelo utilizador
nif_extraido	CharField(20)	não	NIF extraído pela IA
data_extraida	DateField	não	Data de emissão extraída pela IA
total_extraido	DecimalField(10,2)	não	Valor total extraído pela IA
iva_extraido	DecimalField(10,2)	não	Valor de IVA extraído pela IA
confianca_ia	FloatField	não	Score de confiança devolvido pelo LLM (0.0 a 1.0)

Nota sobre identificadores
Neste projeto piloto usa-se o AutoField padrão do Django (inteiro auto-incrementado) como chave primária.
Num módulo de produção do SIGAP, seria obrigatório usar UUID como chave primária,
conforme as Convenções Gerais de Modelação do SIGAP.


6. Regras de Negócio e Validações
6.1. Regras de Upload
•	Formatos aceites: PDF, PNG, JPG, JPEG, TIFF
•	Tamanho máximo por ficheiro: 10 MB
•	Apenas um ficheiro por submissão
•	O ficheiro é validado no frontend (JavaScript) e no backend (Django Forms) antes de ser aceite

6.2. Regras de Processamento
•	Após upload, o estado transita automaticamente para A_PROCESSAR
•	O Celery processa o documento em background — a interface não bloqueia
•	Se o OCR devolver texto vazio, o estado transita para ERRO com mensagem descritiva
•	Se o LLM não devolver JSON válido, o estado transita para ERRO com o detalhe da resposta
•	Em caso de sucesso, o estado transita para A_VALIDAR e os campos são pré-preenchidos

6.3. Regras de Validação Humana
•	O utilizador pode editar qualquer campo extraído antes de confirmar
•	A confirmação transita o estado para VALIDADO e regista data_validacao
•	Documentos no estado VALIDADO podem ser consultados mas não re-editados
•	Documentos no estado ERRO podem ser submetidos novamente (novo upload)

6.4. Prompt para o LLM
O prompt enviado ao modelo Ollama deve ser estruturado da seguinte forma:

Estrutura do prompt
Analisa o seguinte texto extraído de um documento financeiro e devolve APENAS um objeto JSON
com os seguintes campos. Se não conseguires extrair um campo, usa null.

{
  "nif": "string ou null",
  "data_emissao": "YYYY-MM-DD ou null",
  "valor_total": "decimal ou null",
  "valor_iva": "decimal ou null",
  "tipo_documento": "FATURA | RECIBO | OUTRO",
  "confianca": "valor entre 0.0 e 1.0"
}

Texto a analisar:
[TEXTO_EXTRAIDO_PELO_OCR]





7. Rotas da Aplicação (URLs)
URL	Método	Descrição
/	GET	Redireciona para /upload
/upload	GET	Apresenta o formulário de upload
/upload	POST	Recebe o ficheiro, cria registo e lança tarefa Celery
/documentos	GET	Lista todos os documentos submetidos com estado atual
/documentos/<id>	GET	Detalhe do documento: imagem + dados extraídos + formulário de validação
/documentos/<id>/validar	POST	Guarda os dados corrigidos e transita estado para VALIDADO
/documentos/<id>/estado	GET	Devolve o estado atual em JSON (para polling AJAX)


8. Estrutura de Pastas do Projeto
dicas/
├── dicas/                  # configuração Django (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── documentos/             # app principal
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── tasks.py            # tarefas Celery
│   └── templates/
│       ├── upload.html
│       ├── lista.html
│       └── detalhe.html
├── core_ia/                # pipeline OCR + IA (desacoplado)
│   ├── preprocessor.py     # Pillow + OpenCV
│   ├── ocr.py              # Tesseract
│   └── extractor.py        # Ollama / LLM
├── media/                  # ficheiros submetidos (gitignore)
├── requirements.txt
└── manage.py


9. Ficheiro requirements.txt
django>=5.0
celery>=5.3
redis>=5.0
pytesseract>=0.3.10
Pillow>=10.0
opencv-python>=4.8
ollama>=0.1.0
python-decouple>=3.8        # gestão de variáveis de ambiente
psycopg2-binary>=2.9        # apenas se usar PostgreSQL


10. Plano de Desenvolvimento
Fase	Nome	Tarefas principais
1	Configuração do ambiente	Instalar Python, Django, Tesseract, Ollama, Redis. Configurar projeto Django. Testar Ollama com prompt simples.
2	Pipeline OCR + IA	Desenvolver core_ia/ como script autónomo. Testar com documentos reais. Validar qualidade dos campos extraídos.
3	Integração Django + Celery	Criar models, views, urls, forms. Integrar pipeline como tarefa Celery. Testar processamento assíncrono.
4	Interface de validação	Página de detalhe com imagem + formulário editável. Polling de estado via AJAX. Confirmação e gravação.
5	Avaliação e aprendizagem	Testar com 10-20 documentos reais. Registar taxa de acerto por campo. Documentar conclusões para o SIGAP-ANALISE_PP.


11. Critérios de Sucesso da Prova de Conceito
O DICAS é considerado bem-sucedido se, no final da Fase 5, os seguintes critérios forem atingidos:

•	Taxa de extração correta do NIF superior a 80% nos documentos testados
•	Taxa de extração correta do valor total superior a 85%
•	Tempo de processamento inferior a 30 segundos por documento
•	Interface de validação funcional e utilizável sem erros críticos
•	Conclusões documentadas sobre viabilidade de integração no SIGAP-ANALISE_PP
