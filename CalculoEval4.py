# Importación de librerías necesarias
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFormLayout, QLineEdit, QMessageBox, QLabel, QGroupBox, QHBoxLayout
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
        # Título y dimensiones de la ventana
        self.setWindowTitle("Simulación del Llenado de un Tronco de Cono")
        self.setGeometry(200, 100, 1100, 750)

        # Parámetros iniciales por defecto
        self.altura_total = 2           # Altura total del depósito
        self.radio_base = 6             # Radio de la base inferior
        self.radio_superior = 4         # Radio de la parte superior
        self.flujo = 0.1                # Flujo constante en m³/s
        self.vol_actual = 0             # Volumen acumulado de agua

        # Inicializa la interfaz
        self.initUI()

    def initUI(self):
        # ---------- Panel de Parámetros (lado izquierdo) ----------
        parametros_box = QGroupBox("Parámetros de la Simulación")
        parametros_box.setFont(QFont("Arial", 10, QFont.Bold))

        # Campos de entrada con valores por defecto
        self.input_altura = QLineEdit("2")
        self.input_r_base = QLineEdit("6")
        self.input_r_top = QLineEdit("4")
        self.input_flujo = QLineEdit("0.1")

        # Formato visual de los campos
        for campo in [self.input_altura, self.input_r_base, self.input_r_top, self.input_flujo]:
            campo.setFixedWidth(100)
            campo.setAlignment(Qt.AlignRight)
            campo.setFont(QFont("Arial", 10))

        # Layout del formulario (etiquetas + campos)
        form_layout = QFormLayout()
        form_layout.addRow("Altura total (m):", self.input_altura)
        form_layout.addRow("Radio inferior (m):", self.input_r_base)
        form_layout.addRow("Radio superior (m):", self.input_r_top)
        form_layout.addRow("Tasa de llenado (m³/s):", self.input_flujo)

        # Botón para iniciar la simulación
        self.boton = QPushButton("▶ Iniciar Simulación")
        self.boton.setFont(QFont("Arial", 10, QFont.Bold))
        self.boton.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px 12px;")
        self.boton.clicked.connect(self.iniciar_simulacion)

        # Contenedor visual para centrar los campos
        form_container = QWidget()
        form_inner_layout = QFormLayout()
        form_inner_layout.setLabelAlignment(Qt.AlignRight)
        form_inner_layout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        form_inner_layout.addRow("Altura total (m):", self.input_altura)
        form_inner_layout.addRow("Radio inferior (m):", self.input_r_base)
        form_inner_layout.addRow("Radio superior (m):", self.input_r_top)
        form_inner_layout.addRow("Tasa de llenado (m³/s):", self.input_flujo)
        form_container.setLayout(form_inner_layout)

        # Layout para centrar el botón
        boton_layout = QHBoxLayout()
        boton_layout.addStretch()
        boton_layout.addWidget(self.boton)
        boton_layout.addStretch()

        # Agrupación del formulario y botón
        vbox_form = QVBoxLayout()
        vbox_form.setAlignment(Qt.AlignCenter)
        vbox_form.addWidget(form_container)
        vbox_form.addSpacing(10)
        vbox_form.addLayout(boton_layout)

        parametros_box.setLayout(vbox_form)

        # ---------- Canvas de Matplotlib para gráfico 3D (lado derecho) ----------
        self.canvas = FigureCanvas(Figure(figsize=(6, 6)))
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')

        # ---------- Composición horizontal: parámetros + gráfico ----------
        hbox = QHBoxLayout()
        hbox.addWidget(parametros_box)
        hbox.addWidget(self.canvas)

        # Definición del contenedor general
        contenedor = QWidget()
        contenedor.setLayout(hbox)
        self.setCentralWidget(contenedor)

    # Función que se ejecuta al presionar el botón de simulación
    def iniciar_simulacion(self):
        try:
            # Obtener los valores numéricos desde los campos de texto
            self.altura_total = float(self.input_altura.text())
            self.radio_base = float(self.input_r_base.text())
            self.radio_superior = float(self.input_r_top.text())
            self.flujo = float(self.input_flujo.text())
            self.vol_actual = 0  # Reiniciar volumen
        except ValueError:
            # Si hay valores no numéricos, se muestra un mensaje de error
            QMessageBox.warning(self, "Error", "Todos los campos deben ser numéricos.")
            return

        # Se calcula una tabla de valores (volumen-altura) precalculada
        self.vol_lookup = []
        alturas = np.linspace(0, self.altura_total, 1000)  # Alturas desde 0 hasta la altura total

        # Para cada altura, se calcula el volumen correspondiente usando fórmula del tronco de cono
        for h in alturas:
            r = self.radio_en_h(h)
            v = (1/3) * np.pi * h * (self.radio_base**2 + self.radio_base*r + r**2)
            self.vol_lookup.append((v, h))  # Se guarda la tupla (volumen, altura)

        # Se inicia la animación del gráfico
        self.ani = FuncAnimation(self.canvas.figure, self.actualizar, interval=100)
        self.canvas.draw()

    # Función que devuelve el radio del nivel del agua en una altura dada
    def radio_en_h(self, h):
        # Relación lineal entre el radio y la altura (por semejanza de triángulos)
        return self.radio_base - ((self.radio_base - self.radio_superior) / self.altura_total) * h

    # Función que busca la altura correspondiente a un volumen actual usando interpolación
    def altura_por_volumen(self, v_actual):
        vols, hs = zip(*self.vol_lookup)
        return np.interp(v_actual, vols, hs)

    # Función que genera los datos (x, y, z) del tronco de cono para una altura dada
    def get_cono(self, h):
        theta = np.linspace(0, 2*np.pi, 30)
        z = np.linspace(0, h, 30)
        theta_grid, z_grid = np.meshgrid(theta, z)

        # Calcula el radio correspondiente en cada punto z
        r_grid = self.radio_base - ((self.radio_base - self.radio_superior) / self.altura_total) * z_grid
        x = r_grid * np.cos(theta_grid)
        y = r_grid * np.sin(theta_grid)
        return x, y, z_grid

    # Función que actualiza el gráfico en cada "frame" de la animación
    def actualizar(self, frame):
        self.ax.clear()  # Limpia el gráfico anterior

        # Se establecen los límites del gráfico 3D
        self.ax.set_xlim([-self.radio_base, self.radio_base])
        self.ax.set_ylim([-self.radio_base, self.radio_base])
        self.ax.set_zlim([0, self.altura_total])

        # Se incrementa el volumen actual según el flujo y el tiempo (0.1s por frame)
        self.vol_actual += self.flujo * 0.1

        # Se calcula la nueva altura alcanzada por ese volumen
        h = self.altura_por_volumen(self.vol_actual)

        # Título del gráfico con la altura actual del agua
        self.ax.set_title(f"Altura del agua: {h:.2f} m", fontsize=10)

        # Dibuja el contorno total del depósito
        x_cono, y_cono, z_cono = self.get_cono(self.altura_total)
        self.ax.plot_surface(x_cono, y_cono, z_cono, color='lightgray', alpha=0.2)

        # Dibuja el volumen del agua hasta la altura calculada
        x_agua, y_agua, z_agua = self.get_cono(h)
        self.ax.plot_surface(x_agua, y_agua, z_agua, color='blue', alpha=0.6)

# Punto de entrada principal de la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)     # Crea una instancia de la aplicación
    ventana = ConoWindow()           # Crea la ventana principal
    ventana.show()                   # Muestra la ventana
    sys.exit(app.exec_())            # Ejecuta la aplicación y espera su cierre
