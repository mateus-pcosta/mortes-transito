from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from utils.excel_handler import ExcelHandler
from utils.dados_estaticos import COLORS


class TelaSelecao(QWidget):

    # Signal emitido quando arquivo válido é selecionado e usuário clica em Continuar
    arquivo_selecionado = pyqtSignal(object)  # Emite o ExcelHandler

    def __init__(self):
        super().__init__()
        self.excel_handler = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 30, 50, 30)

        # Título
        titulo = QLabel("Sistema de Cadastro - Mortes no Trânsito")
        titulo_font = QFont()
        titulo_font.setPointSize(20)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: white; margin: 20px;")
        layout.addWidget(titulo)

        # Label informativo
        info_label = QLabel("Selecione a planilha Excel para atualizar")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_font = QFont()
        info_font.setPointSize(12)
        info_label.setFont(info_font)
        info_label.setStyleSheet(f"color: {COLORS['info']}; margin: 10px;")
        layout.addWidget(info_label)

        # Espaçador
        layout.addStretch(1)

        # Botão de seleção de arquivo
        self.btn_selecionar = QPushButton("📁 Selecionar Arquivo Excel")
        self.btn_selecionar.setMinimumHeight(60)
        self.btn_selecionar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: #2980B9;
            }}
            QPushButton:pressed {{
                background-color: #21618C;
            }}
        """)
        self.btn_selecionar.clicked.connect(self.selecionar_arquivo)
        layout.addWidget(self.btn_selecionar)

        # Frame para mostrar informações do arquivo selecionado
        self.frame_info = QFrame()
        self.frame_info.setFrameShape(QFrame.Shape.NoFrame)  # Remove borda padrão
        self.frame_info.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS['info']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        frame_layout = QVBoxLayout()

        self.label_arquivo = QLabel("Nenhum arquivo selecionado")
        self.label_arquivo.setWordWrap(True)
        self.label_arquivo.setStyleSheet(f"color: {COLORS['info']}; font-size: 11px;")
        frame_layout.addWidget(self.label_arquivo)

        self.label_info_registros = QLabel("")
        self.label_info_registros.setStyleSheet(f"color: {COLORS['text']}; font-size: 12px; font-weight: bold;")
        frame_layout.addWidget(self.label_info_registros)

        self.label_info_data = QLabel("")
        self.label_info_data.setStyleSheet(f"color: {COLORS['text']}; font-size: 11px;")
        frame_layout.addWidget(self.label_info_data)

        self.frame_info.setLayout(frame_layout)
        self.frame_info.hide()  # Esconde inicialmente
        layout.addWidget(self.frame_info)

        # Espaçador
        layout.addStretch(1)

        # Botão Continuar
        self.btn_continuar = QPushButton("Continuar →")
        self.btn_continuar.setMinimumHeight(50)
        self.btn_continuar.setEnabled(False)  # Desabilitado inicialmente
        self.btn_continuar.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['success']};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
            QPushButton:pressed {{
                background-color: #1E8449;
            }}
            QPushButton:disabled {{
                background-color: {COLORS['info']};
                color: #7F8C8D;
            }}
        """)
        self.btn_continuar.clicked.connect(self.continuar)
        layout.addWidget(self.btn_continuar)

        self.setLayout(layout)

        # Define estilo global para a tela
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
            }}
            QLabel {{
                background-color: transparent;
            }}
        """)

    def selecionar_arquivo(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Planilha Excel",
            "",
            "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)"
        )

        if arquivo:
            self.carregar_arquivo(arquivo)

    def carregar_arquivo(self, caminho: str):
        # Cria handler e tenta carregar
        self.excel_handler = ExcelHandler()
        sucesso, mensagem = self.excel_handler.carregar_arquivo(caminho)

        if sucesso:
            # Arquivo válido - mostra informações
            self.label_arquivo.setText(f"📄 {caminho}")
            self.label_arquivo.setStyleSheet(f"color: {COLORS['success']}; font-size: 11px;")

            # Obtém informações do arquivo
            info = self.excel_handler.obter_info_arquivo()

            self.label_info_registros.setText(f"✓ {info['total_registros']} registros encontrados")

            if info['ultima_data']:
                data_formatada = info['ultima_data'].strftime("%d/%m/%Y")
                self.label_info_data.setText(f"Último registro: {data_formatada}")
            else:
                self.label_info_data.setText("Último registro: data não disponível")

            # Mostra o frame de informações
            self.frame_info.show()
            self.frame_info.setStyleSheet(f"""
                QFrame {{
                    background-color: #E8F8F5;
                    border: 2px solid {COLORS['success']};
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)

            # Habilita botão continuar
            self.btn_continuar.setEnabled(True)

        else:
            # Arquivo inválido - mostra erro
            QMessageBox.critical(
                self,
                "Arquivo Inválido",
                mensagem
            )

            # Reseta interface
            self.label_arquivo.setText("Nenhum arquivo selecionado")
            self.label_arquivo.setStyleSheet(f"color: {COLORS['info']}; font-size: 11px;")
            self.label_info_registros.setText("")
            self.label_info_data.setText("")
            self.frame_info.hide()
            self.btn_continuar.setEnabled(False)
            self.excel_handler = None

    def continuar(self):
        if self.excel_handler and self.excel_handler.dados_carregados:
            self.arquivo_selecionado.emit(self.excel_handler)
