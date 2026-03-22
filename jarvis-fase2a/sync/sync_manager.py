"""
SYNC MANAGER - Sincronización inteligente
Sincroniza datos entre dispositivos cuando hay internet
"""

import json
import logging
import threading
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import socket

logger = logging.getLogger(__name__)


class SyncManager:
    """Gestor de sincronización inteligente"""
    
    def __init__(self, core):
        self.core = core
        self.is_online = False
        self.sync_enabled = core.config.get('sync_enabled', True)
        self.sync_dir = Path(core.project_root) / 'sync'
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Iniciar monitoreo de conectividad
        self.start_connectivity_monitor()
    
    def start_connectivity_monitor(self):
        """Iniciar monitoreo de conectividad"""
        def monitor():
            while True:
                old_status = self.is_online
                self.is_online = self.check_internet()
                
                if old_status != self.is_online:
                    status = "🟢 Online" if self.is_online else "🔴 Offline"
                    logger.info(f"Conectividad: {status}")
                    self.core.sync_status_changed.emit(status)
                    
                    if self.is_online:
                        self.sync_all()
                
                import time
                time.sleep(5)  # Verificar cada 5 segundos
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def check_internet(self) -> bool:
        """Verificar si hay conexión a internet"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except (socket.timeout, socket.error):
            return False
    
    def sync_all(self):
        """Sincronizar todos los datos"""
        if not self.sync_enabled:
            return
        
        logger.info("🔄 Iniciando sincronización...")
        
        try:
            # 1. Sincronizar dispositivos
            self.sync_devices()
            
            # 2. Sincronizar skills
            self.sync_skills()
            
            # 3. Sincronizar conversaciones
            self.sync_conversations()
            
            # 4. Sincronizar personalidades
            self.sync_personalities()
            
            logger.info("✅ Sincronización completada")
            self.core.sync_status_changed.emit("✅ Sincronizado")
        
        except Exception as e:
            logger.error(f"❌ Error en sincronización: {e}")
    
    def sync_devices(self):
        """Sincronizar información de dispositivos"""
        devices = self.core.device_manager.get_devices()
        
        sync_file = self.sync_dir / 'devices_sync.json'
        
        # Leer última sincronización
        last_sync = {}
        if sync_file.exists():
            with open(sync_file, 'r') as f:
                last_sync = json.load(f)
        
        # Comparar y sincronizar cambios
        changes = self.detect_changes(devices, last_sync)
        
        if changes:
            logger.info(f"📱 Sincronizando {len(changes)} cambios de dispositivos")
            # Aquí iría la lógica de sincronización con Google Drive
            self.upload_to_drive('devices', devices)
        
        # Guardar estado actual
        with open(sync_file, 'w') as f:
            json.dump(devices, f, indent=2)
    
    def sync_skills(self):
        """Sincronizar skills"""
        skills = self.core.skill_generator.get_skills()
        
        sync_file = self.sync_dir / 'skills_sync.json'
        
        # Leer última sincronización
        last_sync = {}
        if sync_file.exists():
            with open(sync_file, 'r') as f:
                last_sync = json.load(f)
        
        # Comparar y sincronizar cambios
        changes = self.detect_changes(skills, last_sync)
        
        if changes:
            logger.info(f"⚡ Sincronizando {len(changes)} cambios de skills")
            self.upload_to_drive('skills', skills)
        
        # Guardar estado actual
        with open(sync_file, 'w') as f:
            json.dump(skills, f, indent=2)
    
    def sync_conversations(self):
        """Sincronizar conversaciones"""
        # Aquí iría la lógica de sincronización de conversaciones
        logger.info("💬 Sincronizando conversaciones...")
    
    def sync_personalities(self):
        """Sincronizar personalidades"""
        # Aquí iría la lógica de sincronización de personalidades
        logger.info("👤 Sincronizando personalidades...")
    
    def detect_changes(self, current: Dict, last: Dict) -> Dict:
        """Detectar cambios entre dos estados"""
        changes = {}
        
        # Detectar nuevos elementos
        for key, value in current.items():
            if key not in last:
                changes[key] = {'type': 'new', 'value': value}
            elif value != last.get(key):
                changes[key] = {'type': 'modified', 'value': value}
        
        # Detectar elementos eliminados
        for key in last:
            if key not in current:
                changes[key] = {'type': 'deleted'}
        
        return changes
    
    def upload_to_drive(self, data_type: str, data: Dict):
        """Subir datos a Google Drive"""
        try:
            # Aquí iría la integración real con Google Drive
            # Por ahora, solo guardamos localmente
            
            backup_file = self.sync_dir / f'{data_type}_backup.json'
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Backup guardado: {backup_file}")
        
        except Exception as e:
            logger.error(f"❌ Error subiendo a Drive: {e}")
    
    def download_from_drive(self, data_type: str) -> Optional[Dict]:
        """Descargar datos de Google Drive"""
        try:
            # Aquí iría la integración real con Google Drive
            # Por ahora, solo cargamos del backup local
            
            backup_file = self.sync_dir / f'{data_type}_backup.json'
            if backup_file.exists():
                with open(backup_file, 'r') as f:
                    return json.load(f)
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error descargando de Drive: {e}")
            return None
    
    def merge_data(self, local: Dict, remote: Dict) -> Dict:
        """Fusionar datos locales y remotos"""
        merged = local.copy()
        
        for key, value in remote.items():
            if key not in merged:
                # Agregar elemento remoto
                merged[key] = value
            else:
                # Comparar timestamps si existen
                local_time = merged[key].get('updated_at', '')
                remote_time = value.get('updated_at', '')
                
                if remote_time > local_time:
                    # Usar versión remota si es más reciente
                    merged[key] = value
        
        return merged
    
    def get_status(self) -> Dict:
        """Obtener estado de sincronización"""
        return {
            'online': self.is_online,
            'enabled': self.sync_enabled,
            'status': '🟢 Online' if self.is_online else '🔴 Offline'
        }
    
    def enable_sync(self):
        """Habilitar sincronización"""
        self.sync_enabled = True
        logger.info("✅ Sincronización habilitada")
    
    def disable_sync(self):
        """Deshabilitar sincronización"""
        self.sync_enabled = False
        logger.info("❌ Sincronización deshabilitada")
