# Importación de librerías necesarias
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFormLayout, QLineEdit, QMessageBox, QGroupBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

# Clase principal de la interfaz gráfica
class VentanaCono(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación del Llenado de un Tronco de Cono")
        self.setGeometry(200, 100, 1100, 750)

        # Parámetros iniciales
        self.altura_total = 2
        self.radio_inferior = 6
        self.radio_superior = 4
        self.tasa_llenado = 0.1
        self.volumen_actual = 0

        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        # Sección de parámetros
        caja_parametros = QGroupBox("Parámetros de la Simulación")
        caja_parametros.setFont(QFont("Arial", 10, QFont.Bold))

        # Entradas de usuario
        self.entrada_altura = QLineEdit("7")
        self.entrada_radio_inferior = QLineEdit("6")
        self.entrada_radio_superior = QLineEdit("4")
        self.entrada_tasa = QLineEdit("0.1")

        for campo in [self.entrada_altura, self.entrada_radio_inferior, self.entrada_radio_superior, self.entrada_tasa]:
            campo.setFixedWidth(100)
            campo.setAlignment(Qt.AlignRight)
            campo.setFont(QFont("Arial", 10))

        formulario = QFormLayout()
        formulario.setLabelAlignment(Qt.AlignRight)
        formulario.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        formulario.addRow("Altura total (m):", self.entrada_altura)
        formulario.addRow("Radio inferior (m):", self.entrada_radio_inferior)
        formulario.addRow("Radio superior (m):", self.entrada_radio_superior)
        formulario.addRow("Tasa de llenado (m³/s):", self.entrada_tasa)

        contenedor_formulario = QWidget()
        contenedor_formulario.setLayout(formulario)

        # Botones
        self.boton_iniciar = QPushButton("▶ Iniciar Simulación")
        self.boton_iniciar.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton_iniciar.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px 12px;")
        self.boton_iniciar.clicked.connect(self.iniciar_simulacion)

        self.boton_detener = QPushButton("⏸ Detener Simulación")
        self.boton_detener.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton_detener.setStyleSheet("background-color: #f44336; color: white; padding: 6px 12px;")
        self.boton_detener.clicked.connect(self.detener_simulacion)

        self.boton_reiniciar = QPushButton("🔄 Reiniciar Parámetros")
        self.boton_reiniciar.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton_reiniciar.setStyleSheet("background-color: #2196F3; color: white; padding: 6px 12px;")
        self.boton_reiniciar.clicked.connect(self.reiniciar_parametros)

        layout_botones = QHBoxLayout()
        layout_botones.addStretch()
        layout_botones.addWidget(self.boton_iniciar)
        layout_botones.addWidget(self.boton_detener)
        layout_botones.addWidget(self.boton_reiniciar)
        layout_botones.addStretch()

        layout_vertical = QVBoxLayout()
        layout_vertical.setAlignment(Qt.AlignCenter)
        layout_vertical.addWidget(contenedor_formulario)
        layout_vertical.addSpacing(10)
        layout_vertical.addLayout(layout_botones)

        caja_parametros.setLayout(layout_vertical)

        # Canvas 3D para el gráfico
        self.canvas = FigureCanvas(Figure(figsize=(6, 6)))
        self.ejes = self.canvas.figure.add_subplot(111, projection='3d')

        layout_principal = QHBoxLayout()
        layout_principal.addWidget(caja_parametros)
        layout_principal.addWidget(self.canvas)

        contenedor = QWidget()
        contenedor.setLayout(layout_principal)
        self.setCentralWidget(contenedor)

    def iniciar_simulacion(self):
        try:
            self.altura_total = float(self.entrada_altura.text())
            self.radio_inferior = float(self.entrada_radio_inferior.text())
            self.radio_superior = float(self.entrada_radio_superior.text())
            self.tasa_llenado = float(self.entrada_tasa.text())
            self.volumen_actual = 0
        except ValueError:
            QMessageBox.warning(self, "Error", "Todos los campos deben ser numéricos.")
            return

        # Tabla de volumen vs altura
        self.tabla_volumen_altura = []
        alturas = np.linspace(0, self.altura_total, 1000)
        for h in alturas:
            r = self.radio_a_altura(h)
            v = (1/3) * np.pi * h * (self.radio_inferior**2 + self.radio_inferior*r + r**2)
            self.tabla_volumen_altura.append((v, h))

        self.animacion = FuncAnimation(self.canvas.figure, self.actualizar_grafico, interval=100)
        self.canvas.draw()

    def detener_simulacion(self):
        if hasattr(self, 'animacion'):
            self.animacion.event_source.stop()

    def reiniciar_parametros(self):
        self.entrada_altura.setText("2")
        self.entrada_radio_inferior.setText("6")
        self.entrada_radio_superior.setText("4")
        self.entrada_tasa.setText("0.1")
        self.volumen_actual = 0
        self.canvas.figure.clf()
        self.ejes = self.canvas.figure.add_subplot(111, projection='3d')
        self.canvas.draw()

    def radio_a_altura(self, altura):
        return self.radio_inferior - ((self.radio_inferior - self.radio_superior) / self.altura_total) * altura

    def altura_por_volumen(self, volumen):
        volúmenes, alturas = zip(*self.tabla_volumen_altura)
        return np.interp(volumen, volúmenes, alturas)

    def obtener_cono(self, altura):
        angulo = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(0, altura, 30)
        angulo_grid, z_grid = np.meshgrid(angulo, z)
        radio_grid = self.radio_inferior - ((self.radio_inferior - self.radio_superior) / self.altura_total) * z_grid
        x = radio_grid * np.cos(angulo_grid)
        y = radio_grid * np.sin(angulo_grid)
        return x, y, z_grid

    def actualizar_grafico(self, frame):
        self.ejes.clear()
        self.ejes.set_xlim([-self.radio_inferior, self.radio_inferior])
        self.ejes.set_ylim([-self.radio_inferior, self.radio_inferior])
        self.ejes.set_zlim([0, self.altura_total])

        self.volumen_actual += self.tasa_llenado * 0.1
        altura_actual = self.altura_por_volumen(self.volumen_actual)
        self.ejes.set_title(f"Altura del agua: {altura_actual:.2f} m", fontsize=10)

        x_cono, y_cono, z_cono = self.obtener_cono(self.altura_total)
        self.ejes.plot_surface(x_cono, y_cono, z_cono, color='lightgray', alpha=0.2)

        x_agua, y_agua, z_agua = self.obtener_cono(altura_actual)
        self.ejes.plot_surface(x_agua, y_agua, z_agua, color='blue', alpha=0.6)

# Ejecutar aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaCono()
    ventana.show()
    sys.exit(app.exec_())
