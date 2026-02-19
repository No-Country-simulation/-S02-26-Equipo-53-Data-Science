# test_backend.py
from src.services.orchestrator import run_backend_cleaning_pipeline
import os

print("🚀 Iniciando prueba del Pipeline de Backend...")
resultado = run_backend_cleaning_pipeline()

if resultado["status"] == "success":
    print(f"✅ ÉXITO: {resultado['message']}")
else:
    print(f"❌ ERROR: {resultado['message']}")