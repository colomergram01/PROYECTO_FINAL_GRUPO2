import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit

class TicTacToeServer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe - Servidor")
        self.setGeometry(100, 100, 300, 400)

        self.init_ui()

        # Crear un socket TCP/IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Asignar una dirección y puerto al servidor
        server_address = ('localhost', 12345)
        self.server_socket.bind(server_address)

        # Escuchar conexiones entrantes
        self.server_socket.listen(2)
        self.log_text.append("Esperando jugadores...")

        # Inicializar el estado del tablero y el turno del juego
        self.board = [[None, None, None] for _ in range(3)]
        self.current_turn = 'X'

        # Lista para almacenar las conexiones de los jugadores
        self.clients = []

        # Crear un hilo para aceptar conexiones de clientes
        threading.Thread(target=self.accept_clients).start()

    def init_ui(self):
        layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def accept_clients(self):
        while len(self.clients) < 2:
            # Aceptar una nueva conexión
            client_socket, client_address = self.server_socket.accept()
            self.log_text.append("Jugador conectado: {}".format(client_address))

            # Agregar el cliente a la lista
            self.clients.append(client_socket)

            # Crear un hilo para manejar las comunicaciones del cliente
            player = 'X' if len(self.clients) == 1 else 'O'
            threading.Thread(target=self.handle_client, args=(client_socket, player)).start()

    def handle_client(self, client_socket, player):
        while True:
            try:
                # Recibir el movimiento del jugador
                data = client_socket.recv(1024)
                if not data:
                    break

                # Decodificar el movimiento recibido (Ejemplo: '1,2' para fila 1, columna 2)
                row, column = map(int, data.decode().strip().split(','))

                # Verificar si es el turno del jugador y el movimiento es válido
                if player == self.current_turn and self.board[row][column] is None:
                    self.board[row][column] = player

                    # Verificar si el jugador ha ganado
                    if self.check_win(player):
                        # Enviar mensaje de victoria al jugador
                        message = "Victory,{}".format(player)
                        client_socket.sendall(message.encode())

                    else:
                        # Cambiar el turno al otro jugador
                        self.current_turn = 'X' if self.current_turn == 'O' else 'O'

                        # Verificar si el juego ha terminado en empate
                        if all(all(cell is not None for cell in row) for row in self.board):
                            # Enviar mensaje de empate a ambos jugadores
                            message = "Draw"
                            for client in self.clients:
                                client.sendall(message.encode())

                        else:
                            # Enviar el nuevo estado del tablero a ambos jugadores
                            for client in self.clients:
                                client.sendall(self.board_to_bytes())

            except Exception as e:
                print("Error: {}".format(e))
                break

        client_socket.close()

    def check_win(self, player):
            # Verificar las filas
            for row in self.board:
                if all(cell == player for cell in row):
                        return True

                # Verificar las columnas
            for col in range(3):
                if all(self.board[row][col] == player for row in range(3)):
                        return True

                # Verificar las diagonales
            if all(self.board[i][i] == player for i in range(3)) or all(self.board[i][2 - i] == player for i in range(3)):
                return True

            return False

    def board_to_bytes(self):
        # Convertir el estado del tablero a una cadena de bytes en formato XML
        xml_board = '<Board>{}</Board>'.format("".join(["<Row>{}</Row>".format("".join(["<Cell>{}</Cell>".format(cell) for cell in row])) for row in self.board]))
        return xml_board.encode()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = TicTacToeServer()
    server.show()
    sys.exit(app.exec_())
