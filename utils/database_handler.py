import mysql.connector
from typing import Tuple, Optional
from datetime import datetime, date, time
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseHandler:

    def __init__(self, config: dict = None):
        self.config = config or self._carregar_config()
        self.connection = None
        self.cursor = None

        # Cache para lookups
        self._cache_natureza = {}
        self._cache_tipo_acidente = {}
        self._cache_tipo_veiculo = {}
        self._cache_municipio = {}

    def _carregar_config(self) -> dict:
        config = {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }

        campos_faltantes = [k for k, v in config.items() if v is None and k != 'port']
        if campos_faltantes:
            raise ValueError(
                f"Variaveis de ambiente nao configuradas: {', '.join(campos_faltantes)}. "
                f"Verifique o arquivo .env"
            )

        return config

    def conectar(self) -> Tuple[bool, str]:
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                connect_timeout=15
            )
            self.cursor = self.connection.cursor()

            self._carregar_caches()

            return True, "Conexao com MySQL estabelecida!"

        except mysql.connector.Error as e:
            return False, f"Erro de conexao: {e}"
        except Exception as e:
            return False, f"Erro ao conectar: {str(e)}"

    def _carregar_caches(self):
        try:
            # Cache natureza_ocorrencia
            self.cursor.execute("SELECT id, descricao FROM naturezas_ocorrencia")
            for id_val, descricao in self.cursor.fetchall():
                self._cache_natureza[descricao.strip().lower()] = id_val

            # Cache tipo_acidente
            self.cursor.execute("SELECT id, descricao FROM tipos_acidente")
            for id_val, descricao in self.cursor.fetchall():
                self._cache_tipo_acidente[descricao.strip().lower()] = id_val

            # Cache tipo_veiculo
            self.cursor.execute("SELECT id, descricao FROM tipos_veiculo")
            for id_val, descricao in self.cursor.fetchall():
                self._cache_tipo_veiculo[descricao.strip().lower()] = id_val

            # Cache municipios
            self.cursor.execute("SELECT id, nome FROM municipios")
            for id_val, nome in self.cursor.fetchall():
                if nome:
                    self._cache_municipio[nome.strip().lower()] = id_val

        except Exception as e:
            print(f"Aviso: Erro ao carregar caches: {e}")

    def inserir_registro(self, dados: dict) -> Tuple[bool, str]:

        if not self.connection:
            sucesso, msg = self.conectar()
            if not sucesso:
                return False, msg

        try:
            # 1. Insere na tabela ocorrencias
            id_ocorrencia = self._inserir_ocorrencia(dados)

            if not id_ocorrencia:
                self.connection.rollback()
                return False, "Erro ao inserir ocorrencia"

            # 2. Insere na tabela vitimas com o id_ocorrencia
            sucesso_vitima = self._inserir_vitima(dados, id_ocorrencia)

            if not sucesso_vitima:
                self.connection.rollback()
                return False, "Erro ao inserir vitima"

            self.connection.commit()

            return True, f"Registro inserido no MySQL! (Ocorrencia ID: {id_ocorrencia})"

        except mysql.connector.IntegrityError as e:
            self.connection.rollback()
            return False, f"Erro de integridade: {e}"
        except Exception as e:
            self.connection.rollback()
            return False, f"Erro ao inserir: {str(e)}"

    def _inserir_ocorrencia(self, dados: dict) -> Optional[int]:
        data_fato = self._converter_data(self._get_valor(dados, 'Data do Fato'))
        hora_fato = self._converter_hora(self._get_valor(dados, 'Hora do fato'))
        dia_semana = self._get_valor(dados, 'Dia da Semana')
        mes_referencia = self._get_valor(dados, 'Mês')
        logradouro = self._get_valor(dados, 'Logradouro')
        subtipo_local = self._get_valor(dados, 'Subtipo do Local')
        latitude = self._converter_float(self._get_valor(dados, 'Lat'))
        longitude = self._converter_float(self._get_valor(dados, 'Long'))

        # Lookups
        id_natureza = self._lookup_natureza(self._get_valor(dados, 'Natureza da Ocorrência'))
        id_tipo_acidente = self._lookup_tipo_acidente(self._get_valor(dados, 'Tipo de Acidente'))
        id_municipio = self._lookup_municipio(self._get_valor(dados, 'Município do Fato'))

        query = """
            INSERT INTO ocorrencias (
                data_fato, hora_fato, dia_semana, mes_referencia,
                id_municipio, logradouro, subtipo_local,
                id_natureza, id_tipo_acidente, latitude, longitude
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        valores = (
            data_fato, hora_fato, dia_semana, mes_referencia,
            id_municipio, logradouro, subtipo_local,
            id_natureza, id_tipo_acidente, latitude, longitude
        )

        self.cursor.execute(query, valores)
        return self.cursor.lastrowid

    def _inserir_vitima(self, dados: dict, id_ocorrencia: int) -> bool:
        nome = self._get_valor(dados, 'Vítima')
        sexo = self._get_valor(dados, 'Sexo')
        data_nascimento = self._converter_data(self._get_valor(dados, 'Data de\nNascimento'))
        idade = self._converter_int(self._get_valor(dados, 'Idade'))
        cpf = self._get_valor(dados, 'CPF')
        filiacao = self._get_valor(dados, 'Filiação')
        possui_cnh = self._get_valor(dados, 'Possui\nCNH')
        e_condutor = self._converter_boolean(self._get_valor(dados, 'Condutor'))
        exame_alcoolemia = self._get_valor(dados, 'Realizado Exame\nAlcoolemia')
        uso_capacete = self._get_valor(dados, 'Estava usando\nCapacete')
        data_obito = self._converter_data(self._get_valor(dados, 'Data do Óbito'))
        local_morte = self._get_valor(dados, 'Local da Morte')
        natureza_laudo = self._get_valor(dados, 'Natureza do Laudo')

        # Lookups de veiculos
        id_veiculo_vitima = self._lookup_veiculo(self._get_valor(dados, 'Veículo Vítima\nOu Outros'))
        id_veiculo_envolvido = self._lookup_veiculo(self._get_valor(dados, 'Veículo Envolvido\nOu Outros'))

        query = """
            INSERT INTO vitimas (
                id_ocorrencia, nome, sexo, data_nascimento, idade,
                cpf, filiacao, possui_cnh, e_condutor, exame_alcoolemia,
                uso_capacete, id_veiculo_vitima, id_veiculo_envolvido,
                data_obito, local_morte, natureza_laudo
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        valores = (
            id_ocorrencia, nome, sexo, data_nascimento, idade,
            cpf, filiacao, possui_cnh, e_condutor, exame_alcoolemia,
            uso_capacete, id_veiculo_vitima, id_veiculo_envolvido,
            data_obito, local_morte, natureza_laudo
        )

        self.cursor.execute(query, valores)
        return True

    # METODOS DE LOOKUP

    def _lookup_natureza(self, valor: str) -> Optional[int]:
        if not valor:
            return None
        return self._cache_natureza.get(valor.strip().lower())

    def _lookup_tipo_acidente(self, valor: str) -> Optional[int]:
        if not valor:
            return None
        return self._cache_tipo_acidente.get(valor.strip().lower())

    def _lookup_veiculo(self, valor: str) -> Optional[int]:
        if not valor:
            return None
        return self._cache_tipo_veiculo.get(valor.strip().lower())

    def _lookup_municipio(self, valor: str) -> Optional[int]:
        if not valor:
            return None
        return self._cache_municipio.get(valor.strip().lower())

    # METODOS DE CONVERSAO

    def _get_valor(self, dados: dict, chave: str) -> Optional[str]:
        valor = dados.get(chave, '')
        if valor is None or str(valor).strip() == '':
            return None
        return str(valor).strip()

    def _converter_data(self, valor: str) -> Optional[date]:
        if not valor:
            return None
        try:
            return datetime.strptime(valor, '%d/%m/%Y').date()
        except ValueError:
            try:
                return datetime.strptime(valor, '%Y-%m-%d').date()
            except ValueError:
                return None

    def _converter_hora(self, valor: str) -> Optional[time]:
        if not valor:
            return None
        try:
            if ':' in valor:
                partes = valor.split(':')
                return time(int(partes[0]), int(partes[1]))
            elif len(valor) == 4 and valor.isdigit():
                return time(int(valor[:2]), int(valor[2:]))
            return None
        except (ValueError, IndexError):
            return None

    def _converter_int(self, valor: str) -> Optional[int]:
        if not valor:
            return None
        try:
            if '.' in str(valor):
                return int(float(valor))
            return int(valor)
        except (ValueError, TypeError):
            return None

    def _converter_float(self, valor: str) -> Optional[float]:
        if not valor:
            return None
        try:
            valor_limpo = str(valor).replace(',', '.')
            return float(valor_limpo)
        except (ValueError, TypeError):
            return None

    def _converter_boolean(self, valor: str) -> Optional[bool]:
        if not valor:
            return None
        valor_lower = valor.strip().lower()
        if valor_lower in ('sim', 's', 'yes', 'true', '1'):
            return True
        elif valor_lower in ('não', 'nao', 'n', 'no', 'false', '0'):
            return False
        return None

    # METODOS AUXILIARES

    def testar_conexao(self) -> Tuple[bool, str]:
        try:
            sucesso, msg = self.conectar()
            if sucesso:
                self.cursor.execute("SELECT 1")
                self.desconectar()
                return True, "Conexao testada com sucesso!"
            return False, msg
        except Exception as e:
            return False, f"Erro no teste: {str(e)}"

    def desconectar(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
        except:
            pass
        finally:
            self.cursor = None
            self.connection = None

    def __del__(self):
        self.desconectar()


if __name__ == "__main__":
    print("Testando DatabaseHandler (MySQL)...")

    handler = DatabaseHandler()
    sucesso, msg = handler.testar_conexao()
    print(f"Resultado: {msg}")

    if sucesso:
        print("\nCaches carregados:")
        handler.conectar()
        print(f"  - Tipos Acidente: {len(handler._cache_tipo_acidente)}")
        print(f"  - Tipos Veiculo: {len(handler._cache_tipo_veiculo)}")
        print(f"  - Municipios: {len(handler._cache_municipio)}")
        handler.desconectar()
