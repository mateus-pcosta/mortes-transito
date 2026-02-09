# Nomes das colunas do Excel (exatamente como aparecem na planilha)
COLUNAS_EXCEL = [
    "Tipo de Acidente",
    "Nº Laudo IML",
    "Natureza do Laudo",
    "Data do Óbito",
    "Vítima",
    "Sexo",
    "Filiação",
    "Data de\nNascimento",
    "Idade",
    "CPF",
    "Possui\nCNH",
    "Condutor",
    "Realizado Exame\nAlcoolemia",
    "Estava usando\nCapacete",
    "Município do Fato",
    "Logradouro",
    "Subtipo do Local",
    "Lat",
    "Long",
    "Data do Fato",
    "Hora do fato",
    "Dia da Semana",
    "Mês",
    "Local da Morte",
    "Veículo Vítima\nOu Outros",
    "Veículo Envolvido\nOu Outros",
    "Região",
    "Território de\nDesenvolvimento",
    "OBS:"
]

# Tipos de Acidente
TIPO_ACIDENTE = [
    "Atropelamento",
    "Atropelamento com Animais",
    "Capotamento",
    "Choque",
    "Colisão",
    "Colisão/Animal",
    "Queda",
    "Tombamento",
    "NI",
    "Outro"
]

# Natureza do Laudo
NATUREZA_LAUDO = [
    "Exame cadavérico - Acidente de Tráfego",
    "Exame cadavérico - Outros",
    "Exame Pericial em Local de Ocorrência",
    "Exame em Local de Oc. Tráfego",
    "Carbonização",
    "NI",
    "Outro"
]

# Sexo
SEXO = [
    "Masculino",
    "Feminino"
]

# Possui CNH
POSSUI_CNH = [
    "Sim",
    "Não",
    "NI"
]

# Condutor
CONDUTOR = [
    "Sim",
    "Não",
    "NI"
]

# Realizado Exame Alcoolemia
EXAME_ALCOOLEMIA = [
    "Sim",
    "NI"
]

# Estava usando Capacete
USANDO_CAPACETE = [
    "Sim",
    "Não",
    "NI"
]

# Subtipo do Local
SUBTIPO_LOCAL = [
    "Rua",
    "Avenida",
    "Rodovia Federal",
    "Rodovia Estadual",
    "Estrada de Terra",
    "Estrada Vicinal",
    "Zona Rural",
    "Povoado",
    "Via Pública",
    "Praça",
    "NI",
    "Outro"
]

# Veículos (para Vítima e Envolvido)
VEICULOS_VITIMA = [
    "Motocicleta",
    "Carro/Automóvel",
    "Pedestre",
    "Bicicleta",
    "Caminhão",
    "Ônibus",
    "Carroça",
    "Animal/Cavalo",
    "NI",
    "Outro"
]

VEICULOS_ENVOLVIDO = [
    # Veículos
    "Motocicleta",
    "Carro/Automóvel",
    "Caminhão",
    "Ônibus",
    "Bicicleta",
    "Van",
    "Trator",
    # Obstáculos
    "Choque/Poste",
    "Choque/Árvore",
    "Choque/Muro",
    "Colisão/Ponte",
    # Animais
    "Animal/Cavalo",
    "Animal/Gado",
    "Animal/Cachorro",
    # Outros
    "Capotamento",
    "Queda",
    "Tombamento",
    "NI"
]

# Região
REGIAO = [
    "Capital",
    "Metropolitana",
    "Interior",
    "Litoral",
    "NI"
]

# Dias da Semana (em maiúsculas como na planilha)
DIAS_SEMANA = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
    "SÁBADO",
    "DOMINGO"
]

# Meses (em maiúsculas como na planilha)
MESES = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO"
]

# Paleta de Cores para a interface
COLORS = {
    'primary': '#2C3E50',      # Azul escuro
    'secondary': '#3498DB',    # Azul claro
    'success': '#27AE60',      # Verde
    'warning': '#F39C12',      # Amarelo
    'danger': '#E74C3C',       # Vermelho
    'info': '#95A5A6',         # Cinza
    'background': '#ECF0F1',   # Cinza claro
    'text': '#2C3E50',         # Texto escuro
    'auto_field': '#BDC3C7'    # Campos automáticos (read-only)
}

# Mensagens de erro
ERROS = {
    'arquivo_invalido': "Arquivo Excel inválido. Verifique se contém as 29 colunas necessárias.",
    'data_futura': "Data não pode ser futura.",
    'cpf_invalido': "CPF inválido. Verifique os dígitos.",
    'campo_obrigatorio': "Este campo é obrigatório.",
    'data_inconsistente': "Data de nascimento deve ser anterior à data do óbito.",
    'coordenadas_invalidas': "Coordenadas fora do intervalo válido.",
    'salvamento_erro': "Erro ao salvar arquivo. Verifique permissões.",
    'idade_invalida': "Idade deve estar entre 0 e 120 anos.",
    'arquivo_nao_selecionado': "Nenhum arquivo foi selecionado."
}


def carregar_dados_da_planilha(caminho_excel):
    """
    Carrega dados unicos da planilha existente para popular os comboboxes.
    Retorna dicionario com listas de valores unicos.
    """
    import pandas as pd

    try:
        df = pd.read_excel(caminho_excel)

        dados = {
            'municipios': sorted(df['Município do Fato'].dropna().unique().tolist()),
            'locais_morte': sorted(df['Local da Morte'].dropna().unique().tolist()),
            'territorios': sorted(df['Território de\nDesenvolvimento'].dropna().unique().tolist())
        }

        return dados
    except Exception as e:
        print(f"Erro ao carregar dados da planilha: {e}")
        return {
            'municipios': [],
            'locais_morte': [],
            'territorios': []
        }
