import pandas as pd
from typing import Tuple, Optional
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from .dados_estaticos import COLUNAS_EXCEL
from .calculos import parse_data_excel


class SheetsHandler:

    def __init__(self, credentials_path: str = None, spreadsheet_url: str = None):
        """
        Inicializa o handler do Google Sheets.

        Args:
            credentials_path: Caminho para o arquivo JSON de credenciais
            spreadsheet_url: URL da planilha do Google Sheets
        """
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.caminho_arquivo = spreadsheet_url  # Alias para compatibilidade com ExcelHandler
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.worksheets_por_ano = {}  # Dicionário para armazenar worksheets por ano
        self.df = None
        self.dados_carregados = False
        self.ano_atual = None  # Ano da aba atualmente carregada

    def autenticar(self) -> Tuple[bool, str]:
        """
        Autentica com a API do Google Sheets.

        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            # Define os escopos necessários
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            # Carrega as credenciais
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=scopes
            )

            # Cria o cliente
            self.client = gspread.authorize(creds)

            return True, "Autenticação realizada com sucesso!"

        except FileNotFoundError:
            return False, f"Arquivo de credenciais não encontrado: {self.credentials_path}"
        except Exception as e:
            return False, f"Erro na autenticação: {str(e)}"

    def carregar_planilha(self, spreadsheet_url: str = None) -> Tuple[bool, str]:
        """
        Carrega a planilha do Google Sheets e todas as abas de anos (2024, 2025, 2026).

        Args:
            spreadsheet_url: URL da planilha (se None, usa a URL do construtor)

        Returns:
            Tupla (sucesso, mensagem)
        """
        if spreadsheet_url:
            self.spreadsheet_url = spreadsheet_url

        if not self.client:
            return False, "Cliente não autenticado. Execute autenticar() primeiro."

        try:
            # Abre a planilha pela URL
            self.spreadsheet = self.client.open_by_url(self.spreadsheet_url)

            # Carrega todas as abas de anos disponíveis
            anos_disponiveis = ['2024', '2025', '2026']
            total_registros_geral = 0

            for ano in anos_disponiveis:
                try:
                    worksheet = self.spreadsheet.worksheet(ano)
                    self.worksheets_por_ano[ano] = worksheet

                    # Carrega dados da aba
                    dados = worksheet.get_all_values()
                    if dados and len(dados) > 1:
                        total_registros_geral += len(dados) - 1  # -1 para excluir cabeçalho

                except gspread.exceptions.WorksheetNotFound:
                    # Se a aba do ano não existir, ignora
                    pass

            if not self.worksheets_por_ano:
                return False, "Nenhuma aba de ano (2024, 2025, 2026) encontrada na planilha."

            # Define a aba do ano atual como padrão (2026 se existir, senão o mais recente)
            if '2026' in self.worksheets_por_ano:
                self.ano_atual = '2026'
            else:
                self.ano_atual = max(self.worksheets_por_ano.keys())

            self.worksheet = self.worksheets_por_ano[self.ano_atual]

            # Carrega dados da aba atual em DataFrame
            dados = self.worksheet.get_all_values()

            if not dados:
                return False, "Planilha vazia."

            # Cria DataFrame
            self.df = pd.DataFrame(dados[1:], columns=dados[0])

            # Valida colunas (aceita 32 ou 33 colunas)
            num_colunas = len(self.df.columns)
            if num_colunas < 32 or num_colunas > 33:
                return False, f"Planilha possui {num_colunas} colunas. Esperado: 32 ou 33 colunas."

            # Verifica estrutura das colunas (flexível)
            colunas_planilha = [col.strip() for col in self.df.columns]
            colunas_esperadas = [col.strip() for col in COLUNAS_EXCEL]

            # Se a planilha tem 32 colunas, verifica qual está faltando e adiciona
            if num_colunas == 32:
                # Encontra as colunas que faltam
                colunas_faltantes = []
                for col_esperada in colunas_esperadas:
                    if col_esperada not in colunas_planilha:
                        colunas_faltantes.append(col_esperada)

                # Adiciona colunas faltantes ao DataFrame
                for col_faltante in colunas_faltantes:
                    self.df[col_faltante] = ''

                # Reordena as colunas para corresponder à ordem esperada
                self.df = self.df[colunas_esperadas]

            self.dados_carregados = True

            # Normaliza as datas existentes na planilha para dd/mm/yyyy
            self._normalizar_datas_dataframe()

            anos_carregados = ', '.join(sorted(self.worksheets_por_ano.keys()))

            return True, f"Planilha carregada com sucesso!\nAbas encontradas: {anos_carregados}\nTotal: {total_registros_geral} registros."

        except gspread.exceptions.SpreadsheetNotFound:
            return False, "Planilha não encontrada. Verifique a URL e as permissões."
        except gspread.exceptions.APIError as e:
            return False, f"Erro na API do Google: {str(e)}"
        except Exception as e:
            return False, f"Erro ao carregar planilha: {str(e)}"

    def obter_info_arquivo(self) -> dict:
        """
        Retorna informações sobre a planilha carregada.
        Alias para obter_info_planilha() para compatibilidade com ExcelHandler.

        Returns:
            Dicionário com informações da planilha
        """
        return self.obter_info_planilha()

    def obter_info_planilha(self) -> dict:
        """
        Retorna informações sobre a planilha carregada.

        Returns:
            Dicionário com informações da planilha
        """
        if not self.dados_carregados or self.df is None:
            return {
                'total_registros': 0,
                'ultima_data': None,
                'municipios_unicos': 0,
                'nome_planilha': None
            }

        # Processa a última data
        ultima_data = None
        if 'Data do Fato' in self.df.columns:
            datas_validas = self.df['Data do Fato'].dropna()
            if len(datas_validas) > 0:
                ultima_data_valor = datas_validas.iloc[-1]
                ultima_data = parse_data_excel(ultima_data_valor)

        return {
            'total_registros': len(self.df),
            'ultima_data': ultima_data,
            'municipios_unicos': self.df['Município do Fato'].nunique(),
            'nome_planilha': self.spreadsheet.title if self.spreadsheet else None
        }

    def inserir_registro(self, dados: dict) -> Tuple[bool, str, int]:
        """
        Insere um novo registro na planilha correta baseado no ano da Data do Fato.

        Args:
            dados: Dicionário com os dados do novo registro

        Returns:
            Tupla (sucesso, mensagem, posicao_inserida)
        """
        if not self.dados_carregados:
            return False, "Nenhuma planilha carregada.", -1

        try:
            # Converte dados para formato compatível com DataFrame
            dados_formatados = self._formatar_dados_para_sheets(dados)

            # Extrai o ano da Data do Fato
            ano_registro = self._extrair_ano_data(dados_formatados.get('Data do Fato', ''))

            if not ano_registro:
                return False, "Não foi possível determinar o ano da Data do Fato.", -1

            # Verifica se existe aba para este ano
            if ano_registro not in self.worksheets_por_ano:
                return False, f"Não existe aba para o ano {ano_registro}. Abas disponíveis: {', '.join(sorted(self.worksheets_por_ano.keys()))}", -1

            # Carrega a aba correta baseada no ano
            self._carregar_aba_ano(ano_registro)

            # Cria um novo registro como DataFrame
            novo_registro = pd.DataFrame([dados_formatados])

            # Adiciona ao DataFrame existente
            self.df = pd.concat([self.df, novo_registro], ignore_index=True)

            # Normaliza todas as datas para formato dd/mm/yyyy antes de ordenar
            self._normalizar_datas_dataframe()

            # Converte coluna de data para ordenação
            df_temp = self.df.copy()
            df_temp['Data do Fato_sort'] = pd.to_datetime(
                df_temp['Data do Fato'],
                format='%d/%m/%Y',
                errors='coerce'
            )

            # Ordena por Data do Fato
            df_temp = df_temp.sort_values(by='Data do Fato_sort', ascending=True)
            df_temp = df_temp.drop('Data do Fato_sort', axis=1)
            df_temp = df_temp.reset_index(drop=True)

            # Substitui o DataFrame original
            self.df = df_temp

            # Atualiza a planilha no Google Sheets
            sucesso_update = self._atualizar_sheets()

            if not sucesso_update:
                return False, "Erro ao atualizar Google Sheets.", -1

            # Encontra a posição onde o registro foi inserido
            posicao = self._encontrar_posicao_registro(dados_formatados)

            return True, f"Registro inserido com sucesso na aba {ano_registro}!", posicao

        except Exception as e:
            return False, f"Erro ao inserir registro: {str(e)}", -1

    def _normalizar_datas_dataframe(self):
        """
        Normaliza todas as datas no DataFrame para o formato dd/mm/yyyy.
        Detecta e corrige datas em formatos variados (yyyy-mm-dd, mm/dd/yyyy, etc).
        """
        import re

        # Se DataFrame vazio, não faz nada
        if self.df is None or len(self.df) == 0:
            return

        # Colunas que contêm datas
        colunas_data = ['Data do Fato', 'Data de Nascimento', 'Data do Óbito']

        for coluna in colunas_data:
            if coluna not in self.df.columns:
                continue

            for idx, valor in self.df[coluna].items():
                if not valor or pd.isna(valor):
                    continue

                valor_str = str(valor).strip()
                if not valor_str:
                    continue

                # Tenta detectar o formato da data
                data_normalizada = None

                # Formato yyyy-mm-dd ou yyyy/mm/dd (ISO)
                if re.match(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', valor_str):
                    try:
                        dt = pd.to_datetime(valor_str, errors='coerce')
                        if not pd.isna(dt):
                            data_normalizada = dt.strftime('%d/%m/%Y')
                    except:
                        pass

                # Formato dd/mm/yyyy (já correto)
                elif re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', valor_str):
                    partes = valor_str.split('/')
                    if len(partes) == 3:
                        dia, mes, ano = partes
                        # Verifica se é dd/mm/yyyy ou mm/dd/yyyy
                        if int(dia) > 12:  # Definitivamente dd/mm/yyyy
                            data_normalizada = f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
                        elif int(mes) > 12:  # Definitivamente mm/dd/yyyy
                            data_normalizada = f"{mes.zfill(2)}/{dia.zfill(2)}/{ano}"
                        else:  # Ambíguo - tenta parsear como dd/mm/yyyy
                            try:
                                dt = pd.to_datetime(valor_str, format='%d/%m/%Y', errors='coerce')
                                if not pd.isna(dt):
                                    data_normalizada = dt.strftime('%d/%m/%Y')
                            except:
                                # Se falhar, tenta mm/dd/yyyy
                                try:
                                    dt = pd.to_datetime(valor_str, format='%m/%d/%Y', errors='coerce')
                                    if not pd.isna(dt):
                                        data_normalizada = dt.strftime('%d/%m/%Y')
                                except:
                                    pass

                # Se conseguiu normalizar, atualiza
                if data_normalizada:
                    self.df.at[idx, coluna] = data_normalizada

    def _formatar_dados_para_sheets(self, dados: dict) -> dict:
        """
        Formata os dados para o formato do Google Sheets (strings).

        Args:
            dados: Dicionário com dados originais

        Returns:
            Dicionário formatado
        """
        dados_formatados = {}

        for coluna, valor in dados.items():
            # Converte datas para string dd/mm/yyyy
            if isinstance(valor, (datetime, pd.Timestamp)):
                dados_formatados[coluna] = valor.strftime('%d/%m/%Y')
            elif pd.isna(valor) or valor is None:
                dados_formatados[coluna] = ''
            # Converte números inteiros (remove .0)
            elif isinstance(valor, (int, float)):
                # Se for um número inteiro, remove o .0
                if isinstance(valor, float) and valor.is_integer():
                    dados_formatados[coluna] = str(int(valor))
                else:
                    dados_formatados[coluna] = str(valor)
            else:
                dados_formatados[coluna] = str(valor)

        return dados_formatados

    def _atualizar_sheets(self) -> bool:
        """
        Atualiza o Google Sheets com os dados do DataFrame.

        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Limpa a planilha
            self.worksheet.clear()

            # Prepara dados para atualização
            dados_para_sheets = [self.df.columns.tolist()] + self.df.values.tolist()

            # Converte todos os valores para string com formatação adequada
            dados_formatados = []
            for row in dados_para_sheets:
                row_formatada = []
                for cell in row:
                    if cell is None or (isinstance(cell, float) and pd.isna(cell)):
                        row_formatada.append('')
                    elif isinstance(cell, (int, float)):
                        # Remove .0 de números inteiros
                        if isinstance(cell, float) and cell.is_integer():
                            row_formatada.append(str(int(cell)))
                        else:
                            row_formatada.append(str(cell))
                    else:
                        row_formatada.append(str(cell))
                dados_formatados.append(row_formatada)

            # Atualiza a planilha
            self.worksheet.update('A1', dados_formatados)

            return True

        except Exception as e:
            print(f"Erro ao atualizar sheets: {e}")
            return False

    def _encontrar_posicao_registro(self, dados: dict) -> int:
        """
        Encontra a posição de um registro no DataFrame.

        Args:
            dados: Dados do registro

        Returns:
            Posição (linha) do registro
        """
        try:
            for idx, row in self.df.iterrows():
                if (row['Vítima'] == dados.get('Vítima') and
                    row['Data do Fato'] == dados.get('Data do Fato')):
                    return idx + 2  # +2 porque Excel começa em 1 e tem cabeçalho
            return -1
        except:
            return -1

    def obter_valores_unicos(self, coluna: str) -> list:
        """
        Retorna valores únicos de uma coluna específica.

        Args:
            coluna: Nome da coluna

        Returns:
            Lista de valores únicos ordenados
        """
        if not self.dados_carregados or coluna not in self.df.columns:
            return []

        valores = self.df[coluna].dropna().unique().tolist()
        return sorted([v for v in valores if v != ''])

    def obter_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Retorna o DataFrame atual.

        Returns:
            DataFrame ou None se não houver dados
        """
        return self.df if self.dados_carregados else None

    def _extrair_ano_data(self, data_str: str) -> Optional[str]:
        """
        Extrai o ano de uma string de data no formato dd/mm/yyyy.

        Args:
            data_str: String de data no formato dd/mm/yyyy

        Returns:
            Ano como string ou None se não conseguir extrair
        """
        try:
            if not data_str or data_str.strip() == '':
                return None

            # Formato dd/mm/yyyy
            partes = data_str.split('/')
            if len(partes) == 3:
                ano = partes[2]
                return ano

            return None
        except:
            return None

    def _carregar_aba_ano(self, ano: str):
        """
        Carrega os dados de uma aba específica de ano.

        Args:
            ano: Ano da aba a ser carregada (ex: '2024', '2025', '2026')
        """
        if ano not in self.worksheets_por_ano:
            raise ValueError(f"Aba para o ano {ano} não encontrada.")

        # Atualiza a worksheet atual
        self.worksheet = self.worksheets_por_ano[ano]
        self.ano_atual = ano

        # Carrega dados da aba
        dados = self.worksheet.get_all_values()

        if not dados:
            # Se a aba estiver vazia, cria DataFrame vazio com as colunas esperadas
            self.df = pd.DataFrame(columns=COLUNAS_EXCEL)
        else:
            # Cria DataFrame com os dados
            self.df = pd.DataFrame(dados[1:], columns=dados[0])

        # Normaliza as datas existentes
        self._normalizar_datas_dataframe()
