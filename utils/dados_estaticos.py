COLUNAS_EXCEL = [
    "Natureza da Ocorrência",
    "Tipo de Acidente",
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

NATUREZA_LAUDO = [
    "Exame cadavérico - Acidente de Tráfego",
    "Exame cadavérico - Outros",
    "Exame Pericial em Local de Ocorrência",
    "Exame em Local de Oc. Tráfego",
    "Carbonização",
    "NI",
    "Outro"
]

SEXO = [
    "Masculino",
    "Feminino"
]

POSSUI_CNH = [
    "Sim",
    "Não",
    "NI"
]

CONDUTOR = [
    "Sim",
    "Não",
    "NI"
]

EXAME_ALCOOLEMIA = [
    "Sim",
    "NI"
]

USANDO_CAPACETE = [
    "Sim",
    "Não",
    "NI"
]

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

REGIAO = [
    "Capital",
    "Metropolitana",
    "Interior",
    "Litoral",
    "NI"
]

DIAS_SEMANA = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
    "SÁBADO",
    "DOMINGO"
]

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

COLORS = {
    'primary': '#2C3E50',     
    'secondary': '#3498DB',   
    'success': '#27AE60',      
    'warning': '#F39C12',      
    'danger': '#E74C3C',       
    'info': '#95A5A6',         
    'background': '#ECF0F1',  
    'text': '#2C3E50',        
    'auto_field': '#BDC3C7'    
}

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

    import pandas as pd

    try:
        df = pd.read_excel(caminho_excel)

        dados = {
            'municipios': sorted(df['Município do Fato'].dropna().unique().tolist()),
            'natureza_ocorrencia': sorted(df['Natureza da Ocorrência'].dropna().unique().tolist()),
            'locais_morte': sorted(df['Local da Morte'].dropna().unique().tolist()),
            'territorios': sorted(df['Território de\nDesenvolvimento'].dropna().unique().tolist())
        }

        return dados
    except Exception as e:
        print(f"Erro ao carregar dados da planilha: {e}")
        return {
            'municipios': [],
            'natureza_ocorrencia': [],
            'locais_morte': [],
            'territorios': []
        }
