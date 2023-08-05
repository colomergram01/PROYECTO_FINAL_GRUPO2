
import sys
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout, QMessageBox


class TicTacToeClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe - Cliente")
        self.setGeometry(100, 100, 300, 350)
        self.init_ui()

    def init_ui(self):
        # Etiqueta para mostrar el turno del jugador
        self.turno_label = QLabel("Esperando conexión...")

        # Matriz de botones para representar el tablero
        self.botones = [[QPushButton() for _ in range(3)] for _ in range(3)]

        # Asignar una función a cada botón cuando se haga clic
        for i in range(3):
            for j in range(3):
                self.botones[i][j].setFixedSize(80, 80)  # Tamaño fijo para los botones
                self.botones[i][j].clicked.connect(lambda _, x=i, y=j: self.realizar_movimiento(x, y))

        # Diseño de la interfaz utilizando QGridLayout
        grid_layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                grid_layout.addWidget(self.botones[i][j], i, j)

        vbox = QVBoxLayout()
        vbox.addWidget(self.turno_label)
        vbox.addLayout(grid_layout)

        self.setLayout(vbox)
        self.show()

        self.conectar_servidor()

    def conectar_servidor(self):
        self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "localhost"  # Cambiar esto a la dirección IP del servidor si se encuentra en otra máquina
        self.port = 8080  # Puerto para la conexión

        try:
            self.cliente_socket.connect((self.host, self.port))
            self.turno_label.setText("Conexión establecida. ¡Es tu turno!")
            self.recibir_datos_servidor()

        except Exception as e:
            self.turno_label.setText(f"Error al conectar con el servidor: {e}")

    def realizar_movimiento(self, x, y):
        # Comprobar si la casilla está vacía antes de realizar el movimiento
        if self.botones[x][y].text() == "":
            self.botones[x][y].setText("X")
            self.enviar_datos_servidor(f"X{x},{y}")

    def recibir_datos_servidor(self):
        while True:
            try:
                datos = self.cliente_socket.recv(1024).decode()
                if not datos:
                    break

                self.actualizar_tablero(datos)

            except ConnectionResetError as e:
                print("Error al recibir datos del servidor: la conexión se cerró inesperadamente.")
                self.cliente_socket.close()
                break
            except Exception as e:
                print(f"Error al recibir datos del servidor: {e}")
                self.cliente_socket.close()
                break
          #Porga
        self.cliente_socket.close()

    def actualizar_tablero(self, datos):
        jugador, movimiento = datos.split(":")
        x, y = map(int, movimiento.split(","))
        self.botones[x][y].setText("O") if jugador == "X" else self.botones[x][y].setText("X")
        self.turno_label.setText("¡Es tu turno!" if jugador == "O" else "Esperando turno del otro jugador")

    def enviar_datos_servidor(self, datos):
        try:
            self.cliente_socket.send(datos.encode())
        except BrokenPipeError as e:
            print("Error al enviar datos al servidor: la conexión se cerró inesperadamente.")
            self.cliente_socket.close()
        except Exception as e:
            print(f"Error al enviar datos al servidor: {e}")
            self.cliente_socket.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeClient()
    sys.exit(app.exec_())