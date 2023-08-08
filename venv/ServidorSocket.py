
import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QGridLayout
class TicTacToeServer(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Tic Tac Toe - Servidor")
            self.setGeometry(100, 100, 300, 400)

            self.init_ui()

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = ('localhost', 1234)
            self.server_socket.bind(server_address)
            self.server_socket.listen(2)
            self.log_text.append("Esperando jugadores...")
            self.clients = []
            self.current_turn = 'X'  # Inicializa el turno al comienzo del juego
            self.board = [[None, None, None], [None, None, None],
                          [None, None, None]]  # Agrega la definición de la matriz board
            threading.Thread(target=self.accept_clients).start()

        def init_ui(self):
            layout = QVBoxLayout()

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            layout.addWidget(self.log_text)

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


            self.setLayout(layout)

        def accept_clients(self):
            while len(self.clients) < 2:
                client_socket, client_address = self.server_socket.accept()
                self.log_text.append("Jugador conectado: {}".format(client_address))
                self.clients.append(client_socket)
                player = 'X' if len(self.clients) == 1 else 'O'
                threading.Thread(target=self.handle_client, args=(client_socket, player)).start()

        def handle_client(self, client_socket, player):
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode()

                    if message.startswith("/chat"):
                        chat_message = message[6:]
                        self.handle_chat_message(chat_message)
                        self.log_text.append("Mensaje de chat: {}".format(chat_message))
                    else:
                        self.handle_game_move(player, message)

                except Exception as e:
                    print("Error: {}".format(e))
                    break

            client_socket.close()

        def handle_chat_message(self, chat_message):
            for client in self.clients:
                client.sendall("/chat {}".format(chat_message).encode())

        def handle_game_move(self, player, move):
            row, column = map(int, move.strip().split(','))

            if player == self.current_turn and self.board[row][column] is None:
                self.board[row][column] = player

                if self.check_win(player):
                    self.handle_victory(player)
                else:
                    self.switch_turn()
                    if self.check_draw():
                        self.handle_draw()
                    else:
                        self.send_board_state_to_clients()

        def send_board_state_to_clients(self):
            for row in range(3):
                for col in range(3):
                    value = self.board[row][col]
                    if value is None:
                        value = ""
                    self.board_buttons[row][col].setText(value)

        def handle_victory(self, player):
            message = "Victory,{}".format(player)
            for client in self.clients:
                client.sendall(message.encode())

        def handle_draw(self):
            message = "Draw"
            for client in self.clients:
                client.sendall(message.encode())

        def switch_turn(self):
            self.current_turn = 'X' if self.current_turn == 'O' else 'O'

        def check_win(self, player):
            for row in self.board:
                if all(cell == player for cell in row):
                    return True
            for col in range(3):
                if all(self.board[row][col] == player for row in range(3)):
                    return True
            if all(self.board[i][i] == player for i in range(3)) or all(
                    self.board[i][2 - i] == player for i in range(3)):
                return True
            return False

        def check_draw(self):
            return all(all(cell is not None for cell in row) for row in self.board)

        def send_move(self, row, col):
            player = 'X' if self.current_turn == 'X' else 'O'

            # Verificar si es el turno del jugador y la casilla está vacía
            if player == self.current_turn and self.board[row][col] is None:
                self.board[row][col] = player

                # Actualizar los botones en el servidor
                self.board_buttons[row][col].setText(player)

                # Enviar el movimiento a los clientes
                move = f"{row},{col}"
                for client in self.clients:
                    client.sendall(move.encode())

                # Verificar si hay un ganador o empate
                if self.check_win(player):
                    self.handle_victory(player)
                elif self.check_draw():
                    self.handle_draw()
                else:
                    self.switch_turn()

        def send_chat_message(self):
            message = self.chat_input.text()
            if self.client_socket:
                self.client_socket.sendall(f"/chat {message}".encode())
if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = TicTacToeServer()
    server.show()
    sys.exit(app.exec_())
