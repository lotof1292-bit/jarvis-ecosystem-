#!/usr/bin/env python3
"""
JARVIS FASE 2A - SIMBIOTE
Sistema nervioso central que controla múltiples dispositivos
Personalidades independientes + Sincronización inteligente
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.jarvis_core import JarvisCore
from ui.dashboard import JarvisDashboard
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'jarvis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class JarvisApplication:
    """Aplicación principal de Jarvis FASE 2A"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.core = None
        self.dashboard = None
        
    def initialize(self):
        """Inicializar Jarvis"""
        logger.info("🚀 Inicializando Jarvis FASE 2A SIMBIOTE...")
        
        try:
            # 1. Inicializar núcleo
            self.core = JarvisCore()
            self.core.initialize()
            logger.info("✅ Núcleo inicializado")
            
            # 2. Crear dashboard
            self.dashboard = JarvisDashboard(self.core)
            logger.info("✅ Dashboard creado")
            
            # 3. Conectar señales
            self.setup_connections()
            logger.info("✅ Conexiones establecidas")
            
            # 4. Mostrar dashboard
            self.dashboard.show()
            logger.info("✅ Dashboard mostrado")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Jarvis: {e}", exc_info=True)
            return False
    
    def setup_connections(self):
        """Conectar señales entre componentes"""
        # Conectar eventos del core con el dashboard
        self.core.device_discovered.connect(self.dashboard.on_device_discovered)
        self.core.skill_generated.connect(self.dashboard.on_skill_generated)
        self.core.message_received.connect(self.dashboard.on_message_received)
        self.core.sync_status_changed.connect(self.dashboard.on_sync_status_changed)
    
    def run(self):
        """Ejecutar aplicación"""
        if not self.initialize():
            logger.error("❌ No se pudo inicializar Jarvis")
            return 1
        
        logger.info("🎉 Jarvis FASE 2A SIMBIOTE iniciado correctamente")
        return self.app.exec_()


if __name__ == '__main__':
    app = JarvisApplication()
    sys.exit(app.run())
