"""
JARVIS CORE - Motor central del sistema
Gestiona dispositivos, LLM, personalidades y sincronización
"""

import json
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime

logger = logging.getLogger(__name__)


class JarvisCore(QObject):
    """Núcleo central de Jarvis"""
    
    # Señales
    device_discovered = pyqtSignal(dict)  # Nuevo dispositivo descubierto
    skill_generated = pyqtSignal(dict)    # Nueva skill generada
    message_received = pyqtSignal(dict)   # Mensaje recibido
    sync_status_changed = pyqtSignal(str) # Estado de sincronización cambió
    
    def __init__(self):
        super().__init__()
        
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / 'config'
        self.devices = {}
        self.skills = {}
        self.personality = None
        self.llm_manager = None
        self.device_manager = None
        self.skill_generator = None
        self.sync_manager = None
        
        logger.info("🔧 Jarvis Core inicializado")
    
    def initialize(self):
        """Inicializar todos los componentes"""
        try:
            # 1. Cargar configuración
            self.load_config()
            logger.info("✅ Configuración cargada")
            
            # 2. Inicializar componentes
            self.init_llm_manager()
            self.init_device_manager()
            self.init_skill_generator()
            self.init_sync_manager()
            
            logger.info("✅ Jarvis Core completamente inicializado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Jarvis Core: {e}", exc_info=True)
            return False
    
    def load_config(self):
        """Cargar configuración del sistema"""
        config_file = self.config_dir / 'jarvis_config.json'
        
        if not config_file.exists():
            # Crear configuración por defecto
            default_config = {
                "device_id": "jarvis-main-001",
                "device_name": "Jarvis Central",
                "device_type": "desktop",
                "personality_name": "Jarvis",
                "llm_model": "mistral:7b",
                "ollama_host": "http://localhost:11434",
                "auto_discovery": True,
                "sync_enabled": True,
                "security_level": "high"
            }
            
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"✅ Configuración por defecto creada en {config_file}")
        
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        logger.info(f"✅ Configuración cargada: {self.config['device_name']}")
    
    def init_llm_manager(self):
        """Inicializar gestor de LLM"""
        from llm.ollama_manager import OllamaManager
        self.llm_manager = OllamaManager(self.config)
        logger.info("✅ LLM Manager inicializado")
    
    def init_device_manager(self):
        """Inicializar gestor de dispositivos"""
        from devices.device_manager import DeviceManager
        self.device_manager = DeviceManager(self)
        logger.info("✅ Device Manager inicializado")
    
    def init_skill_generator(self):
        """Inicializar generador de skills"""
        from skills.skill_generator import SkillGenerator
        self.skill_generator = SkillGenerator(self)
        logger.info("✅ Skill Generator inicializado")
    
    def init_sync_manager(self):
        """Inicializar gestor de sincronización"""
        from sync.sync_manager import SyncManager
        self.sync_manager = SyncManager(self)
        logger.info("✅ Sync Manager inicializado")
    
    def process_command(self, command: str) -> str:
        """Procesar comando del usuario"""
        try:
            # 1. Pasar al LLM
            response = self.llm_manager.process(command)
            
            # 2. Detectar intención (dispositivo, skill, etc.)
            intent = self.detect_intent(command, response)
            
            # 3. Ejecutar acción correspondiente
            if intent['type'] == 'device_control':
                return self.execute_device_control(intent)
            elif intent['type'] == 'skill_execution':
                return self.execute_skill(intent)
            else:
                return response
            
        except Exception as e:
            logger.error(f"❌ Error procesando comando: {e}")
            return f"Error: {str(e)}"
    
    def detect_intent(self, command: str, response: str) -> Dict:
        """Detectar intención del comando"""
        # Análisis simple (puede mejorarse con NLP)
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['tv', 'bocina', 'm5stack', 'luz', 'termostato']):
            return {'type': 'device_control', 'command': command}
        elif any(word in command_lower for word in ['ejecuta', 'corre', 'run']):
            return {'type': 'skill_execution', 'command': command}
        else:
            return {'type': 'conversation', 'response': response}
    
    def execute_device_control(self, intent: Dict) -> str:
        """Ejecutar control de dispositivo"""
        try:
            result = self.device_manager.execute_command(intent['command'])
            return result
        except Exception as e:
            logger.error(f"❌ Error ejecutando control: {e}")
            return f"Error: {str(e)}"
    
    def execute_skill(self, intent: Dict) -> str:
        """Ejecutar skill"""
        try:
            result = self.skill_generator.execute_skill(intent['command'])
            return result
        except Exception as e:
            logger.error(f"❌ Error ejecutando skill: {e}")
            return f"Error: {str(e)}"
    
    def get_devices(self) -> Dict:
        """Obtener lista de dispositivos conectados"""
        return self.device_manager.get_devices()
    
    def get_skills(self) -> Dict:
        """Obtener lista de skills disponibles"""
        return self.skill_generator.get_skills()
    
    def get_status(self) -> Dict:
        """Obtener estado del sistema"""
        return {
            'device_id': self.config['device_id'],
            'device_name': self.config['device_name'],
            'devices_connected': len(self.device_manager.get_devices()),
            'skills_available': len(self.skill_generator.get_skills()),
            'llm_status': self.llm_manager.get_status(),
            'sync_status': self.sync_manager.get_status(),
            'timestamp': datetime.now().isoformat()
        }
