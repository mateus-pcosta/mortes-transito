import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from interface.tela_selecao_modo import TelaSelecaoModo
from interface.tela_cadastro import TelaCadastro
from interface.tela_confirmacao import TelaConfirmacao
from utils.database_handler import DatabaseHandler


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.excel_handler = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Sistema de Cadastro - Mortes no Trânsito")
        self.setMinimumSize(700, 600)
        self.resize(800, 650)

        # Widget central com stack de telas
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.tela_selecao = TelaSelecaoModo()
        self.tela_selecao.modo_excel_selecionado.connect(self.mostrar_tela_cadastro)
        self.tela_selecao.modo_sheets_selecionado.connect(self.mostrar_tela_cadastro)
        self.stack.addWidget(self.tela_selecao)

        self.centralizar_janela()

    def centralizar_janela(self):
        frame_geometry = self.frameGeometry()
        screen_center = self.screen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def mostrar_tela_cadastro(self, excel_handler):
        self.excel_handler = excel_handler

        # Cria tela de cadastro
        tela_cadastro = TelaCadastro(excel_handler)
        tela_cadastro.cadastro_finalizado.connect(self.processar_cadastro)
        tela_cadastro.voltar_solicitado.connect(self.voltar_para_selecao)

        # Adiciona ao stack e mostra
        self.stack.addWidget(tela_cadastro)
        self.stack.setCurrentWidget(tela_cadastro)

    def processar_cadastro(self, dados):
        # Insere o registro no Google Sheets/Excel
        sucesso, mensagem, posicao = self.excel_handler.inserir_registro(dados)

        if sucesso:
            # Tenta sincronizar com PostgreSQL
            msg_db = self.sincronizar_postgresql(dados)

            # Mostra tela de confirmação
            tela_confirmacao = TelaConfirmacao(self.excel_handler, dados, posicao, msg_db)
            tela_confirmacao.cadastrar_outro.connect(self.cadastrar_outro)
            tela_confirmacao.fechar_aplicacao.connect(self.fechar_aplicacao)

            self.stack.addWidget(tela_confirmacao)
            self.stack.setCurrentWidget(tela_confirmacao)
        else:
            # Mostra erro
            QMessageBox.critical(
                self,
                "Erro ao Inserir Registro",
                mensagem
            )

    def sincronizar_postgresql(self, dados):
        """
        Sincroniza os dados com o banco PostgreSQL da SSP.

        Args:
            dados: Dicionario com os dados do formulario

        Returns:
            Mensagem de status da sincronizacao
        """
        try:
            db_handler = DatabaseHandler()
            sucesso, mensagem = db_handler.inserir_registro(dados)
            db_handler.desconectar()

            if sucesso:
                return "PostgreSQL: Sincronizado"
            else:
                return f"PostgreSQL: Erro - {mensagem}"

        except Exception as e:
            return f"PostgreSQL: Erro - {str(e)}"

    def cadastrar_outro(self):
        # Remove telas antigas do stack (mantém só a primeira)
        while self.stack.count() > 1:
            widget = self.stack.widget(1)
            self.stack.removeWidget(widget)
            widget.deleteLater()

        # Cria nova tela de cadastro
        self.mostrar_tela_cadastro(self.excel_handler)

    def voltar_para_selecao(self):
        resposta = QMessageBox.question(
            self,
            "Voltar",
            "Deseja voltar para a tela de seleção? Os dados não salvos serão perdidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            # Remove todas as telas exceto a primeira
            while self.stack.count() > 1:
                widget = self.stack.widget(1)
                self.stack.removeWidget(widget)
                widget.deleteLater()

            # Volta para a tela de seleção
            self.stack.setCurrentIndex(0)

    def fechar_aplicacao(self):
        resposta = QMessageBox.question(
            self,
            "Fechar",
            "Deseja fechar a aplicação?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            self.close()

    def closeEvent(self, event):
        """Confirma antes de fechar a janela."""
        if self.stack.currentIndex() > 0:  # Não está na tela inicial
            resposta = QMessageBox.question(
                self,
                "Fechar Aplicação",
                "Tem certeza que deseja sair? Dados não salvos serão perdidos.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if resposta == QMessageBox.StandardButton.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    # Cria a aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("Sistema de Cadastro - Mortes no Trânsito")

    # Define estilo global
    app.setStyle("Fusion")

    # Cria e mostra janela principal
    janela = MainWindow()
    janela.show()

    # Executa o loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
