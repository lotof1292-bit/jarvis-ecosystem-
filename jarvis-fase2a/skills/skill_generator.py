"""
SKILL GENERATOR - Generador dinámico de skills
Crea nuevas habilidades automáticamente según necesidades
"""

import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SkillGenerator:
    """Generador de skills dinámicas"""
    
    def __init__(self, core):
        self.core = core
        self.skills = {}
        self.skills_dir = Path(core.project_root) / 'skills'
        self.load_skills()
    
    def load_skills(self):
        """Cargar skills existentes"""
        skills_file = self.skills_dir / 'skills_registry.json'
        
        if skills_file.exists():
            try:
                with open(skills_file, 'r') as f:
                    self.skills = json.load(f)
                logger.info(f"✅ {len(self.skills)} skills cargadas")
            except Exception as e:
                logger.error(f"❌ Error cargando skills: {e}")
        else:
            # Crear skills por defecto
            self.create_default_skills()
    
    def create_default_skills(self):
        """Crear skills por defecto"""
        default_skills = {
            'hello': {
                'name': 'Saludo',
                'description': 'Saluda al usuario',
                'keywords': ['hola', 'buenos días', 'buenas noches'],
                'action': 'print("¡Hola! Soy Jarvis")'
            },
            'time': {
                'name': 'Hora',
                'description': 'Dice la hora actual',
                'keywords': ['hora', 'qué hora', 'tiempo'],
                'action': 'from datetime import datetime; print(datetime.now().strftime("%H:%M:%S"))'
            },
            'system_info': {
                'name': 'Información del Sistema',
                'description': 'Muestra información del sistema',
                'keywords': ['sistema', 'info', 'información'],
                'action': 'import platform; print(f"Sistema: {platform.system()} {platform.release()}")'
            }
        }
        
        for skill_id, skill_info in default_skills.items():
            self.skills[skill_id] = skill_info
        
        self.save_skills()
        logger.info("✅ Skills por defecto creadas")
    
    def save_skills(self):
        """Guardar skills en archivo"""
        skills_file = self.skills_dir / 'skills_registry.json'
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(skills_file, 'w') as f:
                json.dump(self.skills, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error guardando skills: {e}")
    
    def generate_skill(self, name: str, description: str, keywords: list, action: str) -> Dict:
        """Generar nueva skill dinámicamente"""
        skill_id = name.lower().replace(' ', '_')
        
        skill_info = {
            'id': skill_id,
            'name': name,
            'description': description,
            'keywords': keywords,
            'action': action,
            'created_at': datetime.now().isoformat(),
            'enabled': True
        }
        
        self.skills[skill_id] = skill_info
        self.save_skills()
        
        logger.info(f"⚡ Skill generada: {name}")
        
        # Emitir señal
        self.core.skill_generated.emit(skill_info)
        
        return skill_info
    
    def detect_skill(self, command: str) -> Optional[str]:
        """Detectar qué skill ejecutar basado en comando"""
        command_lower = command.lower()
        
        # Buscar coincidencias de keywords
        best_match = None
        best_score = 0
        
        for skill_id, skill_info in self.skills.items():
            if not skill_info.get('enabled', True):
                continue
            
            for keyword in skill_info.get('keywords', []):
                if keyword.lower() in command_lower:
                    score = len(keyword)  # Priorizar keywords más específicas
                    if score > best_score:
                        best_match = skill_id
                        best_score = score
        
        return best_match
    
    def execute_skill(self, command: str) -> str:
        """Ejecutar skill basado en comando"""
        skill_id = self.detect_skill(command)
        
        if not skill_id:
            return "❌ No se encontró skill para este comando"
        
        skill = self.skills.get(skill_id)
        if not skill:
            return "❌ Skill no encontrada"
        
        try:
            # Ejecutar acción de la skill
            action = skill.get('action', '')
            exec_globals = {}
            exec(action, exec_globals)
            
            logger.info(f"✅ Skill ejecutada: {skill['name']}")
            return f"✅ {skill['name']} ejecutada"
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando skill: {e}")
            return f"❌ Error: {str(e)}"
    
    def auto_generate_device_skill(self, device_info: Dict) -> Dict:
        """Generar skill automáticamente para nuevo dispositivo"""
        device_name = device_info['name']
        device_type = device_info['type']
        
        # Crear skill específica para el dispositivo
        skill_name = f"Controlar {device_name}"
        keywords = [device_name.lower(), device_type.lower()]
        
        # Generar acción basada en tipo de dispositivo
        if device_type == 'wifi':
            action = f'print("Enviando comando a {device_name} por WiFi")'
        elif device_type == 'bluetooth':
            action = f'print("Conectando a {device_name} por Bluetooth")'
        elif device_type == 'ssh':
            action = f'print("Ejecutando comando en {device_name} por SSH")'
        else:
            action = f'print("Controlando {device_name}")'
        
        skill = self.generate_skill(
            name=skill_name,
            description=f"Controla el dispositivo {device_name}",
            keywords=keywords,
            action=action
        )
        
        return skill
    
    def get_skills(self) -> Dict:
        """Obtener lista de skills"""
        return self.skills
    
    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """Obtener información de skill"""
        return self.skills.get(skill_id)
    
    def enable_skill(self, skill_id: str) -> bool:
        """Habilitar skill"""
        if skill_id in self.skills:
            self.skills[skill_id]['enabled'] = True
            self.save_skills()
            return True
        return False
    
    def disable_skill(self, skill_id: str) -> bool:
        """Deshabilitar skill"""
        if skill_id in self.skills:
            self.skills[skill_id]['enabled'] = False
            self.save_skills()
            return True
        return False
    
    def delete_skill(self, skill_id: str) -> bool:
        """Eliminar skill"""
        if skill_id in self.skills:
            del self.skills[skill_id]
            self.save_skills()
            logger.info(f"🗑️ Skill eliminada: {skill_id}")
            return True
        return False
