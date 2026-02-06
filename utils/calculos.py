from datetime import datetime, date
from typing import Optional
import pandas as pd


def calcular_idade(data_nascimento: date, data_obito: date) -> Optional[int]:
    if not data_nascimento or not data_obito:
        return None

    # Converte datetime para date se necessário
    if isinstance(data_nascimento, datetime):
        data_nascimento = data_nascimento.date()
    if isinstance(data_obito, datetime):
        data_obito = data_obito.date()

    # Calcula a diferença em dias e converte para anos
    dias = (data_obito - data_nascimento).days
    if dias < 0:
        return None

    idade = dias // 365  # Divisão inteira para anos completos
    return idade


def obter_dia_semana(data: date) -> str:

    if not data:
        return ""

    # Converte datetime para date se necessário
    if isinstance(data, datetime):
        data = data.date()

    dias_semana = [
        "SEGUNDA-FEIRA",
        "TERÇA-FEIRA",
        "QUARTA-FEIRA",
        "QUINTA-FEIRA",
        "SEXTA-FEIRA",
        "SÁBADO",
        "DOMINGO"
    ]

    # weekday() retorna 0 (segunda) a 6 (domingo)
    return dias_semana[data.weekday()]


def obter_mes(data: date) -> str:
    if not data:
        return ""

    # Converte datetime para date se necessário
    if isinstance(data, datetime):
        data = data.date()

    meses = [
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

    # month é 1-indexed (1 a 12)
    return meses[data.month - 1]


def formatar_data_para_excel(data: date) -> str:
    if not data:
        return ""

    # Converte datetime para date se necessário
    if isinstance(data, datetime):
        data = data.date()

    return data.strftime("%d/%m/%Y")


def formatar_hora_para_excel(hora: datetime) -> str:
    if not hora:
        return ""

    if isinstance(hora, datetime):
        return hora.strftime("%H:%M")
    else:
        # Assume que é um objeto time
        return hora.strftime("%H:%M")


def parse_data_excel(valor) -> Optional[date]:
    """
    Converte um valor do Excel para objeto date.
    Trata vários formatos possíveis.

    Args:
        valor: Valor lido do Excel (pode ser string, datetime, etc)

    Returns:
        Objeto date ou None se não puder converter
    """
    if pd.isna(valor):
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    if isinstance(valor, str):
        # Tenta vários formatos
        formatos = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]
        for formato in formatos:
            try:
                return datetime.strptime(valor, formato).date()
            except ValueError:
                continue

    return None


def parse_hora_excel(valor) -> Optional[str]:
    """
    Converte um valor do Excel para string de hora HH:mm.

    Args:
        valor: Valor lido do Excel

    Returns:
        String HH:mm ou None se não puder converter
    """
    if pd.isna(valor):
        return None

    if isinstance(valor, datetime):
        return valor.strftime("%H:%M")

    if isinstance(valor, str):
        # Já é string, apenas garante formato HH:mm
        try:
            partes = valor.split(":")
            if len(partes) >= 2:
                return f"{int(partes[0]):02d}:{int(partes[1]):02d}"
        except:
            pass

    return None


def validar_hora(hora_str: str) -> bool:
    try:
        partes = hora_str.split(":")
        if len(partes) != 2:
            return False

        horas = int(partes[0])
        minutos = int(partes[1])

        return 0 <= horas <= 23 and 0 <= minutos <= 59
    except:
        return False
