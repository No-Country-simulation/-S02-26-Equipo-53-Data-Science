import time
from datetime import datetime

# Contador de secuencia para seguir el flujo de ejecución
_sequence_counter = 0

def _get_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def logDebug(message, data=None):
    """Log debug - Detalles técnicos para desarrolladores"""
    timestamp = _get_timestamp()
    if data:
        print(f"[DEBUG {timestamp}] {message} | Data: {data}")
    else:
        print(f"[DEBUG {timestamp}] {message}")

def logInfo(message):
    """Log info - Información general del sistema"""
    timestamp = _get_timestamp()
    print(f"[INFO {timestamp}] {message}")

def logSequence(action, detail=''):
    """Log sequence - Muestra el flujo de ejecución de forma comprensible"""
    global _sequence_counter
    _sequence_counter += 1
    timestamp = _get_timestamp()
    detail_message = f" -> {detail}" if detail else ""
    print(f"[STEP {_sequence_counter}] {timestamp} | {action}{detail_message}")

def logWarn(message, context=''):
    """Log warn - Situaciones inesperadas pero manejables"""
    timestamp = _get_timestamp()
    ctx = f" ({context})" if context else ""
    print(f"[WARN {timestamp}] {message}{ctx}")

def logError(message, error=None):
    """Log error - Errores críticos del sistema"""
    timestamp = _get_timestamp()
    print(f"[ERROR {timestamp}] {message}")
    if error:
        print(f"Details: {error}")

def resetSequence():
    """Reinicia el contador de secuencia"""
    global _sequence_counter
    _sequence_counter = 0
    logInfo("Secuencia reiniciada")

def sequenceSummary(operation):
    """Muestra resumen de la secuencia ejecutada"""
    print("=" * 40)
    print(f" RESUMEN: {operation}")
    print(f" Total de pasos ejecutados: {_sequence_counter}")
    print("=" * 40)
