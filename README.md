# Sistema de Cadastro de Mortes no Transito

Aplicacao desktop em Python com PyQt6 para cadastrar mortes no transito, com suporte para **Excel Local** ou **Google Sheets** em tempo real, e sincronizacao com **MySQL**.

## Caracteristicas Principais

- Interface grafica moderna e intuitiva com PyQt6
- **Dois modos de operacao**:
  - **Excel Local**: Trabalhe com arquivos .xlsx offline
  - **Google Sheets**: Atualizacoes em tempo real na nuvem
- Formulario com 29 campos ativos organizados em 7 abas
- Calculos automaticos de idade, dia da semana e mes
- Validacao de dados em tempo real
- Insercao ordenada automatica por Data do Fato
- **Sincronizacao com MySQL**

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

## Requisitos

- Python 3.10 ou superior
- MySQL 8.0 ou superior
- Windows, macOS ou Linux
- Conexao com internet (apenas para modo Google Sheets)

## Instalacao

### 1. Clone o projeto

```bash
git clone https://github.com/mateus-pcosta/mortes-transito.git
cd mortes-transito
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
- mysql-connector-python (MySQL)
- python-dotenv (variaveis de ambiente)

### 3. Configure o banco de dados MySQL

```bash
mysql -u root -p < setup_database.sql
```

Isso cria o banco `mortes_transito` com todas as tabelas e dados iniciais.

### 4. Configure o arquivo .env

Copie o exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o `.env` com seus dados de acesso ao MySQL.

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

- **Boletim** - Tipo de Acidente (demais campos desativados)
- **Laudo** - Informacoes do Laudo IML
- **Vitima** - Dados da Vitima
- **Localizacao** - Localizacao do Acidente
- **Data e Hora** - Data e Hora do Fato
- **Veiculos** - Veiculos e Local da Morte
- **Territorial** - Classificacao Territorial

## Banco de Dados MySQL

### Estrutura

O banco `mortes_transito` possui 5 tabelas:

- **ocorrencias** - Dados do fato (data, hora, local, tipo de acidente)
- **vitimas** - Dados da vitima (nome, idade, CPF, laudo)
- **tipos_acidente** - Lookup de tipos de acidente (10 opcoes)
- **tipos_veiculo** - Lookup de tipos de veiculo (18 opcoes)
- **municipios** - Lookup de municipios

### Diagrama simplificado

```
ocorrencias (1) ----< (N) vitimas
     |                        |
     |-> tipos_acidente       |-> tipos_veiculo (vitima)
     |-> municipios           |-> tipos_veiculo (envolvido)
```

## Campos Calculados Automaticamente

- **Idade**: Calculada a partir de Data de Nascimento e Data do Obito
- **Dia da Semana**: Calculado a partir da Data do Fato
- **Mes**: Calculado a partir da Data do Fato

## Campos Obrigatorios

1. Tipo de Acidente
2. Data do Obito
3. Vitima (Nome Completo)
4. Sexo
5. Municipio do Fato
6. Data do Fato

## Estrutura do Projeto

```
projeto/
|
|-- main.py                       # Inicializacao
|-- requirements.txt              # Dependencias
|-- setup_database.sql            # Script de criacao do MySQL
|-- README.md                     # Este arquivo
|-- .env.example                  # Template de variaveis de ambiente
|-- .gitignore                    # Arquivos ignorados pelo git
|
|-- interface/                    # Interfaces graficas
|   |-- tela_selecao_modo.py     # Escolha Excel/Sheets
|   |-- tela_cadastro.py         # Formulario (7 abas)
|   |-- tela_confirmacao.py      # Confirmacao
|
|-- utils/                        # Utilitarios
    |-- excel_handler.py          # Handler Excel
    |-- sheets_handler.py         # Handler Google Sheets
    |-- database_handler.py       # Handler MySQL
    |-- validacoes.py             # Validacoes
    |-- calculos.py               # Calculos automaticos
    |-- dados_estaticos.py        # Dados pre-definidos
```

## Seguranca

- Credenciais armazenadas em `.env` (nunca commitado)
- Arquivo `credentials/` protegido pelo `.gitignore`
- Senhas e chaves privadas nunca expostas no repositorio

## Configuracao do Google Sheets

Para usar o modo Google Sheets:

1. Criar um projeto no Google Cloud Console
2. Ativar Google Sheets API e Google Drive API
3. Criar uma Service Account
4. Baixar arquivo de credenciais JSON para `credentials/`
5. Compartilhar planilha com o email da Service Account

---

**Versao**: 3.1 (Publica)
**Ultima atualizacao**: Fevereiro 2026
**Desenvolvido com**: Python 3, PyQt6, pandas, openpyxl, gspread, MySQL
