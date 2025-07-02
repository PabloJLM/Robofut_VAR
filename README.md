<h1 align="center">Sistema VAR para RoboFut</h1>
<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python">
  <img src="https://img.shields.io/badge/OpenCV-enabled-green?logo=opencv">
  <img src="https://img.shields.io/badge/CustomTkinter-GUI-blueviolet">
  <img src="https://img.shields.io/badge/pygame-enabled-brightgreen?style=flat-square">

</p>

## Demostración
![Image](https://github.com/user-attachments/assets/9b55d269-9c47-4312-b132-66a86fe4087b) <!-- GIF funcionamiento-->

---

## ¿En qué consiste el proyecto?

Es un **sistema de videoarbitraje automatizado** (VAR) desarrollado en Python para **RoboFut**, un torneo de fútbol de robots a control remoto. Fue creado para el Encuentro Nacional de Robótica **BALAM** 🇬🇹.
![Image](https://github.com/user-attachments/assets/b27297fb-b363-437e-a147-4c916e009d0b) <!-- logo -->

> ⚠️ Todo el proyecto es **open source**, con el objetivo de apoyar la robótica educativa y fomentar el aprendizaje de visión por computadora.

---


## Funcionalidades destacadas

| Característica         | Descripción                                                |
|------------------------|------------------------------------------------------------|
| RTSP Streaming         | Se usaron cámaras IP, modelo TAPO C200                     |
| Aplanado de campo      | Selección de esquinas + `cv2.getPerspectiveTransform`      |
| Detección de pelota    | HSV + morfología + circularidad + Filtro de Kalman         |
| Gol automático         | Detecta cruce de línea definida como portería              |
| Grabación automática   | Guarda 10 s antes y 3 s después del gol                    |
| GUI interactiva        | CustomTkinter para configuración y visualización           |
| Librería de repeticiones | Miniaturas + reproductor integrado con control de velocidad |

---
## Pipeline del sistema
```text
[Cámara RTSP]
          ↓
[Selección de esquinas]
          ↓
[Selección de porterías]
          ↓
[Transformación de perspectiva]
          ↓
[Tracking de pelota (HSV + filtros)]
          ↓
[Kalman Filter + estela]
          ↓
[Verificación de GOL (cruce de línea)]
          ↓
[Reproducción de sonido + grabación del gol]
          ↓
[GUI + reproductor de videos]

```


## Pantalla principal

![Image](https://github.com/user-attachments/assets/225c65f5-d5f8-45ac-a2b5-f2a77543f8ba) <!-- Pantalla principal-->

## Vista con filtros y vista general 
![Image](https://github.com/user-attachments/assets/bd4e24a1-ef8c-46d8-a8d0-d5a18fbb3df9) <!-- ventana con mascaras de color y ventana con todo añadido-->

## Ventana del VAR
![Image](https://github.com/user-attachments/assets/be93450e-ef38-4c85-8a28-2fa92ef9f96b) <!-- VAR -->

## Ventana de selección del campo
![Image](https://github.com/user-attachments/assets/590cc546-e505-47cc-b7f7-5aa4b74929fe) <!-- Seleccion del campo-->

## Ventana de grabaciones
![Image](https://github.com/user-attachments/assets/6fdb605c-1040-40e0-b903-b19aafb61a49) <!-- ventana de grabaciones -->

## Reproducción del VAR
![Image](https://github.com/user-attachments/assets/11bb0025-9e61-496c-8501-12283f4b3120)<!-- ventana de grabaciones reproduccion -->

## Requisitos
- Python 3.10+
- OpenCV
- customtkinter
- pygame
- numpy
- PIL (Pillow)

## Cómo ejecutar

1. Clona el repositorio:
   ```bash
   git clone https://github.com/PabloJLM/Robofut_VAR.git
   cd Robofut_VAR
   
2. Instalar los paquetes:
   ```bash
   pip install -r paquetes.txt
   
3. Prueba la conexión a la cámara con pruebas_camIP.py usando:
   ```bash
   python pruebas_camIP.py
   
4. Ejecuta el programa principal
   ```bash
   python main.py

## Estructura del Proyecto
``` 
Robofut_VAR/
├── main.py              # Script principal
├── aplanar.py           # Usa las coordenadas y realiza la homografía
├── calibrador_hsv.py    # Programa para calibrar las máscaras usando HSV
├── esquinas.npy         # Coordenadas para homografía
├── esquinas.py          # Programa para seleccionar las esquinas
├── grabaciones.py       # Programa para ver las grabaciones
├── porterias.npy        # Coordenadas de porterías
├── porterias.py         # Programa para seleccionar porterías
├── pruebas.py           # Programa para depurar y probar la GUI principal
├── pruebas_camIP.py     # Programa para probar la cámara IP
├── var/                 # Carpeta donde se guardan las repeticiones
└── ...
``` 

## Agradecimientos
Este proyecto fue posible gracias al apoyo del equipo del Proyecto BALAM, al Dr. Óscar Rodas por su guía, y a la Universidad, por facilitar los recursos técnicos necesarios para su desarrollo.

## Créditos
Este proyecto fue desarrollado por [Pablo Jose López Mazariegos](https://github.com/PabloJLM) para el Encuentro Nacional de Robótica **BALAM** 🇬🇹.

## Licencia
Este proyecto está bajo la [MIT License](LICENSE).
