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

class VentanaCono(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulación del Llenado de un Tronco de Cono")
        self.setGeometry(200, 100, 1150, 750)
        self.setStyleSheet("background-color: #f5f7fa;")  # Fondo muy claro y suave

        # Parámetros iniciales
        self.altura_total = 2
        self.radio_inferior = 6
        self.radio_superior = 4
        self.tasa_llenado = 0.1
        self.volumen_actual = 0

        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        # Fuente moderna
        fuente_titulo = QFont("Segoe UI", 11, QFont.Bold)
        fuente_label = QFont("Segoe UI", 10)
        fuente_input = QFont("Segoe UI", 10)
        fuente_boton = QFont("Segoe UI", 10, QFont.Bold)

        # Sección parámetros
        caja_parametros = QGroupBox("Parámetros de la Simulación")
        caja_parametros.setFont(fuente_titulo)
        caja_parametros.setStyleSheet("""
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 12px;
                background-color: white;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 3px 0 3px;
                color: #2c3e50;
            }
        """)

        # Entradas
        self.entrada_altura = QLineEdit("7")
        self.entrada_radio_inferior = QLineEdit("6")
        self.entrada_radio_superior = QLineEdit("4")
        self.entrada_tasa = QLineEdit("0.1")

        for campo in [self.entrada_altura, self.entrada_radio_inferior, self.entrada_radio_superior, self.entrada_tasa]:
            campo.setFixedWidth(130)
            campo.setAlignment(Qt.AlignRight)
            campo.setFont(fuente_input)
            campo.setStyleSheet("""
                QLineEdit {
                    border: 1.5px solid #bdc3c7;
                    border-radius: 6px;
                    padding: 4px 8px;
                    background-color: #ecf0f1;
                    color: #34495e;
                }
                QLineEdit:focus {
                    border-color: #2980b9;
                    background-color: #ffffff;
                }
            """)

        formulario = QFormLayout()
        formulario.setLabelAlignment(Qt.AlignRight)
        formulario.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        formulario.setHorizontalSpacing(20)
        formulario.setVerticalSpacing(15)
        formulario.addRow("Altura total (m):", self.entrada_altura)
        formulario.addRow("Radio inferior (m):", self.entrada_radio_inferior)
        formulario.addRow("Radio superior (m):", self.entrada_radio_superior)
        formulario.addRow("Tasa de llenado (m³/s):", self.entrada_tasa)

        contenedor_formulario = QWidget()
        contenedor_formulario.setLayout(formulario)

        # Botones con estilo moderno y efecto hover
        self.boton_iniciar = QPushButton("▶ Iniciar Simulación")
        self.boton_detener = QPushButton("⏸ Detener Simulación")
        self.boton_reiniciar = QPushButton("🔄 Reiniciar Parámetros")

        for boton, color_base in [
            (self.boton_iniciar, "#27ae60"),
            (self.boton_detener, "#c0392b"),
            (self.boton_reiniciar, "#2980b9"),
        ]:
            boton.setFont(fuente_boton)
            boton.setCursor(Qt.PointingHandCursor)
            boton.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_base};
                    color: white;
                    border-radius: 8px;
                    padding: 8px 18px;
                    border: none;
                    transition: background-color 0.3s ease;
                }}
                QPushButton:hover {{
                    background-color: #1c5980;
                }}
                QPushButton:pressed {{
                    background-color: #145374;
                }}
            """)

        self.boton_iniciar.clicked.connect(self.iniciar_simulacion)
        self.boton_detener.clicked.connect(self.detener_simulacion)
        self.boton_reiniciar.clicked.connect(self.reiniciar_parametros)

        layout_botones = QHBoxLayout()
        layout_botones.setSpacing(15)
        layout_botones.addStretch()
        layout_botones.addWidget(self.boton_iniciar)
        layout_botones.addWidget(self.boton_detener)
        layout_botones.addWidget(self.boton_reiniciar)
        layout_botones.addStretch()

        layout_vertical = QVBoxLayout()
        layout_vertical.setContentsMargins(20, 15, 20, 20)
        layout_vertical.setSpacing(20)
        layout_vertical.setAlignment(Qt.AlignTop)
        layout_vertical.addWidget(contenedor_formulario)
        layout_vertical.addLayout(layout_botones)

        caja_parametros.setLayout(layout_vertical)

        # Canvas para gráfico 3D con borde y sombra sutil
        self.canvas = FigureCanvas(Figure(figsize=(6, 6)))
        self.canvas.setStyleSheet("""
            border: 1.5px solid #bdc3c7;
            border-radius: 10px;
            background-color: white;
        """)
        self.ejes = self.canvas.figure.add_subplot(111, projection='3d')

        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(30)
        layout_principal.addWidget(caja_parametros, stretch=0)
        layout_principal.addWidget(self.canvas, stretch=1)

        contenedor = QWidget()
        contenedor.setLayout(layout_principal)
        self.setCentralWidget(contenedor)

    # Resto del código (sin cambios)
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

        self.tabla_volumen_altura = []
        alturas = np.linspace(0, self.altura_total, 1000)
        for h in alturas:
            r = self.radio_a_altura(h)
            v = (1/3) * np.pi * h * (self.radio_inferior**2 + self.radio_inferior*r + r**2)
            self.tabla_volumen_altura.append((v, h))

        self.animacion = FuncAnimation(self.canvas.figure, self.actualizar_grafico, interval=100)
        self.canvas.draw()

        h_eval = 1.5
        r_h = self.radio_a_altura(h_eval)
        dV_dh = (np.pi / 3) * (self.radio_inferior**2 + self.radio_inferior * r_h + r_h**2
                               + h_eval * (-2/7) * (self.radio_inferior + r_h))

        dh_dt = self.tasa_llenado / dV_dh

        QMessageBox.information(
            self,
            "Resultado",
            f"Para h = {h_eval} m, la velocidad de subida es aproximadamente:\n"
            f"dh/dt ≈ {dh_dt:.6f} m/s"
        )

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
        self.ejes.set_title(f"Altura del agua: {altura_actual:.2f} m", fontsize=12, color="#34495e")

        x_cono, y_cono, z_cono = self.obtener_cono(self.altura_total)
        self.ejes.plot_surface(x_cono, y_cono, z_cono, color='#bdc3c7', alpha=0.25)

        x_agua, y_agua, z_agua = self.obtener_cono(altura_actual)
        self.ejes.plot_surface(x_agua, y_agua, z_agua, color='#2980b9', alpha=0.7)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaCono()
    ventana.show()
    sys.exit(app.exec_())
