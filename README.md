# Sistema de Cadastro de Mortes no Transito

Aplicacao desktop em Python com PyQt6 para cadastrar mortes no transito, com suporte para **Excel Local** ou **Google Sheets** em tempo real.

## Caracteristicas Principais

- Interface grafica moderna e intuitiva com PyQt6
- **Dois modos de operacao**:
  - **Excel Local**: Trabalhe com arquivos .xlsx offline
  - **Google Sheets**: Atualizacoes em tempo real na nuvem
- Formulario completo com 33 campos organizados em 7 abas
- Calculos automaticos de idade, dia da semana e mes
- Validacao de dados em tempo real
- Insercao ordenada automatica por Data do Fato
- **Sincronizacao com PostgreSQL** da SSP

## Modos de Operacao

### Excel Local
- Trabalhe offline com arquivos .xlsx
- Controle total sobre seus arquivos
- Download manual da planilha atualizada

### Google Sheets
- **Atualizacao instantanea** na nuvem
- Acesso de qualquer lugar
- Compartilhamento facilitado com equipe
- Sem necessidade de download

**[Guia de Configuracao do Google Sheets](GOOGLE_SHEETS_CONFIG.md)**

## Requisitos

- Python 3.10 ou superior
- Windows, macOS ou Linux
- Conexao com internet (apenas para modo Google Sheets)
- VPN Tailscale conectada (para sincronizacao com PostgreSQL)

## Instalacao

### 1. Clone ou baixe o projeto

```bash
cd SSP-autom.relat
```

### 2. Instale as dependencias

```bash
pip install -r requirements.txt
```

**Dependencias incluidas**:
- PyQt6 (interface grafica)
- pandas (manipulacao de dados)
- openpyxl (Excel local)
- gspread + google-auth (Google Sheets)
- psycopg2-binary (PostgreSQL)

## Como Usar

### Execute a aplicacao

```bash
python main.py
```

### Escolha o Modo

Na tela inicial, escolha entre:

1. **Arquivo Excel Local**
   - Clique em "Selecionar Arquivo Excel"
   - Escolha seu arquivo .xlsx
   - Cadastre normalmente
   - Baixe a planilha atualizada

2. **Google Sheets Online**
   - Clique em "Conectar ao Google Sheets"
   - Configure credenciais (primeira vez)
   - Insira URL da planilha
   - Cadastros sao salvos instantaneamente

### Preencha o Formulario

O formulario esta organizado em 7 abas:

- **Boletim** - Informacoes do Boletim de Ocorrencia
- **Laudo** - Informacoes do Laudo IML
- **Vitima** - Dados da Vitima
- **Localizacao** - Localizacao do Acidente
- **Data e Hora** - Data e Hora do Fato
- **Veiculos** - Veiculos e Local da Morte
- **Territorial** - Classificacao Territorial

## Configuracao do Google Sheets

Para usar o modo Google Sheets, voce precisa:

1. Criar um projeto no Google Cloud Console
2. Ativar Google Sheets API e Google Drive API
3. Criar uma Service Account
4. Baixar arquivo de credenciais JSON
5. Compartilhar planilha com o email da Service Account

**Guia completo**: [GOOGLE_SHEETS_CONFIG.md](GOOGLE_SHEETS_CONFIG.md)

## Sincronizacao com PostgreSQL

Ao salvar um registro, os dados sao enviados automaticamente para o banco PostgreSQL da SSP:

- **Banco**:
- **Schema**: transito
- **Tabelas**: 
- **Requisito**: VPN Tailscale conectada

## Campos Calculados Automaticamente

- **Idade**: Calculada a partir de Data de Nascimento e Data do Obito
- **Dia da Semana**: Calculado a partir da Data do Fato
- **Mes**: Calculado a partir da Data do Fato

## Campos Obrigatorios

1. Natureza da Ocorrencia
2. N do BO
3. Tipo de Acidente
4. Data do Obito
5. Vitima (Nome Completo)
6. Sexo
7. Municipio do Fato
8. Data do Fato

## Estrutura do Projeto

```
projeto/
|
|-- main.py                       # Inicializacao
|-- requirements.txt              # Dependencias
|-- README.md                     # Este arquivo
|-- config_sheets.txt             # Configuracoes Google Sheets
|
|-- credentials/                  # Credenciais Google
|   |-- mortes-transito-credentials.json
|
|-- interface/                    # Interfaces graficas
|   |-- tela_selecao_modo.py     # Escolha Excel/Sheets
|   |-- tela_cadastro.py         # Formulario
|   |-- tela_confirmacao.py      # Confirmacao
|
|-- utils/                        # Utilitarios
    |-- excel_handler.py          # Handler Excel
    |-- sheets_handler.py         # Handler Google Sheets
    |-- database_handler.py       # Handler PostgreSQL
    |-- validacoes.py             # Validacoes
    |-- calculos.py               # Calculos
    |-- dados_estaticos.py        # Dados pre-definidos
```

## Comparacao: Excel vs Google Sheets

| Caracteristica | Excel Local | Google Sheets |
|----------------|-------------|---------------|
| **Atualizacoes** | Manual | Instantanea |
| **Acesso** | Apenas no PC | Qualquer lugar |
| **Internet** | Nao necessaria | Necessaria |
| **Compartilhamento** | Enviar arquivo | Link compartilhado |
| **Backup** | Manual | Automatico |
| **Setup** | Simples | Requer configuracao |

## Seguranca

### Google Sheets
- **NUNCA** compartilhe seu arquivo `credentials.json`
- Mantenha as credenciais em local seguro
- Revogue acesso de Service Accounts antigas
- Use permissoes minimas necessarias

### PostgreSQL
- Credenciais armazenadas de forma segura
- Conexao via VPN Tailscale (criptografada)
- Usuario com permissoes controladas

### Excel Local
- Faca backup regular dos arquivos
- Armazene em local seguro

## Troubleshooting

### Modo Excel

**Erro ao abrir arquivo**
- Verifique se nao esta aberto em outro programa
- Confirme que tem 33 colunas

**Erro ao salvar**
- Feche o arquivo se estiver aberto
- Verifique permissoes de escrita

### Modo Google Sheets

**Erro de autenticacao**
- Verifique caminho do credentials.json
- Confirme que APIs estao ativadas

**Planilha nao encontrada**
- Verifique URL da planilha
- Confirme permissoes de compartilhamento

**API Error 403**
- Service Account nao tem permissao
- Compartilhe planilha com email da Service Account

### PostgreSQL

**Erro de conexao**
- Verifique se o Tailscale VPN esta conectado
- Confirme que o host ssp-geo01 esta acessivel

**Erro de autenticacao**
- Verifique usuario e senha do banco

## Novidades da Versao 3.0

- Sincronizacao automatica com PostgreSQL (SSP)
- Suporte a multiplas abas por ano (2024, 2025, 2026)
- Deteccao automatica do ano pela Data do Fato
- Mapeamento inteligente de campos para banco relacional
- Lookups automaticos (municipio, tipo acidente, veiculo, natureza)

## Versoes Anteriores

### Versao 2.0
- Suporte ao Google Sheets
- Tela de selecao de modo
- Atualizacao em tempo real
- Interface modernizada

---

**Versao**: 3.0
**Ultima atualizacao**: Fevereiro 2026
**Desenvolvido com**: Python 3, PyQt6, pandas, openpyxl, gspread, psycopg2
**Desenvolvido para**: SSP-PI - Secretaria de Seguranca Publica do Piaui
