from datetime import datetime, date
from typing import Optional, Tuple


def validar_cpf(cpf: str) -> bool:
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False

    # Verifica se todos os dígitos são iguais (CPF inválido)
    if cpf == cpf[0] * 11:
        return False

    # Calcula o primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    # Verifica o primeiro dígito
    if int(cpf[9]) != digito1:
        return False

    # Calcula o segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    # Verifica o segundo dígito
    if int(cpf[10]) != digito2:
        return False

    return True


def validar_data_nao_futura(data: date) -> Tuple[bool, str]:
    """
    Valida se uma data não é futura.

    Args:
        data: Objeto date ou datetime

    Returns:
        Tupla (válido, mensagem_erro)
    """
    hoje = datetime.now().date()
    if isinstance(data, datetime):
        data = data.date()

    if data > hoje:
        return False, "Data não pode ser futura."

    return True, ""


def validar_data_nascimento(data_nascimento: date, data_obito: Optional[date] = None) -> Tuple[bool, str]:
    """
    Valida a data de nascimento.

    Args:
        data_nascimento: Data de nascimento
        data_obito: Data do óbito (opcional, para comparação)

    Returns:
        Tupla (válido, mensagem_erro)
    """
    hoje = datetime.now().date()
    if isinstance(data_nascimento, datetime):
        data_nascimento = data_nascimento.date()

    # Não pode ser futura
    if data_nascimento > hoje:
        return False, "Data de nascimento não pode ser futura."

    # Não pode ter mais de 120 anos
    anos = (hoje - data_nascimento).days / 365.25
    if anos > 120:
        return False, "Data de nascimento indica idade superior a 120 anos."

    # Se houver data de óbito, nascimento deve ser anterior
    if data_obito:
        if isinstance(data_obito, datetime):
            data_obito = data_obito.date()

        if data_nascimento >= data_obito:
            return False, "Data de nascimento deve ser anterior à data do óbito."

    return True, ""


def validar_coordenadas(latitude: float, longitude: float) -> Tuple[bool, str]:
    """
    Valida coordenadas geográficas.

    Args:
        latitude: Valor da latitude
        longitude: Valor da longitude

    Returns:
        Tupla (válido, mensagem_erro)
    """
    if not (-90 <= latitude <= 90):
        return False, "Latitude deve estar entre -90 e 90."

    if not (-180 <= longitude <= 180):
        return False, "Longitude deve estar entre -180 e 180."

    return True, ""


def validar_idade(idade: int) -> Tuple[bool, str]:
    """
    Valida o valor da idade.

    Args:
        idade: Valor da idade

    Returns:
        Tupla (válido, mensagem_erro)
    """
    if idade < 0:
        return False, "Idade não pode ser negativa."

    if idade > 120:
        return False, "Idade não pode ser superior a 120 anos."

    return True, ""


def validar_campo_obrigatorio(valor: any) -> Tuple[bool, str]:
    """
    Valida se um campo obrigatório foi preenchido.

    Args:
        valor: Valor do campo

    Returns:
        Tupla (válido, mensagem_erro)
    """
    if valor is None:
        return False, "Este campo é obrigatório."

    if isinstance(valor, str) and valor.strip() == "":
        return False, "Este campo é obrigatório."

    return True, ""


def validar_n_bos(valor: str) -> Tuple[bool, str]:
    """
    Valida o campo Nº de BOS (deve estar vazio ou ser 1).

    Args:
        valor: Valor do campo Nº de BOS

    Returns:
        Tupla (válido, mensagem_erro)
    """
    if valor.strip() == "":
        return True, ""  # Vazio é válido (vítima adicional)

    try:
        num = float(valor)
        if num == 1.0:
            return True, ""
        else:
            return False, "Nº de BOS deve estar vazio ou ser igual a 1."
    except ValueError:
        return False, "Nº de BOS deve ser um número válido ou estar vazio."


def campos_obrigatorios_preenchidos(dados: dict) -> Tuple[bool, list]:
    """
    Verifica se todos os campos obrigatórios foram preenchidos.

    Args:
        dados: Dicionário com os dados do formulário

    Returns:
        Tupla (todos_preenchidos, lista_campos_vazios)
    """
    campos_obrigatorios = [
        'Natureza da Ocorrência',
        'Nº do BO',
        'Tipo de Acidente',
        'Data do Óbito',
        'Vítima',
        'Sexo',
        'Município do Fato',
        'Data do Fato'
    ]

    campos_vazios = []

    for campo in campos_obrigatorios:
        valor = dados.get(campo)
        valido, _ = validar_campo_obrigatorio(valor)
        if not valido:
            campos_vazios.append(campo)

    return len(campos_vazios) == 0, campos_vazios


def formatar_cpf(cpf: str) -> str:
    """
    Formata um CPF no padrão XXX.XXX.XXX-XX.

    Args:
        cpf: String do CPF (apenas números)

    Returns:
        CPF formatado
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return cpf

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
