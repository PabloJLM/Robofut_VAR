<h1 align="center">Sistema VAR para RoboFut</h1>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python">
  <img src="https://img.shields.io/badge/OpenCV-enabled-green?logo=opencv">
  <img src="https://img.shields.io/badge/CustomTkinter-GUI-blueviolet">
  <img src="https://img.shields.io/badge/pygame-enabled-brightgreen?style=flat-square">

</p>

## Demostracion
![Image](https://github.com/user-attachments/assets/9b55d269-9c47-4312-b132-66a86fe4087b) <!-- GIF funcionamiento-->

---

## ¿En que consiste el proyecto?

Es un **sistema de videoarbitraje automatizado** (VAR) desarrollado en Python para **RoboFut**, un torneo de futbol de robots a control remoto. Fue creado para el Encuentro Nacional de Robótica **BALAM** 🇬🇹.

> ⚠️ Todo el proyecto es **open source**, con el objetivo de apoyar la robótica educativa y fomentar el aprendizaje de visión por computadora.

---
![Image](https://github.com/user-attachments/assets/b27297fb-b363-437e-a147-4c916e009d0b) <!-- logo -->

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
## Pipeline del sistema
```text
[Cámara RTSP]
          ↓
[Selección de Esquinas]
          ↓
[Transformación de Perspectiva]
          ↓
[Tracking de Pelota (HSV + filtros)]
          ↓
[Kalman Filter + Estela]
          ↓
[Verificación de GOL (cruce de línea)]
          ↓
[Reproducción de sonido + grabación del gol]
          ↓
[GUI + Reproductor de videos]
```


## Pantalla principal

![Image](https://github.com/user-attachments/assets/225c65f5-d5f8-45ac-a2b5-f2a77543f8ba) <!-- Pantalla principal-->

## Vista con filtros y vista general 
![Image](https://github.com/user-attachments/assets/bd4e24a1-ef8c-46d8-a8d0-d5a18fbb3df9) <!-- ventana con mascaras de color y ventana con todo añadido-->

## Ventana del VAR
![Image](https://github.com/user-attachments/assets/be93450e-ef38-4c85-8a28-2fa92ef9f96b) <!-- VAR -->

## Ventana de seleccion del campo
![Image](https://github.com/user-attachments/assets/590cc546-e505-47cc-b7f7-5aa4b74929fe) <!-- Seleccion del campo-->

## Ventana de grabaciones
![Image](https://github.com/user-attachments/assets/6fdb605c-1040-40e0-b903-b19aafb61a49) <!-- ventana de grabaciones -->

## Reproduccion del VAR
![Image](https://github.com/user-attachments/assets/11bb0025-9e61-496c-8501-12283f4b3120)<!-- ventana de grabaciones reproduccion -->

## Cómo ejecutar

1. Clona el repositorio:
   ```bash
   git clone https://github.com/PabloJLM/Robofut_VAR.git
   cd Robofut_VAR
   
2. Instalar los paquetes:
   ```bash
   pip install -r paquetes.txt
   
3. Prueba la conexion a la camara con pruebas_camIP.py usando:
   ```bash
   python pruebas_camIP.py
   
4. Ejecuta el programa principal
   ```bash
   python main.py
