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
class ConoWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación del Llenado de un Tronco de Cono")
        self.setGeometry(200, 100, 1100, 750)

        # Valores iniciales
        self.altura_total = 2
        self.radio_base = 6
        self.radio_superior = 4
        self.flujo = 0.1
        self.vol_actual = 0

        self.initUI()

    def initUI(self):
        # Caja de parámetros de entrada
        parametros_box = QGroupBox("Parámetros de la Simulación")
        parametros_box.setFont(QFont("Arial", 10, QFont.Bold))

        # Campos de entrada
        self.input_altura = QLineEdit("2")
        self.input_r_base = QLineEdit("6")
        self.input_r_top = QLineEdit("4")
        self.input_flujo = QLineEdit("0.1")

        for campo in [self.input_altura, self.input_r_base, self.input_r_top, self.input_flujo]:
            campo.setFixedWidth(100)
            campo.setAlignment(Qt.AlignRight)
            campo.setFont(QFont("Arial", 10))

        # Formulario de entrada
        form_inner_layout = QFormLayout()
        form_inner_layout.setLabelAlignment(Qt.AlignRight)
        form_inner_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_inner_layout.addRow("Altura total (m):", self.input_altura)
        form_inner_layout.addRow("Radio inferior (m):", self.input_r_base)
        form_inner_layout.addRow("Radio superior (m):", self.input_r_top)
        form_inner_layout.addRow("Tasa de llenado (m³/s):", self.input_flujo)

        form_container = QWidget()
        form_container.setLayout(form_inner_layout)

        # Botón para iniciar
        self.boton = QPushButton("▶ Iniciar Simulación")
        self.boton.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px 12px;")
        self.boton.clicked.connect(self.iniciar_simulacion)

        # Botón para detener
        self.boton_detener = QPushButton("⏸ Detener Simulación")
        self.boton_detener.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton_detener.setStyleSheet("background-color: #f44336; color: white; padding: 6px 12px;")
        self.boton_detener.clicked.connect(self.detener_simulacion)

        # Botón para reiniciar
        self.boton_reiniciar = QPushButton("🔄 Reiniciar Parámetros")
        self.boton_reiniciar.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton_reiniciar.setStyleSheet("background-color: #2196F3; color: white; padding: 6px 12px;")
        self.boton_reiniciar.clicked.connect(self.reiniciar_parametros)

        # Agrupación de botones
        boton_layout = QHBoxLayout()
        boton_layout.addStretch()
        boton_layout.addWidget(self.boton)
        boton_layout.addWidget(self.boton_detener)
        boton_layout.addWidget(self.boton_reiniciar)
        boton_layout.addStretch()

        # Composición vertical
        vbox_form = QVBoxLayout()
        vbox_form.setAlignment(Qt.AlignCenter)
        vbox_form.addWidget(form_container)
        vbox_form.addSpacing(10)
        vbox_form.addLayout(boton_layout)

        parametros_box.setLayout(vbox_form)

        # Canvas para el gráfico 3D
        self.canvas = FigureCanvas(Figure(figsize=(6, 6)))
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')

        # Layout horizontal principal
        hbox = QHBoxLayout()
        hbox.addWidget(parametros_box)
        hbox.addWidget(self.canvas)

        contenedor = QWidget()
        contenedor.setLayout(hbox)
        self.setCentralWidget(contenedor)

    def iniciar_simulacion(self):
        try:
            self.altura_total = float(self.input_altura.text())
            self.radio_base = float(self.input_r_base.text())
            self.radio_superior = float(self.input_r_top.text())
            self.flujo = float(self.input_flujo.text())
            self.vol_actual = 0
        except ValueError:
            QMessageBox.warning(self, "Error", "Todos los campos deben ser numéricos.")
            return

        # Tabla volumen-altura
        self.vol_lookup = []
        alturas = np.linspace(0, self.altura_total, 1000)
        for h in alturas:
            r = self.radio_en_h(h)
            v = (1/3) * np.pi * h * (self.radio_base**2 + self.radio_base*r + r**2)
            self.vol_lookup.append((v, h))

        # Iniciar animación
        self.ani = FuncAnimation(self.canvas.figure, self.actualizar, interval=100)
        self.canvas.draw()

    def detener_simulacion(self):
        if hasattr(self, 'ani'):
            self.ani.event_source.stop()

    def reiniciar_parametros(self):
        self.input_altura.setText("2")
        self.input_r_base.setText("6")
        self.input_r_top.setText("4")
        self.input_flujo.setText("0.1")
        self.vol_actual = 0
        self.canvas.figure.clf()
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        self.canvas.draw()

    def radio_en_h(self, h):
        return self.radio_base - ((self.radio_base - self.radio_superior) / self.altura_total) * h

    def altura_por_volumen(self, v_actual):
        vols, hs = zip(*self.vol_lookup)
        return np.interp(v_actual, vols, hs)

    def get_cono(self, h):
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(0, h, 30)
        theta_grid, z_grid = np.meshgrid(theta, z)
        r_grid = self.radio_base - ((self.radio_base - self.radio_superior) / self.altura_total) * z_grid
        x = r_grid * np.cos(theta_grid)
        y = r_grid * np.sin(theta_grid)
        return x, y, z_grid

    def actualizar(self, frame):
        self.ax.clear()
        self.ax.set_xlim([-self.radio_base, self.radio_base])
        self.ax.set_ylim([-self.radio_base, self.radio_base])
        self.ax.set_zlim([0, self.altura_total])

        self.vol_actual += self.flujo * 0.1
        h = self.altura_por_volumen(self.vol_actual)
        self.ax.set_title(f"Altura del agua: {h:.2f} m", fontsize=10)

        x_cono, y_cono, z_cono = self.get_cono(self.altura_total)
        self.ax.plot_surface(x_cono, y_cono, z_cono, color='lightgray', alpha=0.2)

        x_agua, y_agua, z_agua = self.get_cono(h)
        self.ax.plot_surface(x_agua, y_agua, z_agua, color='blue', alpha=0.6)

# Ejecutar aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = ConoWindow()
    ventana.show()
    sys.exit(app.exec_())
