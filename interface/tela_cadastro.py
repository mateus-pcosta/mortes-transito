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

    # Signal emitido quando o usuário finaliza o cadastro
    cadastro_finalizado = pyqtSignal(dict)  # Emite dicionário com os dados
    voltar_solicitado = pyqtSignal()  # Emite quando usuário quer voltar

    def __init__(self, excel_handler):
        super().__init__()
        self.excel_handler = excel_handler
        self.campos = {}  # Dicionário para armazenar referências aos campos
        self.dados_dinamicos = {}  # Dados carregados da planilha
        self.init_ui()
        self.carregar_dados_dinamicos()
        self.conectar_signals()

    def init_ui(self):
        """Inicializa a interface da tela."""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Barra superior com informações
        self.criar_barra_superior(layout)

        # Tabs com os campos
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

        # Cria as 7 abas
        self.criar_aba_boletim()
        self.criar_aba_laudo()
        self.criar_aba_vitima()
        self.criar_aba_localizacao()
        self.criar_aba_data_hora()
        self.criar_aba_veiculos()
        self.criar_aba_territorial()

        layout.addWidget(self.tabs)

        # Barra inferior com botões de ação
        self.criar_barra_inferior(layout)

        self.setLayout(layout)

        # Estilo global para garantir legibilidade
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
        """Cria a barra superior com informações do arquivo."""
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

        label_arquivo = QLabel(f"📄 {nome_arquivo}")
        label_arquivo.setStyleSheet("color: white; font-weight: bold; font-size: 13px;")

        label_registros = QLabel(f"Total de registros: {info['total_registros']}")
        label_registros.setStyleSheet("color: white; font-size: 12px;")

        barra_layout.addWidget(label_arquivo)
        barra_layout.addStretch()
        barra_layout.addWidget(label_registros)

        barra.setLayout(barra_layout)
        layout.addWidget(barra)

    def criar_barra_inferior(self, layout):
        """Cria a barra inferior com botões de ação."""
        botoes_layout = QHBoxLayout()

        # Botão Voltar
        btn_voltar = QPushButton("← Voltar ao Arquivo")
        btn_voltar.setStyleSheet(self.estilo_botao(COLORS['info']))
        btn_voltar.clicked.connect(self.voltar)
        botoes_layout.addWidget(btn_voltar)

        # Botão Limpar
        btn_limpar = QPushButton("Limpar Tudo")
        btn_limpar.setStyleSheet(self.estilo_botao(COLORS['warning']))
        btn_limpar.clicked.connect(self.limpar_formulario)
        botoes_layout.addWidget(btn_limpar)

        botoes_layout.addStretch()

        # Botão Finalizar
        btn_finalizar = QPushButton("✓ Finalizar e Salvar")
        btn_finalizar.setStyleSheet(self.estilo_botao(COLORS['success']))
        btn_finalizar.clicked.connect(self.finalizar_cadastro)
        botoes_layout.addWidget(btn_finalizar)

        layout.addLayout(botoes_layout)

    def estilo_botao(self, cor):
        """Retorna estilo CSS para botões."""
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
        """Cria uma área com scroll para formulários longos."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: white; }")
        return scroll

    def criar_campo_label(self, texto, obrigatorio=False):
        """Cria um label para campo do formulário."""
        if obrigatorio:
            texto = f"{texto} *"
        label = QLabel(texto)
        if obrigatorio:
            label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold;")
        return label

    def criar_campo_automatico_style(self):
        """Retorna estilo para campos automáticos (read-only)."""
        return f"""
            QLineEdit {{
                background-color: {COLORS['auto_field']};
                color: #7F8C8D;
                font-style: italic;
                border: 1px solid #95A5A6;
                padding: 5px;
            }}
        """

    # ==================== ABA 1: INFORMAÇÕES DO BOLETIM ====================

    def criar_aba_boletim(self):
        """Cria a aba de Informações do Boletim."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Nº de BOS
        self.campos['n_bos'] = QLineEdit()
        self.campos['n_bos'].setText("1")
        self.campos['n_bos'].setPlaceholderText("Deixe vazio se for vítima adicional")
        layout.addRow(self.criar_campo_label("Nº de BOS"), self.campos['n_bos'])

        help_label = QLabel("💡 Deixe vazio se for vítima adicional do mesmo acidente")
        help_label.setStyleSheet("color: #7F8C8D; font-size: 10px; font-style: italic;")
        layout.addRow("", help_label)

        # Nº de Vítimas
        self.campos['n_vitimas'] = QSpinBox()
        self.campos['n_vitimas'].setRange(1, 20)
        self.campos['n_vitimas'].setValue(1)
        layout.addRow(self.criar_campo_label("Nº de Vítimas"), self.campos['n_vitimas'])

        # Natureza da Ocorrência (obrigatório)
        self.campos['natureza_ocorrencia'] = QComboBox()
        self.campos['natureza_ocorrencia'].setEditable(True)
        layout.addRow(self.criar_campo_label("Natureza da Ocorrência", True),
                     self.campos['natureza_ocorrencia'])

        # Nº do BO (obrigatório)
        self.campos['n_bo'] = QLineEdit()
        self.campos['n_bo'].setPlaceholderText("Ex: 00001111/2025")
        layout.addRow(self.criar_campo_label("Nº do BO", True), self.campos['n_bo'])

        # Tipo de Acidente (obrigatório)
        self.campos['tipo_acidente'] = QComboBox()
        self.campos['tipo_acidente'].addItems(TIPO_ACIDENTE)
        layout.addRow(self.criar_campo_label("Tipo de Acidente", True),
                     self.campos['tipo_acidente'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "📋 Boletim")

    # ==================== ABA 2: INFORMAÇÕES DO LAUDO ====================

    def criar_aba_laudo(self):
        """Cria a aba de Informações do Laudo."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Nº Laudo IML
        self.campos['n_laudo'] = QLineEdit()
        self.campos['n_laudo'].setPlaceholderText("Número do laudo")
        layout.addRow(self.criar_campo_label("Nº Laudo IML"), self.campos['n_laudo'])

        # Natureza do Laudo
        self.campos['natureza_laudo'] = QComboBox()
        self.campos['natureza_laudo'].setEditable(True)  # Permite escrever
        self.campos['natureza_laudo'].addItems(NATUREZA_LAUDO)
        layout.addRow(self.criar_campo_label("Natureza do Laudo"),
                     self.campos['natureza_laudo'])

        # Data do Óbito (obrigatório)
        self.campos['data_obito'] = QDateEdit()
        self.campos['data_obito'].setCalendarPopup(True)
        self.campos['data_obito'].setDate(QDate.currentDate())
        self.campos['data_obito'].setDisplayFormat("dd/MM/yyyy")
        layout.addRow(self.criar_campo_label("Data do Óbito", True),
                     self.campos['data_obito'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "🏥 Laudo")

    # ==================== ABA 3: DADOS DA VÍTIMA ====================

    def criar_aba_vitima(self):
        """Cria a aba de Dados da Vítima."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Vítima - Nome Completo (obrigatório)
        self.campos['vitima'] = QLineEdit()
        self.campos['vitima'].setPlaceholderText("Nome completo da vítima")
        layout.addRow(self.criar_campo_label("Vítima (Nome Completo)", True),
                     self.campos['vitima'])

        # Sexo (obrigatório)
        self.campos['sexo'] = QComboBox()
        self.campos['sexo'].addItems(SEXO)
        layout.addRow(self.criar_campo_label("Sexo", True), self.campos['sexo'])

        # Filiação
        self.campos['filiacao'] = QLineEdit()
        self.campos['filiacao'].setPlaceholderText("Nome da mãe ou responsável")
        layout.addRow(self.criar_campo_label("Filiação"), self.campos['filiacao'])

        # Data de Nascimento
        self.campos['data_nascimento'] = QDateEdit()
        self.campos['data_nascimento'].setCalendarPopup(True)
        self.campos['data_nascimento'].setDate(QDate(2000, 1, 1))
        self.campos['data_nascimento'].setDisplayFormat("dd/MM/yyyy")
        layout.addRow(self.criar_campo_label("Data de Nascimento"),
                     self.campos['data_nascimento'])

        # Idade (automático)
        self.campos['idade'] = QLineEdit()
        self.campos['idade'].setReadOnly(True)
        self.campos['idade'].setStyleSheet(self.criar_campo_automatico_style())
        self.campos['idade'].setPlaceholderText("Calculado automaticamente")
        label_idade = QLabel("Idade 🤖")
        label_idade.setStyleSheet(f"color: {COLORS['info']}; font-style: italic;")
        layout.addRow(label_idade, self.campos['idade'])

        # CPF
        self.campos['cpf'] = QLineEdit()
        self.campos['cpf'].setInputMask("000.000.000-00")
        self.campos['cpf'].setPlaceholderText("000.000.000-00")
        layout.addRow(self.criar_campo_label("CPF"), self.campos['cpf'])

        # Possui CNH
        self.campos['possui_cnh'] = QComboBox()
        self.campos['possui_cnh'].addItems(POSSUI_CNH)
        layout.addRow(self.criar_campo_label("Possui CNH"), self.campos['possui_cnh'])

        # Condutor
        self.campos['condutor'] = QComboBox()
        self.campos['condutor'].addItems(CONDUTOR)
        layout.addRow(self.criar_campo_label("Condutor"), self.campos['condutor'])

        # Realizado Exame Alcoolemia
        self.campos['exame_alcoolemia'] = QComboBox()
        self.campos['exame_alcoolemia'].addItems(EXAME_ALCOOLEMIA)
        layout.addRow(self.criar_campo_label("Realizado Exame de Alcoolemia"),
                     self.campos['exame_alcoolemia'])

        # Estava usando Capacete (condicional)
        self.campos['usando_capacete'] = QComboBox()
        self.campos['usando_capacete'].addItems(USANDO_CAPACETE)
        self.label_capacete = self.criar_campo_label("Estava usando Capacete")
        layout.addRow(self.label_capacete, self.campos['usando_capacete'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "👤 Vítima")

    # ==================== ABA 4: LOCALIZAÇÃO ====================

    def criar_aba_localizacao(self):
        """Cria a aba de Localização do Acidente."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Município do Fato (obrigatório)
        self.campos['municipio'] = QComboBox()
        self.campos['municipio'].setEditable(True)
        layout.addRow(self.criar_campo_label("Município do Fato", True),
                     self.campos['municipio'])

        # Logradouro
        self.campos['logradouro'] = QTextEdit()
        self.campos['logradouro'].setMaximumHeight(80)
        self.campos['logradouro'].setPlaceholderText(
            "Endereço completo: rua, número, bairro, referências\nEx: PI-142, KM 5, próximo ao posto BR")
        layout.addRow(self.criar_campo_label("Logradouro"), self.campos['logradouro'])

        # Subtipo do Local
        self.campos['subtipo_local'] = QComboBox()
        self.campos['subtipo_local'].addItems(SUBTIPO_LOCAL)
        layout.addRow(self.criar_campo_label("Subtipo do Local"),
                     self.campos['subtipo_local'])

        # Latitude
        self.campos['latitude'] = QDoubleSpinBox()
        self.campos['latitude'].setRange(-90.0, 90.0)
        self.campos['latitude'].setDecimals(6)
        self.campos['latitude'].setValue(0.0)
        self.campos['latitude'].setPrefix("")
        layout.addRow(self.criar_campo_label("Latitude"), self.campos['latitude'])

        # Longitude
        self.campos['longitude'] = QDoubleSpinBox()
        self.campos['longitude'].setRange(-180.0, 180.0)
        self.campos['longitude'].setDecimals(6)
        self.campos['longitude'].setValue(0.0)
        layout.addRow(self.criar_campo_label("Longitude"), self.campos['longitude'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "📍 Localização")

    # ==================== ABA 5: DATA E HORA ====================

    def criar_aba_data_hora(self):
        """Cria a aba de Data e Hora do Fato."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Data do Fato (obrigatório)
        self.campos['data_fato'] = QDateEdit()
        self.campos['data_fato'].setCalendarPopup(True)
        self.campos['data_fato'].setDate(QDate.currentDate())
        self.campos['data_fato'].setDisplayFormat("dd/MM/yyyy")
        layout.addRow(self.criar_campo_label("Data do Fato", True),
                     self.campos['data_fato'])

        # Hora do Fato
        self.campos['hora_fato'] = QTimeEdit()
        self.campos['hora_fato'].setDisplayFormat("HH:mm")
        self.campos['hora_fato'].setTime(QTime(12, 0))
        layout.addRow(self.criar_campo_label("Hora do Fato"), self.campos['hora_fato'])

        # Dia da Semana (automático)
        self.campos['dia_semana'] = QLineEdit()
        self.campos['dia_semana'].setReadOnly(True)
        self.campos['dia_semana'].setStyleSheet(self.criar_campo_automatico_style())
        label_dia = QLabel("Dia da Semana 🤖")
        label_dia.setStyleSheet(f"color: {COLORS['info']}; font-style: italic;")
        layout.addRow(label_dia, self.campos['dia_semana'])

        # Mês (automático)
        self.campos['mes'] = QLineEdit()
        self.campos['mes'].setReadOnly(True)
        self.campos['mes'].setStyleSheet(self.criar_campo_automatico_style())
        label_mes = QLabel("Mês 🤖")
        label_mes.setStyleSheet(f"color: {COLORS['info']}; font-style: italic;")
        layout.addRow(label_mes, self.campos['mes'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "📅 Data e Hora")

    # ==================== ABA 6: VEÍCULOS ====================

    def criar_aba_veiculos(self):
        """Cria a aba de Local da Morte e Veículos."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Local da Morte
        self.campos['local_morte'] = QComboBox()
        self.campos['local_morte'].setEditable(True)
        layout.addRow(self.criar_campo_label("Local da Morte"),
                     self.campos['local_morte'])

        # Veículo Vítima
        self.campos['veiculo_vitima'] = QComboBox()
        self.campos['veiculo_vitima'].addItems(VEICULOS_VITIMA)
        layout.addRow(self.criar_campo_label("Veículo Vítima ou Outros"),
                     self.campos['veiculo_vitima'])

        # Veículo Envolvido
        self.campos['veiculo_envolvido'] = QComboBox()
        self.campos['veiculo_envolvido'].addItems(VEICULOS_ENVOLVIDO)
        layout.addRow(self.criar_campo_label("Veículo Envolvido ou Outros"),
                     self.campos['veiculo_envolvido'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "🚗 Veículos")

    # ==================== ABA 7: TERRITORIAL ====================

    def criar_aba_territorial(self):
        """Cria a aba de Classificação Territorial."""
        widget = QWidget()
        scroll = self.criar_scroll_area()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Região
        self.campos['regiao'] = QComboBox()
        self.campos['regiao'].addItems(REGIAO)
        layout.addRow(self.criar_campo_label("Região"), self.campos['regiao'])

        # Território de Desenvolvimento
        self.campos['territorio'] = QComboBox()
        self.campos['territorio'].setEditable(True)
        layout.addRow(self.criar_campo_label("Território de Desenvolvimento"),
                     self.campos['territorio'])

        # OBS
        self.campos['obs'] = QTextEdit()
        self.campos['obs'].setMaximumHeight(100)
        self.campos['obs'].setPlaceholderText("Observações adicionais sobre o caso...")
        layout.addRow(self.criar_campo_label("Observações"), self.campos['obs'])

        widget.setLayout(layout)
        scroll.setWidget(widget)
        self.tabs.addTab(scroll, "🗺️ Territorial")

    # ==================== MÉTODOS AUXILIARES ====================

    def carregar_dados_dinamicos(self):
        """Carrega dados únicos da planilha para popular comboboxes."""
        self.dados_dinamicos = {
            'municipios': self.excel_handler.obter_valores_unicos('Município do Fato'),
            'natureza_ocorrencia': self.excel_handler.obter_valores_unicos('Natureza da Ocorrência'),
            'locais_morte': self.excel_handler.obter_valores_unicos('Local da Morte'),
            'territorios': self.excel_handler.obter_valores_unicos('Território de\nDesenvolvimento')
        }

        # Popula comboboxes
        if self.dados_dinamicos['municipios']:
            self.campos['municipio'].addItems(self.dados_dinamicos['municipios'])

        if self.dados_dinamicos['natureza_ocorrencia']:
            self.campos['natureza_ocorrencia'].addItems(self.dados_dinamicos['natureza_ocorrencia'])

        if self.dados_dinamicos['locais_morte']:
            self.campos['local_morte'].addItems(self.dados_dinamicos['locais_morte'])

        if self.dados_dinamicos['territorios']:
            self.campos['territorio'].addItems(self.dados_dinamicos['territorios'])

    def conectar_signals(self):
        """Conecta signals para cálculos automáticos."""
        # Quando data de nascimento ou data de óbito mudar, recalcula idade
        self.campos['data_nascimento'].dateChanged.connect(self.atualizar_idade)
        self.campos['data_obito'].dateChanged.connect(self.atualizar_idade)

        # Quando data do fato mudar, atualiza dia da semana e mês
        self.campos['data_fato'].dateChanged.connect(self.atualizar_dia_semana_mes)

        # Atualiza inicialmente
        self.atualizar_dia_semana_mes()

    def atualizar_idade(self):
        """Calcula e atualiza o campo idade automaticamente."""
        data_nasc = self.campos['data_nascimento'].date().toPyDate()
        data_obt = self.campos['data_obito'].date().toPyDate()

        idade = calcular_idade(data_nasc, data_obt)
        if idade is not None:
            self.campos['idade'].setText(str(idade))
        else:
            self.campos['idade'].setText("")

    def atualizar_dia_semana_mes(self):
        """Atualiza automaticamente dia da semana e mês."""
        data = self.campos['data_fato'].date().toPyDate()

        dia_semana = obter_dia_semana(data)
        mes = obter_mes(data)

        self.campos['dia_semana'].setText(dia_semana)
        self.campos['mes'].setText(mes)

    def obter_dados_formulario(self) -> dict:
        """
        Coleta todos os dados do formulário.

        Returns:
            Dicionário com os dados preenchidos
        """
        dados = {}

        # Nº de BOS (pode estar vazio)
        n_bos_texto = self.campos['n_bos'].text().strip()
        dados['Nº de\nBOS'] = None if n_bos_texto == "" else 1.0

        # Demais campos
        dados['Nº de\nVítimas'] = self.campos['n_vitimas'].value()
        dados['Natureza da Ocorrência'] = self.campos['natureza_ocorrencia'].currentText()
        dados['Nº do BO'] = self.campos['n_bo'].text()
        dados['Tipo de Acidente'] = self.campos['tipo_acidente'].currentText()
        dados['Nº Laudo IML'] = self.campos['n_laudo'].text()
        dados['Natureza do Laudo'] = self.campos['natureza_laudo'].currentText()
        dados['Data do Óbito'] = self.campos['data_obito'].date().toPyDate().strftime('%d/%m/%Y')
        dados['Vítima'] = self.campos['vitima'].text().strip().title()  # Capitaliza
        dados['Sexo'] = self.campos['sexo'].currentText()
        dados['Filiação'] = self.campos['filiacao'].text().strip().title()  # Capitaliza
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
        """
        Valida todos os campos do formulário.

        Returns:
            Tupla (valido, mensagem_erro)
        """
        dados = self.obter_dados_formulario()

        # Verifica campos obrigatórios
        todos_preenchidos, campos_vazios = campos_obrigatorios_preenchidos(dados)
        if not todos_preenchidos:
            return False, f"Campos obrigatórios não preenchidos:\n" + "\n".join(f"- {c}" for c in campos_vazios)

        # Valida CPF se preenchido
        cpf = dados['CPF']
        if cpf and cpf.replace(".", "").replace("-", "").replace("_", "").strip():
            if not validar_cpf(cpf):
                return False, "CPF inválido."

        return True, ""

    def finalizar_cadastro(self):
        """Valida e emite signal para finalizar cadastro."""
        valido, mensagem = self.validar_formulario()

        if not valido:
            QMessageBox.warning(self, "Validação", mensagem)
            return

        # Emite os dados para a próxima tela
        dados = self.obter_dados_formulario()
        self.cadastro_finalizado.emit(dados)

    def limpar_formulario(self):
        """Limpa todos os campos do formulário."""
        resposta = QMessageBox.question(
            self,
            "Limpar Formulário",
            "Tem certeza? Todos os dados serão perdidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            # Resetar todos os campos
            self.campos['n_bos'].setText("1")
            self.campos['n_vitimas'].setValue(1)
            # ... (resetar todos os outros campos)

    def voltar(self):
        """Emite signal para voltar à tela anterior."""
        self.voltar_solicitado.emit()
