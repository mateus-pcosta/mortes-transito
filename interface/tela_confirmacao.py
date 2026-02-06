from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.dados_estaticos import COLORS
import os
import subprocess
import platform


class TelaConfirmacao(QWidget):
    """Tela de confirmação e download."""

    # Signals
    cadastrar_outro = pyqtSignal()  # Para voltar ao formulário
    fechar_aplicacao = pyqtSignal()  # Para fechar a aplicação

    def __init__(self, excel_handler, dados_inseridos, posicao_inserida, msg_db=None):
        super().__init__()
        self.excel_handler = excel_handler
        self.dados_inseridos = dados_inseridos
        self.posicao_inserida = posicao_inserida
        self.msg_db = msg_db  # Status da sincronizacao com PostgreSQL
        self.arquivo_salvo = None
        self.init_ui()

    def init_ui(self):
        """Inicializa a interface da tela."""
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Mensagem de sucesso
        frame_sucesso = QFrame()
        frame_sucesso.setStyleSheet(f"""
            QFrame {{
                background-color: #D5F4E6;
                border: 2px solid {COLORS['success']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        frame_layout = QVBoxLayout()

        icone_sucesso = QLabel("✅")
        icone_sucesso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icone_font = QFont()
        icone_font.setPointSize(48)
        icone_sucesso.setFont(icone_font)
        frame_layout.addWidget(icone_sucesso)

        msg_sucesso = QLabel("Registro inserido com sucesso!")
        msg_sucesso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_font = QFont()
        msg_font.setPointSize(18)
        msg_font.setBold(True)
        msg_sucesso.setFont(msg_font)
        msg_sucesso.setStyleSheet(f"color: {COLORS['success']};")
        frame_layout.addWidget(msg_sucesso)

        frame_sucesso.setLayout(frame_layout)
        layout.addWidget(frame_sucesso)

        # Informações sobre a inserção
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout()

        if self.posicao_inserida > 0:
            label_posicao = QLabel(f"📍 Nova linha inserida na posição {self.posicao_inserida}")
            label_posicao.setStyleSheet("font-size: 13px; color: #2C3E50;")
            info_layout.addWidget(label_posicao)

        info_arquivo = self.excel_handler.obter_info_arquivo()
        label_total = QLabel(f"📊 Planilha agora possui {info_arquivo['total_registros']} registros")
        label_total.setStyleSheet("font-size: 13px; color: #2C3E50; font-weight: bold;")
        info_layout.addWidget(label_total)

        label_ordenado = QLabel("✓ Registro inserido ordenado por Data do Fato")
        label_ordenado.setStyleSheet("font-size: 12px; color: #7F8C8D; font-style: italic;")
        info_layout.addWidget(label_ordenado)

        # Status do PostgreSQL (se disponivel)
        if self.msg_db:
            if "Sincronizado" in self.msg_db:
                label_db = QLabel(f"🗄️ {self.msg_db}")
                label_db.setStyleSheet("font-size: 12px; color: #27AE60; font-weight: bold;")
            else:
                label_db = QLabel(f"⚠️ {self.msg_db}")
                label_db.setStyleSheet("font-size: 12px; color: #E67E22;")
            info_layout.addWidget(label_db)

        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # Preview dos dados inseridos
        preview_label = QLabel("Dados Inseridos:")
        preview_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(preview_label)

        self.criar_preview_tabela(layout)

        # Botões de ação
        layout.addStretch()
        self.criar_botoes_acao(layout)

        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {COLORS['background']};")

    def criar_preview_tabela(self, layout):
        """Cria tabela com preview dos dados principais."""
        tabela = QTableWidget()
        tabela.setColumnCount(2)
        tabela.setHorizontalHeaderLabels(["Campo", "Valor"])
        tabela.horizontalHeader().setStretchLastSection(True)
        tabela.setMaximumHeight(300)

        # Campos principais para mostrar no preview
        campos_preview = [
            ('Vítima', self.dados_inseridos.get('Vítima', '')),
            ('Data do Fato', self.formatar_data(self.dados_inseridos.get('Data do Fato'))),
            ('Hora do Fato', self.dados_inseridos.get('Hora do fato', '')),
            ('Município', self.dados_inseridos.get('Município do Fato', '')),
            ('Tipo de Acidente', self.dados_inseridos.get('Tipo de Acidente', '')),
            ('Sexo', self.dados_inseridos.get('Sexo', '')),
            ('Idade', str(self.dados_inseridos.get('Idade', '')) if self.dados_inseridos.get('Idade') else 'N/A'),
            ('Nº do BO', self.dados_inseridos.get('Nº do BO', '')),
        ]

        tabela.setRowCount(len(campos_preview))

        for i, (campo, valor) in enumerate(campos_preview):
            item_campo = QTableWidgetItem(campo)
            item_campo.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            tabela.setItem(i, 0, item_campo)

            item_valor = QTableWidgetItem(str(valor))
            tabela.setItem(i, 1, item_valor)

        tabela.resizeColumnsToContents()
        layout.addWidget(tabela)

    def criar_botoes_acao(self, layout):
        """Cria os botões de ação."""
        botoes_layout = QHBoxLayout()

        # Botão Cadastrar Outro
        btn_cadastrar = QPushButton("← Cadastrar Outro")
        btn_cadastrar.setMinimumHeight(45)
        btn_cadastrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 150px;
            }}
            QPushButton:hover {{
                background-color: #2980B9;
            }}
        """)
        btn_cadastrar.clicked.connect(self.cadastrar_outro_registro)
        botoes_layout.addWidget(btn_cadastrar)

        # Botão Baixar Planilha
        btn_baixar = QPushButton("📥 Baixar Planilha Atualizada")
        btn_baixar.setMinimumHeight(45)
        btn_baixar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        btn_baixar.clicked.connect(self.baixar_planilha)
        botoes_layout.addWidget(btn_baixar)

        # Botão Fechar
        btn_fechar = QPushButton("✕ Fechar")
        btn_fechar.setMinimumHeight(45)
        btn_fechar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['danger']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #C0392B;
            }}
        """)
        btn_fechar.clicked.connect(self.fechar)
        botoes_layout.addWidget(btn_fechar)

        layout.addLayout(botoes_layout)

    def formatar_data(self, data):
        """Formata data para exibição."""
        if data:
            try:
                return data.strftime("%d/%m/%Y")
            except:
                return str(data)
        return ""

    def baixar_planilha(self):
        """Abre dialog para salvar a planilha atualizada."""
        # Sugere nome de arquivo
        nome_original = os.path.basename(self.excel_handler.caminho_arquivo)
        nome_base, extensao = os.path.splitext(nome_original)
        nome_sugerido = f"{nome_base}_atualizado{extensao}"

        arquivo_destino, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Planilha Atualizada",
            nome_sugerido,
            "Arquivos Excel (*.xlsx)"
        )

        if arquivo_destino:
            # Garante extensão .xlsx
            if not arquivo_destino.endswith('.xlsx'):
                arquivo_destino += '.xlsx'

            # Salva o arquivo
            sucesso, mensagem = self.excel_handler.salvar_arquivo(arquivo_destino)

            if sucesso:
                self.arquivo_salvo = arquivo_destino

                # Mostra mensagem de sucesso com opções
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Arquivo Salvo")
                msg.setText(f"Arquivo salvo com sucesso!")
                msg.setInformativeText(f"Local: {arquivo_destino}")

                btn_abrir_pasta = msg.addButton("Abrir Pasta", QMessageBox.ButtonRole.ActionRole)
                btn_abrir_arquivo = msg.addButton("Abrir Arquivo", QMessageBox.ButtonRole.ActionRole)
                btn_ok = msg.addButton(QMessageBox.StandardButton.Ok)

                msg.exec()

                # Verifica qual botão foi clicado
                if msg.clickedButton() == btn_abrir_pasta:
                    self.abrir_pasta(arquivo_destino)
                elif msg.clickedButton() == btn_abrir_arquivo:
                    self.abrir_arquivo(arquivo_destino)

            else:
                QMessageBox.critical(self, "Erro ao Salvar", mensagem)

    def abrir_pasta(self, caminho_arquivo):
        """Abre a pasta contendo o arquivo."""
        pasta = os.path.dirname(caminho_arquivo)

        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(pasta)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", pasta])
            else:  # Linux
                subprocess.run(["xdg-open", pasta])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir a pasta: {e}")

    def abrir_arquivo(self, caminho_arquivo):
        """Abre o arquivo Excel."""
        try:
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(caminho_arquivo)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", caminho_arquivo])
            else:  # Linux
                subprocess.run(["xdg-open", caminho_arquivo])
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir o arquivo: {e}")

    def cadastrar_outro_registro(self):
        """Emite signal para cadastrar outro registro."""
        self.cadastrar_outro.emit()

    def fechar(self):
        """Emite signal para fechar a aplicação."""
        self.fechar_aplicacao.emit()
