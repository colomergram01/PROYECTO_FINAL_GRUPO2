
import random
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout, QMessageBox, \
    QMainWindow, QAction, QMenu

# Representación del tablero (lista de listas)
tablero = [
    [" ", " ", " "],
    [" ", " ", " "],
    [" ", " ", " "]
]

# Variable para habilitar/deshabilitar el modo un jugador
modo_un_jugador = False  # False para modo multijugador, True para modo un jugador


class TicTacToeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tic Tac Toe")
        self.setGeometry(100, 100, 300, 350)  # Aumentamos la altura para agregar el botón "Reiniciar"
        self.init_ui()

    def init_ui(self):
        # Etiqueta para mostrar el turno del jugador
        self.turno_label = QLabel("Turno: Jugador X")

        # Matriz de botones para representar el tablero
        self.botones = [[QPushButton() for _ in range(3)] for _ in range(3)]

        # Botón "Reiniciar"
        self.btn_reiniciar = QPushButton("Reiniciar")
        self.btn_reiniciar.clicked.connect(self.reiniciar_juego)

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
        vbox.addWidget(self.btn_reiniciar)  # Agregamos el botón "Reiniciar" al diseño

        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)

        self.actualizar_tablero()
        self.show()

        # Crear el menú y las acciones
        menu = self.menuBar()
        modo_menu = menu.addMenu("Modo de Juego")

        jugador_vs_jugador_action = QAction("Jugador vs. Jugador", self)
        jugador_vs_jugador_action.triggered.connect(self.iniciar_modo_jugador_vs_jugador)
        modo_menu.addAction(jugador_vs_jugador_action)

        jugador_vs_computadora_action = QAction("Jugador vs. Computadora", self)
        jugador_vs_computadora_action.triggered.connect(self.iniciar_modo_jugador_vs_computadora)
        modo_menu.addAction(jugador_vs_computadora_action)

        # Iniciar el juego en el modo seleccionado por defecto
        if modo_un_jugador:
            self.iniciar_modo_jugador_vs_computadora()
        else:
            self.iniciar_modo_jugador_vs_jugador()

    def actualizar_tablero(self):
        for i in range(3):
            for j in range(3):
                self.botones[i][j].setText(tablero[i][j])

    def realizar_movimiento(self, x, y):
        # Comprobar si la casilla está vacía antes de realizar el movimiento
        if tablero[x][y] == " ":
            tablero[x][y] = "X" if self.turno_label.text() == "Turno: Jugador X" else "O"
            self.actualizar_tablero()
            if self.verificar_victoria():
                self.mostrar_mensaje_victoria(tablero[x][y])
            elif self.verificar_empate():
                self.mostrar_mensaje_empate()
            else:
                self.cambiar_turno()
                if modo_un_jugador and self.turno_label.text() == "Turno: Jugador O":
                    self.mover_computadora()

    def cambiar_turno(self):
        self.turno_label.setText(
            "Turno: Jugador O" if self.turno_label.text() == "Turno: Jugador X" else "Turno: Jugador X")

    def verificar_victoria(self):
        # Verificar filas
        for i in range(3):
            if tablero[i][0] == tablero[i][1] == tablero[i][2] != " ":
                return True

        # Verificar columnas
        for j in range(3):
            if tablero[0][j] == tablero[1][j] == tablero[2][j] != " ":
                return True

        # Verificar diagonal principal
        if tablero[0][0] == tablero[1][1] == tablero[2][2] != " ":
            return True

        # Verificar diagonal secundaria
        if tablero[0][2] == tablero[1][1] == tablero[2][0] != " ":
            return True

        return False

    def verificar_empate(self):
        return all(tablero[i][j] != " " for i in range(3) for j in range(3))

    def mostrar_mensaje_victoria(self, jugador):
        QMessageBox.information(self, "Fin del juego", f"¡El jugador {jugador} ha ganado!")

    def mostrar_mensaje_empate(self):
        QMessageBox.information(self, "Fin del juego", "¡El juego ha terminado en empate!")

    def reiniciar_juego(self):
        global tablero
        tablero = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]  # Reiniciamos el tablero
        self.actualizar_tablero()  # Actualizamos la interfaz para mostrar el tablero vacío
        self.turno_label.setText("Turno: Jugador X")  # Reiniciamos el turno

    def mover_computadora(self):
        # La computadora realizará un movimiento aleatorio
        # Primero, obtenemos las coordenadas de las casillas vacías
        casillas_vacias = [(i, j) for i in range(3) for j in range(3) if tablero[i][j] == " "]
        if casillas_vacias:
            x, y = random.choice(casillas_vacias)
            self.realizar_movimiento(x, y)

    def iniciar_modo_jugador_vs_jugador(self):
        global modo_un_jugador
        modo_un_jugador = False
        self.reiniciar_juego()

    def iniciar_modo_jugador_vs_computadora(self):
        global modo_un_jugador
        modo_un_jugador = True
        self.reiniciar_juego()


class ServidorTicTacToe:
    def __init__(self):
        self.host = "localhost"  # Cambia esto a la dirección IP de tu servidor si se encuentra en otra máquina
        self.port = 8080  # Puerto para la conexión
        self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_servidor.bind((self.host, self.port))
        self.socket_servidor.listen(2)  # Acepta hasta 2 conexiones simultáneas (Jugador vs. Jugador)

    def aceptar_conexiones(self):
        print("Esperando conexiones...")
        while True:
            cliente_socket, cliente_direccion = self.socket_servidor.accept()
            print(f"Conexión establecida con {cliente_direccion}")
            threading.Thread(target=self.manipular_cliente, args=(cliente_socket,)).start()

    def manipular_cliente(self, cliente_socket):
        while True:
            try:
                datos = cliente_socket.recv(1024).decode()
                if not datos:
                    break

                # Lógica para procesar los movimientos del cliente y actualizar el tablero
                # Aquí debes implementar la lógica para verificar la validez de los movimientos
                # y determinar el estado del juego (victoria, empate, etc.)
                # También enviarás las actualizaciones del tablero a los clientes conectados.

                # Por ahora, simplemente actualizamos el tablero con los datos recibidos del cliente
                # y enviamos la actualización a los otros clientes.
                self.actualizar_tablero(datos)
                self.enviar_actualizacion_tablero(datos, cliente_socket)

            except Exception as e:
                print(f"Error en la conexión con el cliente: {e}")
                break

        cliente_socket.close()

    def actualizar_tablero(self, datos):
        x, y = map(int, datos.split(","))
        if tablero[x][y] == " ":
            tablero[x][y] = "X" if datos.startswith("X") else "O"
            window.actualizar_tablero()  # Actualizar la interfaz de usuario
            window.cambiar_turno()  # Cambiar el turno en la interfaz de usuario

    def enviar_actualizacion_tablero(self, datos, cliente_socket):
        for cliente in self.clientes:
            if cliente != cliente_socket:   #Provando
                try:
                    cliente.send(datos.encode())
                except Exception as e:
                    print(f"Error al enviar actualización a cliente: {e}")
                    cliente.close()
                    self.clientes.remove(cliente)

    def run(self):
        self.clientes = []
        thread_aceptar_conexiones = threading.Thread(target=self.aceptar_conexiones)
        thread_aceptar_conexiones.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeApp()
    sys.exit(app.exec_())