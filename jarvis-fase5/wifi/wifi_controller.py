"""
JARVIS FASE 5 - WiFi Controller
Control universal de dispositivos por WiFi
"""

import requests
import json
import threading
import logging
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime
import socket
import subprocess

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/wifi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class WiFiDevice:
    """Representación de dispositivo WiFi"""
    name: str
    ip: str
    port: int = 80
    connected: bool = False
    last_seen: Optional[str] = None
    device_type: str = "generic"  # m5stack, kode_dot, smart_tv, etc.
    mac_address: Optional[str] = None


class WiFiController:
    """Controlador universal de WiFi"""
    
    def __init__(self, network_prefix: str = "192.168.1", scan_interval: int = 60):
        """
        Inicializar controlador WiFi
        
        Args:
            network_prefix: Prefijo de red (ej: 192.168.1)
            scan_interval: Intervalo de escaneo en segundos
        """
        logger.info("📡 Inicializando WiFi Controller...")
        
        self.devices: Dict[str, WiFiDevice] = {}
        self.network_prefix = network_prefix
        self.scan_interval = scan_interval
        self.scanning = False
        self.callbacks: Dict[str, List[Callable]] = {
            'device_found': [],
            'device_connected': [],
            'device_disconnected': [],
            'data_received': [],
            'command_executed': []
        }
        
        # Estadísticas
        self.stats = {
            'total_scans': 0,
            'devices_found': 0,
            'commands_sent': 0,
            'commands_failed': 0,
            'start_time': str(datetime.now())
        }
        
        logger.info("✅ WiFi Controller inicializado")
    
    def scan_network(self, timeout: int = 2) -> List[WiFiDevice]:
        """
        Escanear dispositivos WiFi en la red
        
        Args:
            timeout: Timeout para cada ping
            
        Returns:
            Lista de dispositivos encontrados
        """
        try:
            logger.info(f"🔍 Escaneando red {self.network_prefix}.0/24...")
            self.stats['total_scans'] += 1
            
            found_devices = []
            
            # Escanear rango de IPs
            for i in range(1, 255):
                ip = f"{self.network_prefix}.{i}"
                
                # Ping para verificar si está activo
                if self._ping(ip, timeout):
                    # Obtener nombre del dispositivo
                    hostname = self._get_hostname(ip)
                    
                    if ip not in self.devices:
                        device = WiFiDevice(
                            name=hostname or f"Device_{i}",
                            ip=ip,
                            last_seen=str(datetime.now())
                        )
                        self.devices[ip] = device
                        self.stats['devices_found'] += 1
                        found_devices.append(device)
                        
                        logger.info(f"✅ Dispositivo encontrado: {device.name} ({ip})")
                        self._trigger_callback('device_found', device)
                    else:
                        # Actualizar último visto
                        self.devices[ip].last_seen = str(datetime.now())
        
        except Exception as e:
            logger.error(f"❌ Error en escaneo: {e}")
        
        logger.info(f"📊 Total de dispositivos: {len(self.devices)}")
        return found_devices
    
    def _ping(self, ip: str, timeout: int = 2) -> bool:
        """Hacer ping a IP"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout*1000), ip],
                capture_output=True,
                timeout=timeout+1
            )
            return result.returncode == 0
        except:
            return False
    
    def _get_hostname(self, ip: str) -> Optional[str]:
        """Obtener hostname de IP"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return None
    
    def connect_device(self, ip: str, port: int = 80, timeout: int = 5) -> bool:
        """
        Conectar a dispositivo WiFi
        
        Args:
            ip: Dirección IP del dispositivo
            port: Puerto HTTP (default: 80)
            timeout: Timeout de conexión
            
        Returns:
            True si conexión exitosa
        """
        try:
            if ip not in self.devices:
                logger.error(f"❌ Dispositivo no encontrado: {ip}")
                return False
            
            device = self.devices[ip]
            logger.info(f"🔗 Conectando a {device.name}...")
            
            # Hacer request de prueba
            response = requests.get(
                f'http://{ip}:{port}/health',
                timeout=timeout
            )
            
            if response.status_code == 200:
                device.connected = True
                device.port = port
                logger.info(f"✅ Conectado a {device.name}")
                self._trigger_callback('device_connected', device)
                return True
            else:
                logger.error(f"❌ Respuesta inválida: {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            return False
    
    def disconnect_device(self, ip: str) -> bool:
        """
        Desconectar de dispositivo WiFi
        
        Args:
            ip: Dirección IP del dispositivo
            
        Returns:
            True si desconexión exitosa
        """
        try:
            if ip not in self.devices:
                return False
            
            device = self.devices[ip]
            device.connected = False
            
            logger.info(f"✅ Desconectado de {device.name}")
            self._trigger_callback('device_disconnected', device)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error desconectando: {e}")
            return False
    
    def send_command(self, ip: str, endpoint: str, command: str, 
                     params: Dict = None, method: str = 'POST') -> Optional[Dict]:
        """
        Enviar comando a dispositivo WiFi
        
        Args:
            ip: Dirección IP del dispositivo
            endpoint: Endpoint del API
            command: Comando a enviar
            params: Parámetros del comando
            method: Método HTTP (POST, GET, etc.)
            
        Returns:
            Respuesta del dispositivo o None
        """
        try:
            if ip not in self.devices:
                logger.error(f"❌ Dispositivo no encontrado: {ip}")
                self.stats['commands_failed'] += 1
                return None
            
            device = self.devices[ip]
            
            if not device.connected:
                logger.error(f"❌ Dispositivo no conectado: {device.name}")
                self.stats['commands_failed'] += 1
                return None
            
            # Construir URL
            url = f'http://{ip}:{device.port}{endpoint}'
            
            # Construir payload
            payload = {
                'command': command,
                'params': params or {},
                'timestamp': str(datetime.now())
            }
            
            # Enviar request
            if method.upper() == 'POST':
                response = requests.post(url, json=payload, timeout=5)
            elif method.upper() == 'GET':
                response = requests.get(url, params=payload, timeout=5)
            else:
                response = requests.request(method, url, json=payload, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"📤 Comando enviado a {device.name}: {command}")
                self.stats['commands_sent'] += 1
                self._trigger_callback('command_executed', {
                    'device': device.name,
                    'command': command,
                    'status': 'sent'
                })
                return response.json()
            else:
                logger.error(f"❌ Error en respuesta: {response.status_code}")
                self.stats['commands_failed'] += 1
                return None
        
        except Exception as e:
            logger.error(f"❌ Error enviando comando: {e}")
            self.stats['commands_failed'] += 1
            return None
    
    def get_device_info(self, ip: str) -> Optional[Dict]:
        """Obtener información de dispositivo"""
        if ip not in self.devices:
            return None
        
        device = self.devices[ip]
        return {
            'name': device.name,
            'ip': device.ip,
            'connected': device.connected,
            'device_type': device.device_type,
            'last_seen': device.last_seen,
            'port': device.port,
            'mac_address': device.mac_address
        }
    
    def list_devices(self, connected_only: bool = False) -> List[Dict]:
        """Listar dispositivos"""
        devices = []
        
        for ip, device in self.devices.items():
            if connected_only and not device.connected:
                continue
            
            devices.append({
                'name': device.name,
                'ip': device.ip,
                'connected': device.connected,
                'device_type': device.device_type,
                'last_seen': device.last_seen
            })
        
        return devices
    
    def set_device_type(self, ip: str, device_type: str):
        """Establecer tipo de dispositivo"""
        if ip in self.devices:
            self.devices[ip].device_type = device_type
            logger.info(f"✅ Tipo de dispositivo actualizado: {device_type}")
    
    def register_callback(self, event: str, callback: Callable):
        """Registrar callback para evento"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            logger.info(f"✅ Callback registrado para: {event}")
    
    def _trigger_callback(self, event: str, data: any):
        """Disparar callbacks registrados"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"❌ Error en callback: {e}")
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return {
            **self.stats,
            'connected_devices': sum(1 for d in self.devices.values() if d.connected),
            'total_devices': len(self.devices)
        }
    
    def start_continuous_scan(self):
        """Iniciar escaneo continuo en thread"""
        def scan_loop():
            self.scanning = True
            while self.scanning:
                self.scan_network()
                import time
                time.sleep(self.scan_interval)
        
        thread = threading.Thread(target=scan_loop, daemon=True)
        thread.start()
        logger.info("🔄 Escaneo continuo iniciado")
    
    def stop_continuous_scan(self):
        """Detener escaneo continuo"""
        self.scanning = False
        logger.info("⏹️ Escaneo continuo detenido")


# Ejemplo de uso
if __name__ == '__main__':
    wifi = WiFiController()
    
    # Escanear red
    devices = wifi.scan_network()
    
    print("\n🌐 Dispositivos encontrados:")
    for device in wifi.list_devices():
        print(f"  - {device['name']} ({device['ip']})")
    
    # Conectar a primer dispositivo
    if devices:
        first_device = devices[0]
        if wifi.connect_device(first_device.ip):
            # Enviar comando
            result = wifi.send_command(
                first_device.ip,
                '/api/command',
                'test',
                {'param': 'value'}
            )
            print(f"Respuesta: {result}")
            
            # Desconectar
            wifi.disconnect_device(first_device.ip)
    
    # Ver estadísticas
    print(f"\n📊 Estadísticas: {wifi.get_stats()}")
