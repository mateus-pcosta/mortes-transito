from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QMessageBox, QFrame,
                             QLineEdit, QDialog, QDialogButtonBox, QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.excel_handler import ExcelHandler
from utils.sheets_handler import SheetsHandler
from utils.dados_estaticos import COLORS


class TelaSelecaoModo(QWidget):

    # Signals
    modo_excel_selecionado = pyqtSignal(object)  # Emite ExcelHandler
    modo_sheets_selecionado = pyqtSignal(object)  # Emite SheetsHandler

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 40, 50, 40)

        # Título
        titulo = QLabel("Sistema de Cadastro - Mortes no Trânsito")
        titulo_font = QFont()
        titulo_font.setPointSize(20)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: white; background-color: transparent; margin-bottom: 20px;")
        titulo.setWordWrap(True)
        layout.addWidget(titulo)

        # Subtítulo
        subtitulo = QLabel("Escolha o modo de operação:")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo_font = QFont()
        subtitulo_font.setPointSize(14)
        subtitulo.setFont(subtitulo_font)
        subtitulo.setStyleSheet(f"color: {COLORS['info']}; background-color: transparent; margin-bottom: 30px;")
        layout.addWidget(subtitulo)

        # Espaçador
        layout.addStretch(1)

        # Botão Excel
        btn_excel = QPushButton("📂 ARQUIVO EXCEL LOCAL")
        btn_excel.setMinimumHeight(80)
        btn_excel.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
            }}
            QPushButton:hover {{
                background-color: #2980B9;
            }}
        """)
        btn_excel.clicked.connect(self.selecionar_excel)
        layout.addWidget(btn_excel)

        # Espaçador
        layout.addSpacing(20)

        # Botão Google Sheets
        btn_sheets = QPushButton("☁️ GOOGLE SHEETS ONLINE")
        btn_sheets.setMinimumHeight(80)
        btn_sheets.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
        """)
        btn_sheets.clicked.connect(self.conectar_sheets)
        layout.addWidget(btn_sheets)

        # Espaçador
        layout.addStretch(1)

        self.setLayout(layout)

        # Estilo global
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
        """)

    def selecionar_excel(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Planilha Excel",
            "",
            "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)"
        )

        if arquivo:
            self.carregar_excel(arquivo)

    def carregar_excel(self, caminho: str):
        handler = ExcelHandler()
        sucesso, mensagem = handler.carregar_arquivo(caminho)

        if sucesso:
            self.modo_excel_selecionado.emit(handler)
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Erro ao Carregar")
            msg_box.setText(mensagem)
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()

    def conectar_sheets(self):
        dialog = DialogSheetsConfig(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            credentials_path, spreadsheet_url = dialog.get_dados()
            self.carregar_sheets(credentials_path, spreadsheet_url)

    def carregar_sheets(self, credentials_path: str, spreadsheet_url: str):
        # Mostra mensagem de carregamento
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt

        progress = QProgressDialog("Conectando ao Google Sheets...", None, 0, 0, self)
        progress.setWindowTitle("Aguarde")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setCancelButton(None)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()

        try:
            handler = SheetsHandler(credentials_path, spreadsheet_url)

            # Autentica
            progress.setLabelText("Autenticando com Google...")
            sucesso_auth, msg_auth = handler.autenticar()
            if not sucesso_auth:
                progress.close()
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("Erro de Autenticação")
                msg_box.setText(msg_auth)
                msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
                msg_box.exec()
                return

            # Carrega planilha
            progress.setLabelText("Carregando planilha...")
            sucesso_load, msg_load = handler.carregar_planilha()
            progress.close()

            if sucesso_load:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("Conexão Estabelecida")
                msg_box.setText(f"Conectado com sucesso!\n\n{msg_load}")
                msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
                msg_box.exec()
                self.modo_sheets_selecionado.emit(handler)
            else:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("Erro ao Carregar Planilha")
                msg_box.setText(msg_load)
                msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
                msg_box.exec()
        except Exception as e:
            progress.close()
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Erro")
            msg_box.setText(f"Erro inesperado: {str(e)}")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()


class DialogSheetsConfig(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conectar ao Google Sheets")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        titulo = QLabel("Configuração do Google Sheets")
        titulo_font = QFont()
        titulo_font.setPointSize(14)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setStyleSheet("color: black;")
        layout.addWidget(titulo)

        # Botão de carregar configuração salva
        btn_carregar_config = QPushButton("📋 Carregar Configuração Salva")
        btn_carregar_config.setStyleSheet("color: #3498DB; font-size: 11px;")
        btn_carregar_config.clicked.connect(self.carregar_config_salva)
        layout.addWidget(btn_carregar_config)

        # Instruções
        instrucoes = QLabel(
            "Para conectar ao Google Sheets, você precisa:\n\n"
            "1. Arquivo de credenciais JSON (Service Account)\n"
            "2. URL da planilha do Google Sheets\n\n"
            "Confira o README para instruções detalhadas."
        )
        instrucoes.setStyleSheet("color: #555555; font-size: 11px; margin: 10px 0;")
        instrucoes.setWordWrap(True)
        layout.addWidget(instrucoes)

        # Formulário
        form = QFormLayout()

        # Credenciais
        self.input_credentials = QLineEdit()
        self.input_credentials.setPlaceholderText("Caminho para o arquivo credentials.json")
        self.input_credentials.setStyleSheet("color: black; background-color: white;")

        btn_browse_cred = QPushButton("📁 Procurar")
        btn_browse_cred.setStyleSheet("color: black;")
        btn_browse_cred.clicked.connect(self.procurar_credentials)

        cred_layout = QHBoxLayout()
        cred_layout.addWidget(self.input_credentials)
        cred_layout.addWidget(btn_browse_cred)

        form.addRow("Arquivo de Credenciais:", cred_layout)

        # URL da planilha
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        self.input_url.setStyleSheet("color: black; background-color: white;")
        form.addRow("URL da Planilha:", self.input_url)

        layout.addLayout(form)

        # Botões
        botoes = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        layout.addWidget(botoes)

        self.setLayout(layout)

        # Estilo global do dialog
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLabel {
                color: black;
            }
            QPushButton {
                color: black;
            }
        """)

    def carregar_config_salva(self):

        import os
        config_path = "config_sheets.txt"

        if not os.path.exists(config_path):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Arquivo não encontrado")
            msg_box.setText(f"Arquivo {config_path} não encontrado.\n\nPreencha manualmente os campos abaixo.")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                linhas = f.readlines()

            credentials_path = ""
            spreadsheet_url = ""

            for i, linha in enumerate(linhas):
                if linha.strip().startswith("c:") or linha.strip().startswith("C:"):
                    credentials_path = linha.strip()
                elif "spreadsheets/d/" in linha:
                    spreadsheet_url = linha.strip()

            if credentials_path:
                self.input_credentials.setText(credentials_path)
            if spreadsheet_url:
                self.input_url.setText(spreadsheet_url)

            if credentials_path and spreadsheet_url:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setWindowTitle("Configuração Carregada")
                msg_box.setText("Configuração carregada com sucesso!")
                msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
                msg_box.exec()
            else:
                msg_box = QMessageBox(self)
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.setWindowTitle("Configuração Incompleta")
                msg_box.setText("Não foi possível carregar toda a configuração.\nVerifique o arquivo config_sheets.txt")
                msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
                msg_box.exec()
        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Erro ao Carregar")
            msg_box.setText(f"Erro ao ler arquivo de configuração:\n{str(e)}")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()

    def procurar_credentials(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo de Credenciais",
            "",
            "Arquivos JSON (*.json);;Todos os arquivos (*.*)"
        )
        if arquivo:
            self.input_credentials.setText(arquivo)

    def get_dados(self) -> tuple:
        return (
            self.input_credentials.text().strip(),
            self.input_url.text().strip()
        )

    def accept(self):
        if not self.input_credentials.text().strip():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Atenção")
            msg_box.setText("Selecione o arquivo de credenciais.")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()
            return

        if not self.input_url.text().strip():
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Atenção")
            msg_box.setText("Insira a URL da planilha.")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()
            return

        super().accept()
