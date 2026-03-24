"""
JARVIS FASE 5 - Network Sniffer
Detector de intrusos y monitor de tráfico de red
"""

import logging
import subprocess
import json
import threading
from typing import Dict, List, Optional
from datetime import datetime
import socket
import struct
import textwrap
import ipaddress

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/network_sniffer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class NetworkDevice:
    """Representación de dispositivo en la red"""
    
    def __init__(self, ip: str, mac: str, hostname: str = None):
        self.ip = ip
        self.mac = mac
        self.hostname = hostname or "Unknown"
        self.first_seen = str(datetime.now())
        self.last_seen = str(datetime.now())
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.protocols = {}  # Protocolos usados
        self.ports = set()   # Puertos accedidos
        self.is_trusted = False
        self.is_intruder = False
    
    def to_dict(self) -> Dict:
        return {
            'ip': self.ip,
            'mac': self.mac,
            'hostname': self.hostname,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'protocols': self.protocols,
            'ports': list(self.ports),
            'is_trusted': self.is_trusted,
            'is_intruder': self.is_intruder
        }


class NetworkSniffer:
    """Sniffer de red para detectar intrusos"""
    
    def __init__(self, network_interface: str = None, network_prefix: str = "192.168.1"):
        """
        Inicializar sniffer
        
        Args:
            network_interface: Interfaz de red (eth0, wlan0, etc.)
            network_prefix: Prefijo de red (ej: 192.168.1)
        """
        logger.info("🔍 Inicializando Network Sniffer...")
        
        self.network_interface = network_interface or self._get_default_interface()
        self.network_prefix = network_prefix
        self.devices: Dict[str, NetworkDevice] = {}
        self.trusted_devices: List[str] = []
        self.sniffing = False
        
        # Estadísticas
        self.stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'start_time': str(datetime.now()),
            'intruders_detected': 0
        }
        
        logger.info(f"✅ Network Sniffer inicializado (Interfaz: {self.network_interface})")
    
    def _get_default_interface(self) -> str:
        """Obtener interfaz de red por defecto"""
        try:
            result = subprocess.run(
                ['ip', 'route', 'show'],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        return parts[4]
            
            return 'eth0'
        except:
            return 'eth0'
    
    def scan_network(self) -> Dict[str, NetworkDevice]:
        """
        Escanear red para encontrar dispositivos
        
        Returns:
            Diccionario de dispositivos encontrados
        """
        try:
            logger.info(f"🔍 Escaneando red {self.network_prefix}.0/24...")
            
            for i in range(1, 255):
                ip = f"{self.network_prefix}.{i}"
                
                # Ping para verificar si está activo
                if self._ping(ip):
                    # Obtener MAC
                    mac = self._get_mac(ip)
                    
                    # Obtener hostname
                    hostname = self._get_hostname(ip)
                    
                    if ip not in self.devices:
                        device = NetworkDevice(ip, mac, hostname)
                        self.devices[ip] = device
                        
                        logger.info(f"✅ Dispositivo encontrado: {hostname} ({ip}) - {mac}")
                    else:
                        self.devices[ip].last_seen = str(datetime.now())
            
            logger.info(f"📊 Total de dispositivos: {len(self.devices)}")
            return self.devices
        
        except Exception as e:
            logger.error(f"❌ Error escaneando: {e}")
            return {}
    
    def _ping(self, ip: str, timeout: int = 1) -> bool:
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
    
    def _get_mac(self, ip: str) -> str:
        """Obtener MAC de IP"""
        try:
            result = subprocess.run(
                ['arp', '-n', ip],
                capture_output=True,
                text=True
            )
            
            for line in result.stdout.split('\n'):
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        return parts[2]
            
            return "Unknown"
        except:
            return "Unknown"
    
    def _get_hostname(self, ip: str) -> str:
        """Obtener hostname de IP"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return f"Device_{ip.split('.')[-1]}"
    
    def mark_trusted(self, ip: str):
        """Marcar dispositivo como confiable"""
        if ip in self.devices:
            self.devices[ip].is_trusted = True
            self.trusted_devices.append(ip)
            logger.info(f"✅ Dispositivo marcado como confiable: {ip}")
    
    def mark_intruder(self, ip: str):
        """Marcar dispositivo como intruso"""
        if ip in self.devices:
            self.devices[ip].is_intruder = True
            self.stats['intruders_detected'] += 1
            logger.warning(f"🚨 Dispositivo marcado como intruso: {ip}")
    
    def get_unknown_devices(self) -> List[NetworkDevice]:
        """Obtener dispositivos desconocidos"""
        return [
            device for device in self.devices.values()
            if not device.is_trusted and not device.is_intruder
        ]
    
    def get_intruders(self) -> List[NetworkDevice]:
        """Obtener intrusos detectados"""
        return [
            device for device in self.devices.values()
            if device.is_intruder
        ]
    
    def get_trusted_devices(self) -> List[NetworkDevice]:
        """Obtener dispositivos confiables"""
        return [
            device for device in self.devices.values()
            if device.is_trusted
        ]
    
    def analyze_device(self, ip: str) -> Dict:
        """Analizar dispositivo específico"""
        if ip not in self.devices:
            return {'error': 'Dispositivo no encontrado'}
        
        device = self.devices[ip]
        
        return {
            'ip': device.ip,
            'mac': device.mac,
            'hostname': device.hostname,
            'first_seen': device.first_seen,
            'last_seen': device.last_seen,
            'activity': {
                'packets_sent': device.packets_sent,
                'packets_received': device.packets_received,
                'bytes_sent': device.bytes_sent,
                'bytes_received': device.bytes_received,
                'total_traffic': device.bytes_sent + device.bytes_received
            },
            'protocols': device.protocols,
            'ports_accessed': list(device.ports),
            'status': 'Intruso' if device.is_intruder else ('Confiable' if device.is_trusted else 'Desconocido'),
            'threat_level': self._calculate_threat_level(device)
        }
    
    def _calculate_threat_level(self, device: NetworkDevice) -> str:
        """Calcular nivel de amenaza"""
        if device.is_intruder:
            return 'CRÍTICO'
        
        if device.is_trusted:
            return 'BAJO'
        
        # Analizar comportamiento
        if device.packets_sent > 1000:
            return 'ALTO'
        
        if device.packets_sent > 100:
            return 'MEDIO'
        
        return 'BAJO'
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return {
            **self.stats,
            'total_devices': len(self.devices),
            'trusted_devices': len(self.get_trusted_devices()),
            'intruders': len(self.get_intruders()),
            'unknown_devices': len(self.get_unknown_devices())
        }
    
    def print_summary(self):
        """Imprimir resumen"""
        print("\n" + "="*70)
        print("🔍 NETWORK SNIFFER - RESUMEN")
        print("="*70)
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  Total de dispositivos: {len(self.devices)}")
        print(f"  Dispositivos confiables: {len(self.get_trusted_devices())}")
        print(f"  Intrusos detectados: {len(self.get_intruders())}")
        print(f"  Dispositivos desconocidos: {len(self.get_unknown_devices())}")
        
        print(f"\n✅ DISPOSITIVOS CONFIABLES:")
        for device in self.get_trusted_devices():
            print(f"  - {device.hostname} ({device.ip}) - {device.mac}")
        
        print(f"\n⚠️ DISPOSITIVOS DESCONOCIDOS:")
        for device in self.get_unknown_devices():
            print(f"  - {device.hostname} ({device.ip}) - {device.mac}")
        
        print(f"\n🚨 INTRUSOS:")
        for device in self.get_intruders():
            print(f"  - {device.hostname} ({device.ip}) - {device.mac}")
        
        print("\n" + "="*70 + "\n")
    
    def export_report(self, filename: str):
        """Exportar reporte"""
        try:
            report = {
                'timestamp': str(datetime.now()),
                'stats': self.get_stats(),
                'trusted_devices': [d.to_dict() for d in self.get_trusted_devices()],
                'unknown_devices': [d.to_dict() for d in self.get_unknown_devices()],
                'intruders': [d.to_dict() for d in self.get_intruders()]
            }
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Reporte exportado a: {filename}")
        except Exception as e:
            logger.error(f"❌ Error exportando: {e}")


# Ejemplo de uso
if __name__ == '__main__':
    sniffer = NetworkSniffer()
    
    # Escanear red
    devices = sniffer.scan_network()
    
    # Marcar dispositivos confiables
    if devices:
        first_ip = list(devices.keys())[0]
        sniffer.mark_trusted(first_ip)
    
    # Mostrar resumen
    sniffer.print_summary()
    
    # Analizar dispositivo
    if devices:
        for ip in list(devices.keys())[:3]:
            analysis = sniffer.analyze_device(ip)
            print(f"\n📊 Análisis de {ip}:")
            print(json.dumps(analysis, indent=2))
    
    # Exportar reporte
    sniffer.export_report('network_report.json')
