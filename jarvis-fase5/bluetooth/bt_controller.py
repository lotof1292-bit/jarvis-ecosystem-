"""
JARVIS FASE 5 - Bluetooth Controller
Control universal de dispositivos por Bluetooth
"""

import bluetooth
import threading
import json
import logging
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bluetooth.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class BluetoothDevice:
    """Representación de dispositivo Bluetooth"""
    name: str
    address: str
    port: int = 1
    connected: bool = False
    socket: Optional[object] = None
    last_seen: Optional[str] = None
    device_type: str = "generic"  # m5stack, kode_dot, speaker, etc.


class BluetoothController:
    """Controlador universal de Bluetooth"""
    
    def __init__(self, scan_interval: int = 30):
        """
        Inicializar controlador Bluetooth
        
        Args:
            scan_interval: Intervalo de escaneo en segundos
        """
        logger.info("🔵 Inicializando Bluetooth Controller...")
        
        self.devices: Dict[str, BluetoothDevice] = {}
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
        
        logger.info("✅ Bluetooth Controller inicializado")
    
    def scan_devices(self, duration: int = 5) -> List[BluetoothDevice]:
        """
        Escanear dispositivos Bluetooth disponibles
        
        Args:
            duration: Duración del escaneo en segundos
            
        Returns:
            Lista de dispositivos encontrados
        """
        try:
            logger.info(f"🔍 Escaneando Bluetooth durante {duration}s...")
            self.stats['total_scans'] += 1
            
            # Realizar escaneo
            nearby_devices = bluetooth.discover_devices(
                duration=duration,
                lookup_names=True,
                flush_cache=True
            )
            
            found_devices = []
            
            for address, name in nearby_devices:
                # Verificar si ya existe
                if address not in self.devices:
                    device = BluetoothDevice(
                        name=name or "Unknown",
                        address=address,
                        last_seen=str(datetime.now())
                    )
                    self.devices[address] = device
                    self.stats['devices_found'] += 1
                    found_devices.append(device)
                    
                    logger.info(f"✅ Dispositivo encontrado: {name} ({address})")
                    self._trigger_callback('device_found', device)
                else:
                    # Actualizar último visto
                    self.devices[address].last_seen = str(datetime.now())
            
            logger.info(f"📊 Total de dispositivos: {len(self.devices)}")
            return found_devices
        
        except Exception as e:
            logger.error(f"❌ Error en escaneo: {e}")
            return []
    
    def connect_device(self, address: str, port: int = 1) -> bool:
        """
        Conectar a dispositivo Bluetooth
        
        Args:
            address: Dirección MAC del dispositivo
            port: Puerto RFCOMM (default: 1)
            
        Returns:
            True si conexión exitosa
        """
        try:
            if address not in self.devices:
                logger.error(f"❌ Dispositivo no encontrado: {address}")
                return False
            
            device = self.devices[address]
            logger.info(f"🔗 Conectando a {device.name}...")
            
            # Crear socket
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((address, port))
            
            device.socket = sock
            device.connected = True
            device.port = port
            
            logger.info(f"✅ Conectado a {device.name}")
            self._trigger_callback('device_connected', device)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error conectando: {e}")
            return False
    
    def disconnect_device(self, address: str) -> bool:
        """
        Desconectar de dispositivo Bluetooth
        
        Args:
            address: Dirección MAC del dispositivo
            
        Returns:
            True si desconexión exitosa
        """
        try:
            if address not in self.devices:
                return False
            
            device = self.devices[address]
            
            if device.socket:
                device.socket.close()
            
            device.connected = False
            device.socket = None
            
            logger.info(f"✅ Desconectado de {device.name}")
            self._trigger_callback('device_disconnected', device)
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error desconectando: {e}")
            return False
    
    def send_command(self, address: str, command: str, params: Dict = None) -> bool:
        """
        Enviar comando a dispositivo Bluetooth
        
        Args:
            address: Dirección MAC del dispositivo
            command: Comando a enviar
            params: Parámetros del comando
            
        Returns:
            True si envío exitoso
        """
        try:
            if address not in self.devices:
                logger.error(f"❌ Dispositivo no encontrado: {address}")
                self.stats['commands_failed'] += 1
                return False
            
            device = self.devices[address]
            
            if not device.connected:
                logger.error(f"❌ Dispositivo no conectado: {device.name}")
                self.stats['commands_failed'] += 1
                return False
            
            # Construir mensaje
            message = {
                'command': command,
                'params': params or {},
                'timestamp': str(datetime.now())
            }
            
            # Enviar
            data = json.dumps(message).encode('utf-8')
            device.socket.send(data)
            
            logger.info(f"📤 Comando enviado a {device.name}: {command}")
            self.stats['commands_sent'] += 1
            self._trigger_callback('command_executed', {
                'device': device.name,
                'command': command,
                'status': 'sent'
            })
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Error enviando comando: {e}")
            self.stats['commands_failed'] += 1
            return False
    
    def receive_data(self, address: str, buffer_size: int = 1024) -> Optional[str]:
        """
        Recibir datos de dispositivo Bluetooth
        
        Args:
            address: Dirección MAC del dispositivo
            buffer_size: Tamaño del buffer
            
        Returns:
            Datos recibidos o None
        """
        try:
            if address not in self.devices:
                return None
            
            device = self.devices[address]
            
            if not device.connected or not device.socket:
                return None
            
            # Recibir datos
            data = device.socket.recv(buffer_size)
            
            if data:
                logger.info(f"📥 Datos recibidos de {device.name}: {data}")
                self._trigger_callback('data_received', {
                    'device': device.name,
                    'data': data.decode('utf-8')
                })
                return data.decode('utf-8')
            
            return None
        
        except Exception as e:
            logger.error(f"❌ Error recibiendo datos: {e}")
            return None
    
    def get_device_info(self, address: str) -> Optional[Dict]:
        """Obtener información de dispositivo"""
        if address not in self.devices:
            return None
        
        device = self.devices[address]
        return {
            'name': device.name,
            'address': device.address,
            'connected': device.connected,
            'device_type': device.device_type,
            'last_seen': device.last_seen,
            'port': device.port
        }
    
    def list_devices(self, connected_only: bool = False) -> List[Dict]:
        """Listar dispositivos"""
        devices = []
        
        for address, device in self.devices.items():
            if connected_only and not device.connected:
                continue
            
            devices.append({
                'name': device.name,
                'address': device.address,
                'connected': device.connected,
                'device_type': device.device_type,
                'last_seen': device.last_seen
            })
        
        return devices
    
    def set_device_type(self, address: str, device_type: str):
        """Establecer tipo de dispositivo"""
        if address in self.devices:
            self.devices[address].device_type = device_type
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
                self.scan_devices(duration=5)
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
    bt = BluetoothController()
    
    # Escanear dispositivos
    devices = bt.scan_devices(duration=10)
    
    print("\n📱 Dispositivos encontrados:")
    for device in bt.list_devices():
        print(f"  - {device['name']} ({device['address']})")
    
    # Conectar a primer dispositivo
    if devices:
        first_device = devices[0]
        if bt.connect_device(first_device.address):
            # Enviar comando
            bt.send_command(first_device.address, 'test', {'param': 'value'})
            
            # Recibir datos
            data = bt.receive_data(first_device.address)
            print(f"Datos recibidos: {data}")
            
            # Desconectar
            bt.disconnect_device(first_device.address)
    
    # Ver estadísticas
    print(f"\n📊 Estadísticas: {bt.get_stats()}")
