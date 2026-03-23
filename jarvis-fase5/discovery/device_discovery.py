"""
JARVIS FASE 5 - Device Discovery
Descubrimiento automático y clasificación de dispositivos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

from sys import path
path.insert(0, '..')

from bluetooth.bt_controller import BluetoothController
from wifi.wifi_controller import WiFiController

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/discovery.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Tipos de dispositivos"""
    M5STACK = "m5stack"
    KODE_DOT = "kode_dot"
    SMART_TV = "smart_tv"
    SMART_SPEAKER = "smart_speaker"
    SMART_LIGHT = "smart_light"
    SMART_PLUG = "smart_plug"
    SENSOR = "sensor"
    CAMERA = "camera"
    ROUTER = "router"
    COMPUTER = "computer"
    PHONE = "phone"
    UNKNOWN = "unknown"


class DeviceDiscovery:
    """Sistema de descubrimiento de dispositivos"""
    
    def __init__(self):
        """Inicializar descubrimiento"""
        logger.info("🔍 Inicializando Device Discovery...")
        
        self.bt_controller = BluetoothController()
        self.wifi_controller = WiFiController()
        
        self.all_devices: Dict[str, Dict] = {}
        
        # Patrones de identificación
        self.identification_patterns = {
            DeviceType.M5STACK: ['m5stack', 'M5Stack', 'M5'],
            DeviceType.KODE_DOT: ['kode', 'KodeDot', 'dot'],
            DeviceType.SMART_TV: ['tv', 'TV', 'samsung', 'lg', 'sony', 'chromecast'],
            DeviceType.SMART_SPEAKER: ['speaker', 'echo', 'google', 'alexa'],
            DeviceType.SMART_LIGHT: ['light', 'philips', 'hue', 'lamp'],
            DeviceType.SMART_PLUG: ['plug', 'outlet', 'power'],
            DeviceType.SENSOR: ['sensor', 'dht', 'temperature', 'humidity'],
            DeviceType.CAMERA: ['camera', 'cam', 'webcam'],
            DeviceType.ROUTER: ['router', 'gateway', 'access point'],
            DeviceType.COMPUTER: ['computer', 'laptop', 'desktop', 'pc'],
            DeviceType.PHONE: ['phone', 'mobile', 'android', 'iphone']
        }
        
        logger.info("✅ Device Discovery inicializado")
    
    def discover_all_devices(self) -> Dict[str, List[Dict]]:
        """
        Descubrir todos los dispositivos (Bluetooth + WiFi)
        
        Returns:
            Diccionario con dispositivos por tipo
        """
        try:
            logger.info("🔍 Descubriendo dispositivos...")
            
            # Escanear Bluetooth
            logger.info("📱 Escaneando Bluetooth...")
            bt_devices = self.bt_controller.scan_devices(duration=10)
            
            # Escanear WiFi
            logger.info("📡 Escaneando WiFi...")
            wifi_devices = self.wifi_controller.scan_network()
            
            # Clasificar dispositivos
            classified_devices = {}
            
            for device_type in DeviceType:
                classified_devices[device_type.value] = []
            
            # Procesar dispositivos Bluetooth
            for bt_device in bt_devices:
                device_info = self._classify_device(
                    bt_device.name,
                    'bluetooth',
                    bt_device.address
                )
                classified_devices[device_info['type']].append(device_info)
                self.all_devices[bt_device.address] = device_info
            
            # Procesar dispositivos WiFi
            for wifi_device in wifi_devices:
                device_info = self._classify_device(
                    wifi_device.name,
                    'wifi',
                    wifi_device.ip
                )
                classified_devices[device_info['type']].append(device_info)
                self.all_devices[wifi_device.ip] = device_info
            
            logger.info(f"✅ Descubrimiento completado: {len(self.all_devices)} dispositivos")
            
            return classified_devices
        
        except Exception as e:
            logger.error(f"❌ Error en descubrimiento: {e}")
            return {}
    
    def _classify_device(self, name: str, protocol: str, identifier: str) -> Dict:
        """
        Clasificar dispositivo por nombre
        
        Args:
            name: Nombre del dispositivo
            protocol: Protocolo (bluetooth, wifi)
            identifier: Identificador (MAC o IP)
            
        Returns:
            Información del dispositivo
        """
        device_type = DeviceType.UNKNOWN
        
        # Buscar coincidencias
        for dtype, patterns in self.identification_patterns.items():
            for pattern in patterns:
                if pattern.lower() in name.lower():
                    device_type = dtype
                    break
            if device_type != DeviceType.UNKNOWN:
                break
        
        return {
            'name': name,
            'type': device_type.value,
            'protocol': protocol,
            'identifier': identifier,
            'discovered_at': str(datetime.now()),
            'connected': False
        }
    
    def connect_to_device(self, identifier: str) -> bool:
        """
        Conectar a dispositivo por identificador
        
        Args:
            identifier: MAC (Bluetooth) o IP (WiFi)
            
        Returns:
            True si conexión exitosa
        """
        try:
            if identifier not in self.all_devices:
                logger.error(f"❌ Dispositivo no encontrado: {identifier}")
                return False
            
            device_info = self.all_devices[identifier]
            protocol = device_info['protocol']
            
            if protocol == 'bluetooth':
                success = self.bt_controller.connect_device(identifier)
            elif protocol == 'wifi':
                success = self.wifi_controller.connect_device(identifier)
            else:
                return False
            
            if success:
                device_info['connected'] = True
                logger.info(f"✅ Conectado a {device_info['name']}")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            return False
    
    def send_command_to_device(self, identifier: str, command: str, 
                               params: Dict = None) -> bool:
        """
        Enviar comando a dispositivo
        
        Args:
            identifier: MAC (Bluetooth) o IP (WiFi)
            command: Comando a enviar
            params: Parámetros del comando
            
        Returns:
            True si envío exitoso
        """
        try:
            if identifier not in self.all_devices:
                logger.error(f"❌ Dispositivo no encontrado: {identifier}")
                return False
            
            device_info = self.all_devices[identifier]
            protocol = device_info['protocol']
            
            if protocol == 'bluetooth':
                success = self.bt_controller.send_command(
                    identifier, command, params
                )
            elif protocol == 'wifi':
                success = self.wifi_controller.send_command(
                    identifier, '/api/command', command, params
                )
            else:
                return False
            
            logger.info(f"📤 Comando enviado a {device_info['name']}: {command}")
            return success
        
        except Exception as e:
            logger.error(f"❌ Error enviando comando: {e}")
            return False
    
    def get_devices_by_type(self, device_type: str) -> List[Dict]:
        """Obtener dispositivos por tipo"""
        return [
            device for device in self.all_devices.values()
            if device['type'] == device_type
        ]
    
    def get_connected_devices(self) -> List[Dict]:
        """Obtener dispositivos conectados"""
        return [
            device for device in self.all_devices.values()
            if device['connected']
        ]
    
    def list_all_devices(self) -> List[Dict]:
        """Listar todos los dispositivos"""
        return list(self.all_devices.values())
    
    def get_device_info(self, identifier: str) -> Optional[Dict]:
        """Obtener información de dispositivo"""
        return self.all_devices.get(identifier)
    
    def print_summary(self):
        """Imprimir resumen de dispositivos"""
        print("\n" + "="*60)
        print("📊 RESUMEN DE DISPOSITIVOS DESCUBIERTOS")
        print("="*60)
        
        # Agrupar por tipo
        by_type = {}
        for device in self.all_devices.values():
            dtype = device['type']
            if dtype not in by_type:
                by_type[dtype] = []
            by_type[dtype].append(device)
        
        # Mostrar por tipo
        for dtype, devices in sorted(by_type.items()):
            print(f"\n🔹 {dtype.upper()} ({len(devices)})")
            for device in devices:
                status = "✅" if device['connected'] else "⭕"
                print(f"  {status} {device['name']} ({device['identifier']})")
        
        print("\n" + "="*60)
        print(f"Total: {len(self.all_devices)} dispositivos")
        print(f"Conectados: {len(self.get_connected_devices())}")
        print("="*60 + "\n")


# Ejemplo de uso
if __name__ == '__main__':
    discovery = DeviceDiscovery()
    
    # Descubrir dispositivos
    devices = discovery.discover_all_devices()
    
    # Mostrar resumen
    discovery.print_summary()
    
    # Conectar a primer dispositivo M5Stack
    m5stacks = discovery.get_devices_by_type('m5stack')
    if m5stacks:
        m5 = m5stacks[0]
        print(f"\n🔗 Conectando a {m5['name']}...")
        if discovery.connect_to_device(m5['identifier']):
            print("✅ Conectado!")
            
            # Enviar comando
            discovery.send_command_to_device(
                m5['identifier'],
                'display',
                {'message': 'Hola desde Jarvis!'}
            )
