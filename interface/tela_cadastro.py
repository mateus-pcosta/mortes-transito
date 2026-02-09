from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTabWidget, QFormLayout, QLineEdit,
                             QComboBox, QSpinBox, QDateEdit, QTimeEdit,
                             QTextEdit, QDoubleSpinBox, QMessageBox, QScrollArea,
                             QFrame, QCompleter)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, date
from typing import Tuple
from utils.dados_estaticos import (COLORS, TIPO_ACIDENTE, NATUREZA_LAUDO, SEXO,
                                   POSSUI_CNH, CONDUTOR, EXAME_ALCOOLEMIA,
                                   USANDO_CAPACETE, SUBTIPO_LOCAL, VEICULOS_VITIMA,
                                   VEICULOS_ENVOLVIDO, REGIAO)
from utils.calculos import calcular_idade, obter_dia_semana, obter_mes
from utils.validacoes import validar_cpf, campos_obrigatorios_preenchidos


class TelaCadastro(QWidget):

    cadastro_finalizado = pyqtSignal(dict)
    voltar_solicitado = pyqtSignal()

    def __init__(self, excel_handler):
        super().__init__()
        self.excel_handler = excel_handler
        self.campos = {}
        self.dados_dinamicos = {}
        self.init_ui()
        self.carregar_dados_dinamicos()
        self.conectar_signals()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.criar_barra_superior(layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ECF0F1;
                color: black;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498DB;
                color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #D5DBDB;
            }
        """)

        self.criar_aba_boletim()
        self.criar_aba_laudo()
        self.criar_aba_vitima()
        self.criar_aba_localizacao()
        self.criar_aba_data_hora()
        self.criar_aba_veiculos()
        self.criar_aba_territorial()

        layout.addWidget(self.tabs)

        self.criar_barra_inferior(layout)

        self.setLayout(layout)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit, QTimeEdit {{
                background-color: white;
                color: black;
                border: 1px solid #BDC3C7;
                padding: 5px;
                border-radius: 3px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid black;
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background-color: white;
                color: black;
                selection-background-color: {COLORS['secondary']};
                selection-color: white;
            }}
            QLabel {{
                color: {COLORS['text']};
            }}
        """)

    def criar_barra_superior(self, layout):
        barra = QFrame()
        barra.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['primary']};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        barra_layout = QHBoxLayout()

        info = self.excel_handler.obter_info_arquivo()
        nome_arquivo = self.excel_handler.caminho_arquivo.split('/')[-1].split('\\')[-1]

        label_arquivo = QLabel(f"{nome_arquivo}")
        label_arquivo.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")

        label_registros = QLabel(f"Total de registros: {info['total_registros']}")
        label_registros.setStyleSheet("color: white; font-size: 12px;")

        barra_layout.addWidget(label_arquivo)
        barra_layout.addStretch()
        barra_layout.addWidget(label_registros)

        barra.setLayout(barra_layout)
        layout.addWidget(barra)

    def criar_barra_inferior(self, layout):
        botoes_layout = QHBoxLayout()

        btn_voltar = QPushButton("Voltar ao Arquivo")
        btn_voltar.setStyleSheet(self.estilo_botao(COLORS['info']))
        btn_voltar.clicked.connect(self.voltar)
        botoes_layout.addWidget(btn_voltar)

        btn_limpar = QPushButton("Limpar Tudo")
        btn_limpar.setStyleSheet(self.estilo_botao(COLORS['warning']))
        btn_limpar.clicked.connect(self.limpar_formulario)
        botoes_layout.addWidget(btn_limpar)

        botoes_layout.addStretch()

        btn_finalizar = QPushButton("Finalizar e Salvar")
        btn_finalizar.setStyleSheet(self.estilo_botao(COLORS['success']))
        btn_finalizar.clicked.connect(self.finalizar_cadastro)
        botoes_layout.addWidget(btn_finalizar)

        layout.addLayout(botoes_layout)

    def estilo_botao(self, cor):
        return f"""
            QPushButton {{
                background-color: {cor};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
        """

    def criar_scroll_area(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        return scroll

    def criar_campo_label(self, texto, obrigatorio=False):
        if obrigatorio:
            texto = f"{texto} *"
        label = QLabel(texto)
        if obrigatorio:
            label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold;")
        return label

    def criar_campo_automatico_style(self):
        return f"""
            QLineEdit {{
                background-color: {COLORS['auto_field']};
                color: #7F8C8D;
                font-style: italic;
                border: 1px solid #95A5A6;
                padding: 5px;
            }}
        """

    # ==================== ABA 1: BOLETIM (CAMPOS BLOQUEADOS) ====================

    def criar_aba_boletim(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        estilo_bloqueado = f"""
            QLineEdit, QSpinBox, QComboBox {{
                background-color: {COLORS['auto_field']};
                color: #7F8C8D;
                font-style: italic;
                border: 1px solid #95A5A6;
                padding: 5px;
            }}
        """

        aviso = QLabel("Os campos abaixo estao desativados nesta versao. "
                       "Apenas o Tipo de Acidente esta disponivel.")
        aviso.setStyleSheet("color: #7F8C8D; font-size: 10px; font-style: italic;")
        aviso.setWordWrap(True)
        layout.addRow("", aviso)

        # N de BOS (bloqueado)
        self.campos['n_bos'] = QLineEdit()
        self.campos['n_bos'].setText("")
        self.campos['n_bos'].setEnabled(False)
        self.campos['n_bos'].setStyleSheet(estilo_bloqueado)
        layout.addRow(self.criar_campo_label("N de BOS"), self.campos['n_bos'])

        # N de Vitimas (bloqueado)
        self.campos['n_vitimas'] = QSpinBox()
        self.campos['n_vitimas'].setRange(0, 20)
        self.campos['n_vitimas'].setValue(0)
        self.campos['n_vitimas'].setEnabled(False)
        self.campos['n_vitimas'].setStyleSheet(estilo_bloqueado)
        layout.addRow(self.criar_campo_label("N de Vitimas"), self.campos['n_vitimas'])

        # Natureza da Ocorrencia (bloqueado)
        self.campos['natureza_ocorrencia'] = QComboBox()
        self.campos['natureza_ocorrencia'].setEnabled(False)
        self.campos['natureza_ocorrencia'].setStyleSheet(estilo_bloqueado)
        layout.addRow(self.criar_campo_label("Natureza da Ocorrencia"),
                     self.campos['natureza_ocorrencia'])

        # N do BO (bloqueado)
        self.campos['n_bo'] = QLineEdit()
        self.campos['n_bo'].setEnabled(False)
        self.campos['n_bo'].setStyleSheet(estilo_bloqueado)
        layout.addRow(self.criar_campo_label("N do BO"), self.campos['n_bo'])

        # Tipo de Acidente (UNICO CAMPO ATIVO - obrigatorio)
        self.campos['tipo_acidente'] = QComboBox()
        self.campos['tipo_acidente'].addItems(TIPO_ACIDENTE)
        layout.addRow(self.criar_campo_label("Tipo de Acidente", True),
                     self.campos['tipo_acidente'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Boletim")

    # ==================== ABA 2: LAUDO ====================

    def criar_aba_laudo(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.campos['n_laudo'] = QLineEdit()
        self.campos['n_laudo'].setPlaceholderText("Numero do laudo")
        layout.addRow(self.criar_campo_label("N Laudo IML"), self.campos['n_laudo'])

        self.campos['natureza_laudo'] = QComboBox()
        self.campos['natureza_laudo'].setEditable(True)
        self.campos['natureza_laudo'].addItems(NATUREZA_LAUDO)
        layout.addRow(self.criar_campo_label("Natureza do Laudo"),
                     self.campos['natureza_laudo'])

        self.campos['data_obito'] = QDateEdit()
        self.campos['data_obito'].setCalendarPopup(True)
        self.campos['data_obito'].setDate(QDate.currentDate())
        self.campos['data_obito'].setDisplayFormat("dd/MM/yyyy")
        layout.addRow(self.criar_campo_label("Data do Obito", True),
                     self.campos['data_obito'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Laudo")

    # ==================== ABA 3: VITIMA ====================

    def criar_aba_vitima(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.campos['vitima'] = QLineEdit()
        self.campos['vitima'].setPlaceholderText("Nome completo da vitima")
        layout.addRow(self.criar_campo_label("Vitima (Nome Completo)", True),
                     self.campos['vitima'])

        self.campos['sexo'] = QComboBox()
        self.campos['sexo'].addItems(SEXO)
        layout.addRow(self.criar_campo_label("Sexo", True), self.campos['sexo'])

        self.campos['filiacao'] = QLineEdit()
        self.campos['filiacao'].setPlaceholderText("Nome da mae ou responsavel")
        layout.addRow(self.criar_campo_label("Filiacao"), self.campos['filiacao'])

        self.campos['data_nascimento'] = QDateEdit()
        self.campos['data_nascimento'].setCalendarPopup(True)
        self.campos['data_nascimento'].setDate(QDate(2000, 1, 1))
        self.campos['data_nascimento'].setDisplayFormat("dd/MM/yyyy")
        layout.addRow(self.criar_campo_label("Data de Nascimento"),
                     self.campos['data_nascimento'])

        self.campos['idade'] = QLineEdit()
        self.campos['idade'].setReadOnly(True)
        self.campos['idade'].setStyleSheet(self.criar_campo_automatico_style())
        self.campos['idade'].setPlaceholderText("Calculado automaticamente")
        label_idade = QLabel("Idade (auto)")
        label_idade.setStyleSheet(f"color: {COLORS['info']}; font-style: italic;")
        layout.addRow(label_idade, self.campos['idade'])

        self.campos['cpf'] = QLineEdit()
        self.campos['cpf'].setInputMask("000.000.000-00")
        self.campos['cpf'].setPlaceholderText("000.000.000-00")
        layout.addRow(self.criar_campo_label("CPF"), self.campos['cpf'])

        self.campos['possui_cnh'] = QComboBox()
        self.campos['possui_cnh'].addItems(POSSUI_CNH)
        layout.addRow(self.criar_campo_label("Possui CNH"), self.campos['possui_cnh'])

        self.campos['condutor'] = QComboBox()
        self.campos['condutor'].addItems(CONDUTOR)
        layout.addRow(self.criar_campo_label("Condutor"), self.campos['condutor'])

        self.campos['exame_alcoolemia'] = QComboBox()
        self.campos['exame_alcoolemia'].addItems(EXAME_ALCOOLEMIA)
        layout.addRow(self.criar_campo_label("Realizado Exame de Alcoolemia"),
                     self.campos['exame_alcoolemia'])

        self.campos['usando_capacete'] = QComboBox()
        self.campos['usando_capacete'].addItems(USANDO_CAPACETE)
        self.label_capacete = self.criar_campo_label("Estava usando Capacete")
        layout.addRow(self.label_capacete, self.campos['usando_capacete'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Vitima")

    # ==================== ABA 4: LOCALIZACAO ====================

    def criar_aba_localizacao(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.campos['municipio'] = QComboBox()
        self.campos['municipio'].setEditable(True)
        layout.addRow(self.criar_campo_label("Municipio do Fato", True),
                     self.campos['municipio'])

        self.campos['logradouro'] = QTextEdit()
        self.campos['logradouro'].setMaximumHeight(80)
        self.campos['logradouro'].setPlaceholderText(
            "Endereco completo: rua, numero, bairro, referencias")
        layout.addRow(self.criar_campo_label("Logradouro"), self.campos['logradouro'])

        self.campos['subtipo_local'] = QComboBox()
        self.campos['subtipo_local'].addItems(SUBTIPO_LOCAL)
        layout.addRow(self.criar_campo_label("Subtipo do Local"),
                     self.campos['subtipo_local'])

        self.campos['latitude'] = QDoubleSpinBox()
        self.campos['latitude'].setRange(-90.0, 90.0)
        self.campos['latitude'].setDecimals(6)
        self.campos['latitude'].setValue(0.0)
        self.campos['latitude'].setPrefix("")
        layout.addRow(self.criar_campo_label("Latitude"), self.campos['latitude'])

        self.campos['longitude'] = QDoubleSpinBox()
        self.campos['longitude'].setRange(-180.0, 180.0)
        self.campos['longitude'].setDecimals(6)
        self.campos['longitude'].setValue(0.0)
        layout.addRow(self.criar_campo_label("Longitude"), self.campos['longitude'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Localizacao")

    # ==================== ABA 5: DATA E HORA ====================

    def criar_aba_data_hora(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.campos['data_fato'] = QDateEdit()
        self.campos['data_fato'].setCalendarPopup(True)
        self.campos['data_fato'].setDate(QDate.currentDate())
        self.campos['data_fato'].setDisplayFormat("dd/MM/yyyy")
        layout.addRow(self.criar_campo_label("Data do Fato", True),
                     self.campos['data_fato'])

        self.campos['hora_fato'] = QTimeEdit()
        self.campos['hora_fato'].setDisplayFormat("HH:mm")
        self.campos['hora_fato'].setTime(QTime(12, 0))
        layout.addRow(self.criar_campo_label("Hora do Fato"), self.campos['hora_fato'])

        self.campos['dia_semana'] = QLineEdit()
        self.campos['dia_semana'].setReadOnly(True)
        self.campos['dia_semana'].setStyleSheet(self.criar_campo_automatico_style())
        label_dia = QLabel("Dia da Semana (auto)")
        label_dia.setStyleSheet(f"color: {COLORS['info']}; font-style: italic;")
        layout.addRow(label_dia, self.campos['dia_semana'])

        self.campos['mes'] = QLineEdit()
        self.campos['mes'].setReadOnly(True)
        self.campos['mes'].setStyleSheet(self.criar_campo_automatico_style())
        label_mes = QLabel("Mes (auto)")
        label_mes.setStyleSheet(f"color: {COLORS['info']}; font-style: italic;")
        layout.addRow(label_mes, self.campos['mes'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Data e Hora")

    # ==================== ABA 6: VEICULOS ====================

    def criar_aba_veiculos(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.campos['local_morte'] = QComboBox()
        self.campos['local_morte'].setEditable(True)
        layout.addRow(self.criar_campo_label("Local da Morte"),
                     self.campos['local_morte'])

        self.campos['veiculo_vitima'] = QComboBox()
        self.campos['veiculo_vitima'].addItems(VEICULOS_VITIMA)
        layout.addRow(self.criar_campo_label("Veiculo Vitima ou Outros"),
                     self.campos['veiculo_vitima'])

        self.campos['veiculo_envolvido'] = QComboBox()
        self.campos['veiculo_envolvido'].addItems(VEICULOS_ENVOLVIDO)
        layout.addRow(self.criar_campo_label("Veiculo Envolvido ou Outros"),
                     self.campos['veiculo_envolvido'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Veiculos")

    # ==================== ABA 7: TERRITORIAL ====================

    def criar_aba_territorial(self):
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.campos['regiao'] = QComboBox()
        self.campos['regiao'].addItems(REGIAO)
        layout.addRow(self.criar_campo_label("Regiao"), self.campos['regiao'])

        self.campos['territorio'] = QComboBox()
        self.campos['territorio'].setEditable(True)
        layout.addRow(self.criar_campo_label("Territorio de Desenvolvimento"),
                     self.campos['territorio'])

        self.campos['obs'] = QTextEdit()
        self.campos['obs'].setMaximumHeight(100)
        self.campos['obs'].setPlaceholderText("Observacoes adicionais sobre o caso...")
        layout.addRow(self.criar_campo_label("Observacoes"), self.campos['obs'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "Territorial")

    # ==================== METODOS AUXILIARES ====================

    def carregar_dados_dinamicos(self):
        self.dados_dinamicos = {
            'municipios': self.excel_handler.obter_valores_unicos('Município do Fato'),
            'locais_morte': self.excel_handler.obter_valores_unicos('Local da Morte'),
            'territorios': self.excel_handler.obter_valores_unicos('Território de\nDesenvolvimento')
        }

        if self.dados_dinamicos['municipios']:
            self.campos['municipio'].addItems(self.dados_dinamicos['municipios'])

        if self.dados_dinamicos['locais_morte']:
            self.campos['local_morte'].addItems(self.dados_dinamicos['locais_morte'])

        if self.dados_dinamicos['territorios']:
            self.campos['territorio'].addItems(self.dados_dinamicos['territorios'])

    def conectar_signals(self):
        self.campos['data_nascimento'].dateChanged.connect(self.atualizar_idade)
        self.campos['data_obito'].dateChanged.connect(self.atualizar_idade)
        self.campos['data_fato'].dateChanged.connect(self.atualizar_dia_semana_mes)
        self.atualizar_dia_semana_mes()

    def atualizar_idade(self):
        data_nasc = self.campos['data_nascimento'].date().toPyDate()
        data_obt = self.campos['data_obito'].date().toPyDate()

        idade = calcular_idade(data_nasc, data_obt)
        if idade is not None:
            self.campos['idade'].setText(str(idade))
        else:
            self.campos['idade'].setText("")

    def atualizar_dia_semana_mes(self):
        data = self.campos['data_fato'].date().toPyDate()
        dia_semana = obter_dia_semana(data)
        mes = obter_mes(data)
        self.campos['dia_semana'].setText(dia_semana)
        self.campos['mes'].setText(mes)

    def obter_dados_formulario(self) -> dict:
        dados = {}

        # Apenas campos ativos (29 colunas - sem os 4 bloqueados do Boletim)
        dados['Tipo de Acidente'] = self.campos['tipo_acidente'].currentText()
        dados['Nº Laudo IML'] = self.campos['n_laudo'].text()
        dados['Natureza do Laudo'] = self.campos['natureza_laudo'].currentText()
        dados['Data do Óbito'] = self.campos['data_obito'].date().toPyDate().strftime('%d/%m/%Y')
        dados['Vítima'] = self.campos['vitima'].text().strip().title()
        dados['Sexo'] = self.campos['sexo'].currentText()
        dados['Filiação'] = self.campos['filiacao'].text().strip().title()
        dados['Data de\nNascimento'] = self.campos['data_nascimento'].date().toPyDate().strftime('%d/%m/%Y')
        dados['Idade'] = int(self.campos['idade'].text()) if self.campos['idade'].text() else None
        dados['CPF'] = self.campos['cpf'].text().strip()
        dados['Possui\nCNH'] = self.campos['possui_cnh'].currentText()
        dados['Condutor'] = self.campos['condutor'].currentText()
        dados['Realizado Exame\nAlcoolemia'] = self.campos['exame_alcoolemia'].currentText()
        dados['Estava usando\nCapacete'] = self.campos['usando_capacete'].currentText()
        dados['Município do Fato'] = self.campos['municipio'].currentText()
        dados['Logradouro'] = self.campos['logradouro'].toPlainText().strip()
        dados['Subtipo do Local'] = self.campos['subtipo_local'].currentText()
        dados['Lat'] = self.campos['latitude'].value()
        dados['Long'] = self.campos['longitude'].value()
        dados['Data do Fato'] = self.campos['data_fato'].date().toPyDate().strftime('%d/%m/%Y')
        dados['Hora do fato'] = self.campos['hora_fato'].time().toString("HH:mm")
        dados['Dia da Semana'] = self.campos['dia_semana'].text()
        dados['Mês'] = self.campos['mes'].text()
        dados['Local da Morte'] = self.campos['local_morte'].currentText()
        dados['Veículo Vítima\nOu Outros'] = self.campos['veiculo_vitima'].currentText()
        dados['Veículo Envolvido\nOu Outros'] = self.campos['veiculo_envolvido'].currentText()
        dados['Região'] = self.campos['regiao'].currentText()
        dados['Território de\nDesenvolvimento'] = self.campos['territorio'].currentText()
        dados['OBS:'] = self.campos['obs'].toPlainText().strip()

        return dados

    def validar_formulario(self) -> Tuple[bool, str]:
        dados = self.obter_dados_formulario()

        todos_preenchidos, campos_vazios = campos_obrigatorios_preenchidos(dados)
        if not todos_preenchidos:
            return False, "Campos obrigatorios nao preenchidos:\n" + "\n".join(f"- {c}" for c in campos_vazios)

        cpf = dados['CPF']
        if cpf and cpf.replace(".", "").replace("-", "").replace("_", "").strip():
            if not validar_cpf(cpf):
                return False, "CPF invalido."

        return True, ""

    def finalizar_cadastro(self):
        valido, mensagem = self.validar_formulario()

        if not valido:
            QMessageBox.warning(self, "Validacao", mensagem)
            return

        dados = self.obter_dados_formulario()
        self.cadastro_finalizado.emit(dados)

    def limpar_formulario(self):
        resposta = QMessageBox.question(
            self,
            "Limpar Formulario",
            "Tem certeza? Todos os dados serao perdidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            self.campos['tipo_acidente'].setCurrentIndex(0)
            self.campos['n_laudo'].setText("")
            self.campos['natureza_laudo'].setCurrentIndex(0)
            self.campos['data_obito'].setDate(QDate.currentDate())
            self.campos['vitima'].setText("")
            self.campos['sexo'].setCurrentIndex(0)
            self.campos['filiacao'].setText("")
            self.campos['data_nascimento'].setDate(QDate(2000, 1, 1))
            self.campos['cpf'].setText("")
            self.campos['possui_cnh'].setCurrentIndex(0)
            self.campos['condutor'].setCurrentIndex(0)
            self.campos['exame_alcoolemia'].setCurrentIndex(0)
            self.campos['usando_capacete'].setCurrentIndex(0)
            self.campos['municipio'].setCurrentIndex(0)
            self.campos['logradouro'].clear()
            self.campos['subtipo_local'].setCurrentIndex(0)
            self.campos['latitude'].setValue(0.0)
            self.campos['longitude'].setValue(0.0)
            self.campos['data_fato'].setDate(QDate.currentDate())
            self.campos['hora_fato'].setTime(QTime(12, 0))
            self.campos['local_morte'].setCurrentIndex(0)
            self.campos['veiculo_vitima'].setCurrentIndex(0)
            self.campos['veiculo_envolvido'].setCurrentIndex(0)
            self.campos['regiao'].setCurrentIndex(0)
            self.campos['territorio'].setCurrentIndex(0)
            self.campos['obs'].clear()

    def voltar(self):
        self.voltar_solicitado.emit()
