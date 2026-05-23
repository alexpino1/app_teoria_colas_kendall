# Calculadora de Teoría de Colas (Notación de Kendall)

Una aplicación de escritorio premium e interactiva escrita en **Python y Tkinter** para calcular, comparar y graficar de forma sencilla los modelos de la Teoría de Colas más utilizados en ingeniería, investigación de operaciones y planificación de capacidad.

<p align="center">
  <img src="calculo_png.png" alt="Vista previa de la calculadora" width="100">
</p>

---

## Inicio Rápido (En 3 pasos)

Sigue estos sencillos pasos para configurar y correr la aplicación en tu entorno local:

### 1. Clonar y preparar el entorno virtual
Asegúrate de estar en el directorio del proyecto y crea un entorno virtual aislado:
```bash
python -m venv .venv
```

### 2. Instalar dependencias necesarias
Instala las librerías requeridas para habilitar la visualización de gráficos dinámicos:
```bash
.venv\Scripts\python -m pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
Ejecuta el script principal usando el intérprete del entorno virtual:
```bash
.venv\Scripts\python teoria_colas_kendall.py
```

---

## Modelos de Kendall Soportados

La aplicación cuenta con un potente motor matemático de cálculo para los siguientes modelos estándar:

| Modelo (Kendall) | Descripción | Parámetros Requeridos |
| :--- | :--- | :--- |
| **M/M/1** | Un solo servidor, llegadas/servicios exponenciales, capacidad infinita. | $\lambda$ (llegada), $\mu$ (servicio) |
| **M/M/c** | Múltiples servidores en paralelo. Cálculo con fórmula de Erlang-C. | $\lambda$, $\mu$, $c$ (servidores) |
| **M/M/1/K** | Un servidor con capacidad máxima limitada (pérdidas por bloqueo). | $\lambda$, $\mu$, $K$ (capacidad) |
| **M/M/c/K** | Múltiples servidores con capacidad total finita $K$. | $\lambda$, $\mu$, $c$, $K$ |
| **M/M/1/K/K** | Modelo cerrado con población y fuente finita (ej. máquinas en reparación). | $\lambda$ (indiv.), $\mu$, $K$ (población) |
| **M/D/1** | Un servidor con tiempos de servicio determinísticos (tiempo fijo). | $\lambda$, $\mu$ |
| **M/G/1** | Un servidor con tiempos de servicio generales (Pollaczek-Khinchine). | $\lambda$, $\mu$, $CV$ (coeficiente de variación) |
| **M/Ek/1** | Un servidor con servicio de etapas Erlang-$k$. | $\lambda$, $\mu$, $k$ (etapas) |
| **M/M/∞** | Servidores infinitos (modelo de autoservicio o sin bloqueo). | $\lambda$, $\mu$ |

---

## Características Destacadas

*   **Diseño Oscuro Premium (Aesthetics-First):** Interfaz moderna inspirada en temas modernos de Github, utilizando una combinación curada de grises oscuros, acentos verdes, azules y cianes que evitan la fatiga visual.
*   **Métricas de Rendimiento Clave en Tiempo Real:** Visualización instantánea de:
    *   $\rho$ (Factor de utilización del sistema)
    *   $P_0$ (Probabilidad de sistema vacío)
    *   $L$ y $L_q$ (Clientes promedio en el sistema y en la cola)
    *   $W$ y $W_q$ (Tiempo promedio de estancia en el sistema y de espera en la cola)
    *   $\lambda_{ef}$ (Tasa efectiva de llegada para sistemas finitos)
*   **Gráficos Interactivos de Distribución:** Pestaña con histograma interactivo que muestra las probabilidades individuales de estado estable $P(n)$ y acumulativas para los primeros 20 clientes utilizando `matplotlib`.
*   **Tabla de Comparativa Integrada:** Guarda el historial de tus cálculos recientes en una tabla para comparar el rendimiento de diferentes configuraciones y modelos cara a cara de forma inmediata.
*   **Resiliencia Extensible:** La aplicación detecta automáticamente si `matplotlib` o `numpy` están instalados. Si no lo están, continúa funcionando perfectamente con fallbacks textuales de las probabilidades.

---

## Requisitos Técnicos

*   **Python 3.8+**
*   Bibliotecas estándar de Python (`tkinter`, `math`, `threading`).
*   **Dependencias Externas:**
    *   `matplotlib` (para renderizar los gráficos interactivos de barras)
    *   `numpy` (para los cálculos vectoriales de distribución)

---

## Licencia

Este proyecto está bajo la Licencia MIT. Siéntete libre de clonarlo, mejorarlo y adaptarlo a tus necesidades académicas o profesionales.
