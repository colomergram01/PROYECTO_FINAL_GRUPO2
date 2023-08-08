

import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QGridLayout
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class UpdateHandler(QObject):
    update_received = pyqtSignal(str)

class TicTacToeClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe - Cliente")
        self.setGeometry(100, 100, 300, 400)

        self.init_ui()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 1234)
        self.client_socket.connect(server_address)

        self.update_handler = UpdateHandler()
        self.update_handler.update_received.connect(self.handle_update)

        threading.Thread(target=self.receive_updates).start()

    def init_ui(self):
        layout = QVBoxLayout()
        self.username_label = QLabel("Nombre de Usuario:")
        layout.addWidget(self.username_label)

        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        self.board_buttons = [[None, None, None], [None, None, None], [None, None, None]]
        grid_layout = QGridLayout()

        for row in range(3):
            for col in range(3):
                button = QPushButton("", self)
                button.clicked.connect(lambda _, r=row, c=col: self.send_move(r, c))
                self.board_buttons[row][col] = button
                grid_layout.addWidget(button, row, col)

        layout.addLayout(grid_layout)

        self.chat_input = QLineEdit()
        layout.addWidget(self.chat_input)

        self.chat_button = QPushButton("Enviar mensaje de chat")
        self.chat_button.clicked.connect(self.send_chat_message)
        layout.addWidget(self.chat_button)

        self.scores_label = QLabel("Puntajes: X - 0, O - 0")
        layout.addWidget(self.scores_label)

        self.board_display = QTextEdit()
        self.board_display.setReadOnly(True)
        layout.addWidget(self.board_display)

        self.setLayout(layout)

    def handle_update(self, message):
        if message.startswith("<Board>"):
            self.update_board_display(message)
        # Resto de la función handle_update (igual a tu implementación actual)

    def update_board_display(self, board_xml):
        from xml.etree import ElementTree

        root = ElementTree.fromstring(board_xml)
        rows = root.findall('Row')
        board_data = [[cell.text for cell in row.findall('Cell')] for row in rows]

        for row in range(3):
            for col in range(3):
                self.board_buttons[row][col].setText(board_data[row][col])

    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                message = data.decode()
                self.update_handler.update_received.emit(message)
            except Exception as e:
                print(f"Error: {e}")
                break
        self.client_socket.close()

    def send_move(self, row, col):
        move = f"{row},{col}"
        self.client_socket.sendall(move.encode())

    def send_chat_message(self):
        message = self.chat_input.text()
        if self.client_socket:
            self.client_socket.sendall(f"/chat {message}".encode())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TicTacToeClient()
    client.show()
    sys.exit(app.exec_())
