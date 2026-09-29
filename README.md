# TestBench
# Módulo de Simulación Lógica (FSM) - Lector RFID FollowUp

Este repositorio contiene el modelado lógico (Testbench) del subsistema de lectura RFID del proyecto **FollowUp**. 

Dado que el ecosistema del proyecto (Backend, API REST, Base de Datos MySQL) está orientado a software de alto nivel, se ha desarrollado este script en **Python** como alternativa a un lenguaje de descripción de hardware (HDL como VHDL o Verilog). El objetivo es abstraer y validar el comportamiento secuencial del microcontrolador (ESP32) al interactuar con el módulo lector RC522.

## Arquitectura del Modelo

El sistema está modelado como una **Máquina de Estados Finitos (FSM - Finite State Machine)**. Emula el comportamiento interno del circuito frente a los flancos de subida del reloj (Clock Rising Edge) y los estímulos de los pines de entrada.

### Estados Definidos (`Enum`)
1. **IDLE (Espera):** El circuito se encuentra en bajo consumo, monitoreando alteraciones en el campo magnético.
2. **DETECTING (Detección):** Transición automática al percibir un tag; prepara el bus SPI.
3. **READING_DATA (Lectura):** Evaluación del stream de bits. Valida el CRC.
4. **TRANSMITTING (Transmisión):** Volcado de la trama de datos correcta hacia el buffer UART/TX.
5. **ERROR (Fallo):** Estado de control de excepciones ante colisiones de datos o paridad incorrecta, seguido de un reset (Watchdog).

## Estructura del Código

- Se implementó tipado estático (`Type Hinting`) para garantizar la robustez del modelo.
- Las transiciones de estado se manejan mediante lógica combinacional pura, evaluada en cada iteración del método `flanco_subida()`.
- Se reemplazó la salida estándar (`print`) por la librería nativa `logging`, permitiendo estampar marcas de tiempo (milisegundos) y simular el conteo de ciclos de reloj de un procesador real.

## Ejecución del Testbench

El script es completamente autocontenido y no requiere de conexión física al hardware (ESP32 o módulo RFID) ni instalación de librerías de terceros. Contiene un vector de pruebas integrado que inyecta estímulos lógicos para evaluar tanto casos de éxito como de error.

**Requisitos:**
- Python 3.8 o superior.

**Instrucciones de ejecución:**
```bash
python simulador_fsm_rfid.py