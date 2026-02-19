
import sys
import os

# Add root and libs to sys.path
root_dir = os.getcwd()
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'libs'))

print("Testing imports...")

try:
    import libs.db_connection
    print("✅ libs.db_connection imported")
except ImportError as e:
    print(f"❌ libs.db_connection failed: {e}")

try:
    import libs.logger
    print("✅ libs.logger imported")
except ImportError as e:
    print(f"❌ libs.logger failed: {e}")

try:
    import modules.ingesta_ventas.app
    print("✅ modules.ingesta_ventas.app imported")
except ImportError as e:
    print(f"❌ modules.ingesta_ventas.app failed: {e}")

try:
    import modules.ingesta_ventas.services.extraction_service
    print("✅ modules.ingesta_ventas.services.extraction_service imported")
except ImportError as e:
    print(f"❌ modules.ingesta_ventas.services.extraction_service failed: {e}")

try:
    import modules.ingesta_ventas.services.db_service
    print("✅ modules.ingesta_ventas.services.db_service imported")
except ImportError as e:
    print(f"❌ modules.ingesta_ventas.services.db_service failed: {e}")

print("Test finished.")
