import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit

class TicTacToeClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe - Cliente")
        self.setGeometry(100, 100, 300, 400)

        self.init_ui()

        # Crear un socket TCP/IP
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Conectar al servidor
        server_address = ('localhost', 12345)
        self.client_socket.connect(server_address)

        # Crear un hilo para recibir actualizaciones del servidor
        threading.Thread(target=self.receive_updates).start()

    def init_ui(self):
        layout = QVBoxLayout()

        self.board_display = QTextEdit()
        self.board_display.setReadOnly(True)
        layout.addWidget(self.board_display)

        self.move_input = QLineEdit()
        layout.addWidget(self.move_input)

        self.move_button = QPushButton("Realizar movimiento")
        self.move_button.clicked.connect(self.send_move)
        layout.addWidget(self.move_button)

        # Caja de texto para escribir mensajes de chat
        self.chat_input = QLineEdit()
        layout.addWidget(self.chat_input)

        # Botón para enviar mensajes de chat
        self.chat_button = QPushButton("Enviar mensaje de chat")
        self.chat_button.clicked.connect(self.send_chat_message)
        layout.addWidget(self.chat_button)

        # Etiqueta para mostrar los puntajes
        self.scores_label = QLabel("Puntajes: X - 0, O - 0")
        layout.addWidget(self.scores_label)


        self.setLayout(layout)
    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break

                # Decodificar el mensaje recibido
                message = data.decode()

                # Si el mensaje comienza con "/chat", es un mensaje de chat
                if message.startswith("/chat"):
                    # Mostrar el mensaje de chat en la interfaz
                    chat_message = message[6:]
                    self.board_display.append(chat_message)
                elif message.startswith("Scores"):
                    # Mostrar los puntajes en la interfaz
                    scores = message.split(',')[1:]
                    self.scores_label.setText("Puntajes: " + ", ".join(scores))

                # Separar el mensaje y el jugador (si es una victoria)
                parts = message.split(',')
                if len(parts) == 2 and parts[0] == "Victory":
                    winner = parts[1]
                    if winner == self.player:
                        self.board_display.setPlainText("¡Has ganado!")
                    else:
                        self.board_display.setPlainText("¡Has perdido!")

                elif message == "Draw":
                    # Notificar al usuario que el juego ha terminado en empate
                    self.board_display.setPlainText("¡Empate!")

                else:
                    # Decodificar el estado del tablero recibido en formato XML y mostrarlo en la interfaz
                    xml_board = message
                    self.board_display.setPlainText(xml_board)

            except Exception as e:
                print(f"Error: {e}")
                break

        self.client_socket.close()
    def send_chat_message(self):
        # Leer el mensaje de chat del usuario desde la interfaz y enviarlo al servidor
        message = self.chat_input.text()
        self.client_socket.sendall("/chat{}".format(message).encode())


    def send_move(self):
        # Leer el movimiento del jugador desde la interfaz y enviarlo al servidor
        move = self.move_input.text()
        self.client_socket.sendall(move.encode())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TicTacToeClient()
    client.show()
    sys.exit(app.exec_())
