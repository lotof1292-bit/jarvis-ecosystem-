"""
DEVICE MANAGER - Gestión de dispositivos
Descubrimiento automático y control de dispositivos WiFi/Bluetooth
"""

import logging
import socket
import subprocess
import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DeviceManager:
    """Gestor de dispositivos conectados"""
    
    def __init__(self, core):
        self.core = core
        self.devices = {}
        self.device_cache_file = Path(core.project_root) / 'config' / 'devices.json'
        self.load_devices_cache()
        self.start_discovery()
    
    def load_devices_cache(self):
        """Cargar dispositivos guardados"""
        if self.device_cache_file.exists():
            try:
                with open(self.device_cache_file, 'r') as f:
                    self.devices = json.load(f)
                logger.info(f"✅ {len(self.devices)} dispositivos cargados del caché")
            except Exception as e:
                logger.error(f"❌ Error cargando caché: {e}")
    
    def save_devices_cache(self):
        """Guardar dispositivos en caché"""
        try:
            with open(self.device_cache_file, 'w') as f:
                json.dump(self.devices, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error guardando caché: {e}")
    
    def start_discovery(self):
        """Iniciar descubrimiento de dispositivos"""
        logger.info("🔍 Iniciando descubrimiento de dispositivos...")
        
        # Descubrimiento WiFi (mDNS)
        self.discover_wifi_devices()
        
        # Descubrimiento Bluetooth
        self.discover_bluetooth_devices()
        
        # Descubrimiento SSH (Pi, Linux)
        self.discover_ssh_devices()
        
        logger.info(f"✅ Descubrimiento completado: {len(self.devices)} dispositivos")
    
    def discover_wifi_devices(self):
        """Descubrir dispositivos WiFi (mDNS)"""
        try:
            # Usar avahi-browse si está disponible (Linux)
            result = subprocess.run(
                ['avahi-browse', '-a', '-t', '-r'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if 'IPv4' in line:
                    # Parsear línea de avahi
                    parts = line.split()
                    if len(parts) > 7:
                        device_name = parts[3]
                        device_ip = parts[7]
                        
                        device_id = f"wifi_{device_name}"
                        if device_id not in self.devices:
                            self.add_device({
                                'id': device_id,
                                'name': device_name,
                                'type': 'wifi',
                                'ip': device_ip,
                                'protocol': 'REST',
                                'authorized': False,
                                'discovered_at': datetime.now().isoformat()
                            })
        
        except Exception as e:
            logger.debug(f"⚠️ No se pudo descubrir dispositivos WiFi: {e}")
    
    def discover_bluetooth_devices(self):
        """Descubrir dispositivos Bluetooth"""
        try:
            # Usar bluetoothctl si está disponible
            result = subprocess.run(
                ['bluetoothctl', 'devices'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            for line in result.stdout.split('\n'):
                if line.startswith('Device'):
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[1]
                        name = ' '.join(parts[2:])
                        
                        device_id = f"ble_{mac}"
                        if device_id not in self.devices:
                            self.add_device({
                                'id': device_id,
                                'name': name,
                                'type': 'bluetooth',
                                'mac': mac,
                                'protocol': 'BLE',
                                'authorized': False,
                                'discovered_at': datetime.now().isoformat()
                            })
        
        except Exception as e:
            logger.debug(f"⚠️ No se pudo descubrir dispositivos Bluetooth: {e}")
    
    def discover_ssh_devices(self):
        """Descubrir dispositivos SSH (Pi, Linux)"""
        # Buscar en hosts conocidos
        ssh_hosts = [
            ('raspberrypi.local', 'Raspberry Pi'),
            ('ubuntu.local', 'Ubuntu'),
            ('192.168.1.100', 'Dispositivo Local')
        ]
        
        for host, name in ssh_hosts:
            try:
                socket.gethostbyname(host)
                device_id = f"ssh_{host}"
                if device_id not in self.devices:
                    self.add_device({
                        'id': device_id,
                        'name': name,
                        'type': 'ssh',
                        'host': host,
                        'protocol': 'SSH',
                        'authorized': False,
                        'discovered_at': datetime.now().isoformat()
                    })
            except socket.gaierror:
                pass
    
    def add_device(self, device_info: Dict):
        """Agregar nuevo dispositivo"""
        device_id = device_info['id']
        self.devices[device_id] = device_info
        
        logger.info(f"📱 Dispositivo agregado: {device_info['name']} ({device_info['type']})")
        
        # Emitir señal
        self.core.device_discovered.emit(device_info)
        
        # Guardar caché
        self.save_devices_cache()
    
    def authorize_device(self, device_id: str) -> bool:
        """Autorizar dispositivo"""
        if device_id in self.devices:
            self.devices[device_id]['authorized'] = True
            self.devices[device_id]['authorized_at'] = datetime.now().isoformat()
            self.save_devices_cache()
            logger.info(f"✅ Dispositivo autorizado: {self.devices[device_id]['name']}")
            return True
        return False
    
    def revoke_device(self, device_id: str) -> bool:
        """Revocar autorización de dispositivo"""
        if device_id in self.devices:
            self.devices[device_id]['authorized'] = False
            self.save_devices_cache()
            logger.info(f"❌ Autorización revocada: {self.devices[device_id]['name']}")
            return True
        return False
    
    def execute_command(self, command: str) -> str:
        """Ejecutar comando en dispositivo"""
        # Parsear comando para identificar dispositivo
        # Ejemplo: "encender tv" -> buscar TV
        
        command_lower = command.lower()
        
        # Buscar dispositivo mencionado
        for device_id, device_info in self.devices.items():
            if device_info['name'].lower() in command_lower:
                if not device_info.get('authorized'):
                    return f"❌ Dispositivo no autorizado: {device_info['name']}"
                
                # Ejecutar comando específico del dispositivo
                return self.send_device_command(device_id, command)
        
        return "❌ No se encontró dispositivo"
    
    def send_device_command(self, device_id: str, command: str) -> str:
        """Enviar comando a dispositivo específico"""
        device = self.devices.get(device_id)
        if not device:
            return "❌ Dispositivo no encontrado"
        
        try:
            if device['type'] == 'wifi':
                return self.send_wifi_command(device, command)
            elif device['type'] == 'bluetooth':
                return self.send_bluetooth_command(device, command)
            elif device['type'] == 'ssh':
                return self.send_ssh_command(device, command)
            else:
                return f"❌ Tipo de dispositivo no soportado: {device['type']}"
        
        except Exception as e:
            logger.error(f"❌ Error enviando comando: {e}")
            return f"Error: {str(e)}"
    
    def send_wifi_command(self, device: Dict, command: str) -> str:
        """Enviar comando por WiFi (REST API)"""
        try:
            # Ejemplo simple
            import requests
            url = f"http://{device['ip']}/command"
            response = requests.post(url, json={'command': command}, timeout=5)
            return response.text
        except Exception as e:
            return f"❌ Error WiFi: {str(e)}"
    
    def send_bluetooth_command(self, device: Dict, command: str) -> str:
        """Enviar comando por Bluetooth"""
        try:
            # Usar bluetoothctl
            subprocess.run(
                ['bluetoothctl', 'connect', device['mac']],
                timeout=5
            )
            return f"✅ Conectado a {device['name']}"
        except Exception as e:
            return f"❌ Error Bluetooth: {str(e)}"
    
    def send_ssh_command(self, device: Dict, command: str) -> str:
        """Enviar comando por SSH"""
        try:
            result = subprocess.run(
                ['ssh', f"ubuntu@{device['host']}", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout or result.stderr
        except Exception as e:
            return f"❌ Error SSH: {str(e)}"
    
    def get_devices(self) -> Dict:
        """Obtener lista de dispositivos"""
        return self.devices
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Obtener información de dispositivo"""
        return self.devices.get(device_id)
