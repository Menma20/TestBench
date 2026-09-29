import time
import logging
from enum import Enum, auto
from typing import List, Tuple

# Configuración del sistema de logging para simular salida de consola de hardware
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - [CLK: %(clock)03d] - [%(levelname)s] - %(message)s",
    datefmt="%H:%M:%S"
)

class EstadoRFID(Enum):
    """Enumerador que define los estados finitos del hardware RFID."""
    IDLE = auto()
    DETECTING = auto()
    READING_DATA = auto()
    TRANSMITTING = auto()
    ERROR = auto()

class FSM_LectorRFID:
    """
    Máquina de Estados Finitos (FSM) que modela la lógica de control 
    de un lector RFID para el proyecto FollowUp.
    """
    
    def __init__(self) -> None:
        self.estado_actual: EstadoRFID = EstadoRFID.IDLE
        self.reloj_ciclos: int = 0
        self.logger = logging.getLogger("FSM_RFID")

    def _log(self, mensaje: str, nivel: int = logging.INFO) -> None:
        """Envoltorio para inyectar el ciclo de reloj en los logs."""
        self.logger.log(nivel, mensaje, extra={"clock": self.reloj_ciclos})

    def flanco_subida(self, senal_presente: bool, lectura_ok: bool) -> None:
        """
        Evalúa las entradas lógicas en el flanco de subida del reloj (Clock Rising Edge)
        y determina la transición de estado.
        """
        self.reloj_ciclos += 1
        self._log(f"Estado actual: {self.estado_actual.name} | Entradas: (Señal={senal_presente}, OK={lectura_ok})", logging.DEBUG)

        # Lógica combinacional de transición de estados
        if self.estado_actual == EstadoRFID.IDLE:
            if senal_presente:
                self.estado_actual = EstadoRFID.DETECTING
                self._log("Interrupción HW: Perturbación en campo magnético. Etiqueta detectada.")
                
        elif self.estado_actual == EstadoRFID.DETECTING:
            self.estado_actual = EstadoRFID.READING_DATA
            self._log("Iniciando protocolo de lectura SPI (MISO/MOSI)...")
            
        elif self.estado_actual == EstadoRFID.READING_DATA:
            if lectura_ok:
                self.estado_actual = EstadoRFID.TRANSMITTING
                self._log("Bits decodificados. CRC válido. Paquete FollowUp identificado.")
            else:
                self.estado_actual = EstadoRFID.ERROR
                self._log("Fallo de paridad o colisión detectada.", logging.ERROR)
                
        elif self.estado_actual == EstadoRFID.TRANSMITTING:
            self._log("Datos transferidos al buffer UART (TX/RX). Retornando a espera.")
            self.estado_actual = EstadoRFID.IDLE
            
        elif self.estado_actual == EstadoRFID.ERROR:
            self._log("Ejecutando rutina de reset (Watchdog).", logging.WARNING)
            self.estado_actual = EstadoRFID.IDLE

def ejecutar_testbench() -> None:
    """
    Banco de pruebas (Testbench) que inyecta vectores de prueba (estímulos)
    en la Máquina de Estados para validar su comportamiento secuencial.
    """
    fsm = FSM_LectorRFID()
    fsm._log("--- INICIANDO TESTBENCH FSM RFID FOLLOWUP ---")

    # Vectores de prueba: Lista de tuplas (senal_presente, lectura_ok)
    vectores_prueba: List[Tuple[bool, bool]] = [
        (False, False),  # T1: Reposo
        (True, False),   # T2: Acercamiento de paquete
        (True, False),   # T3: Detección en progreso
        (True, True),    # T4: Lectura exitosa de la etiqueta
        (False, False),  # T5: Transmisión de datos
        (False, False),  # T6: Reposo
        (True, False),   # T7: Nuevo paquete
        (True, False),   # T8: Detección en progreso
        (True, False),   # T9: Falla en la lectura (simulación de error)
        (False, False),  # T10: Recuperación
    ]

    for senal, ok in vectores_prueba:
        fsm.flanco_subida(senal, ok)
        time.sleep(0.3)  # Retardo artificial para facilitar la lectura en consola

    fsm._log("--- FIN DE LA SIMULACIÓN ---")

if __name__ == "__main__":
    ejecutar_testbench()