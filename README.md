## Simulación del Llenado de un Tronco de Cono

Este proyecto implementa una **visualización interactiva en 3D** del proceso de llenado de un depósito con forma de **tronco de cono**, utilizando **PyQt5** y **Matplotlib**. El propósito principal es mostrar cómo varía la **altura del agua** a medida que se llena el recipiente con una **tasa de flujo constante**.

## Descripción
El programa permite que el usuario:
- Ingrese parámetros personalizados del depósito: altura, radio inferior, radio superior y flujo de llenado.
- Visualice en tiempo real el nivel del agua dentro del depósito.
- Controle la simulación con botones para **iniciar**, **detener** y **reiniciar parámetros**.

Este proyecto forma parte de un proyecto relacionado con la aplicación de las **derivadas** para estudiar razones de cambio.

## Funcionalidades

- Interfaz gráfica intuitiva con PyQt5.
- Entrada dinámica de parámetros: altura, radios y tasa de llenado.
- Visualización en 3D del tronco de cono y el nivel de agua en tiempo real.
- Botones de control:
  - Iniciar Simulación
  - Detener Simulación
  - Reiniciar Parámetros
- Cálculo e interpolación automática de la altura del agua con base en el volumen acumulado.

## Requisitos
Instalar las dependencias con:
```bash
pip install pyqt5 matplotlib numpy
