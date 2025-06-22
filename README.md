<h1 align="center">Sistema VAR para RoboFut</h1>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python">
  <img src="https://img.shields.io/badge/OpenCV-enabled-green?logo=opencv">
  <img src="https://img.shields.io/badge/CustomTkinter-GUI-blueviolet">
  <img src="https://img.shields.io/badge/pygame-enabled-brightgreen?style=flat-square">

</p>

---

## ¿En que consiste el proyecto?

Es un **sistema de videoarbitraje automatizado** (VAR) desarrollado en Python para **RoboFut**, un torneo de futbol de robots a control remoto. Fue creado para el Encuentro Nacional de Robótica **BALAM** 🇬🇹.

> ⚠️ Todo el proyecto es **open source**, con el objetivo de apoyar la robótica educativa y fomentar el aprendizaje de visión por computadora.

---

## Funcionalidades destacadas

| Característica | Descripción |
|----------------|-------------|
| RTSP Streaming | Se usaron cámaras IP, modelo TAPO C200 |
| Aplanado de campo | Selección de esquinas + `cv2.getPerspectiveTransform` |
| Detección de pelota | HSV + morfología + circularity + Filtro de Kalman  |
| Gol automático | Detecta cruce de línea definida como portería |
| Grabación automatica | Guarda 10s antes y 3s después del gol |
| GUI Interactiva | CustomTkinter para configuración y visualización |
| Librería de Repeticiones | Miniaturas + reproductor integrado con control de velocidad |

---

## Vista general del sistema

![Image](https://github.com/user-attachments/assets/225c65f5-d5f8-45ac-a2b5-f2a77543f8ba)

![Image](https://github.com/user-attachments/assets/bd4e24a1-ef8c-46d8-a8d0-d5a18fbb3df9)

![Image](https://github.com/user-attachments/assets/be93450e-ef38-4c85-8a28-2fa92ef9f96b)

![Image](https://github.com/user-attachments/assets/590cc546-e505-47cc-b7f7-5aa4b74929fe)

![Image](https://github.com/user-attachments/assets/b27297fb-b363-437e-a147-4c916e009d0b)

![Image](https://github.com/user-attachments/assets/9b55d269-9c47-4312-b132-66a86fe4087b)
