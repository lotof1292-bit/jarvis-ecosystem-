"""
JARVIS FASE 5 - Network Monitor
Monitor en tiempo real de intrusos y tráfico
"""

import logging
import os
import time
import threading
from typing import Dict, List
from datetime import datetime

from network_sniffer import NetworkSniffer
from traffic_analyzer import TrafficAnalyzer
from intruder_report import IntruderReport

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """Monitor en tiempo real de red"""
    
    def __init__(self, network_prefix: str = "192.168.1", scan_interval: int = 30):
        """
        Inicializar monitor
        
        Args:
            network_prefix: Prefijo de red
            scan_interval: Intervalo de escaneo en segundos
        """
        logger.info("🔍 Inicializando Network Monitor...")
        
        self.sniffer = NetworkSniffer(network_prefix=network_prefix)
        self.analyzer = TrafficAnalyzer()
        self.report_gen = IntruderReport(self.sniffer, self.analyzer)
        
        self.scan_interval = scan_interval
        self.monitoring = False
        self.monitor_thread = None
        
        logger.info("✅ Network Monitor inicializado")
    
    def start_monitoring(self):
        """Iniciar monitoreo"""
        if self.monitoring:
            logger.warning("⚠️  Ya está monitoreando")
            return
        
        logger.info("🚀 Iniciando monitoreo...")
        self.monitoring = True
        
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        logger.info("⏹️  Monitoreo detenido")
    
    def _monitor_loop(self):
        """Loop de monitoreo"""
        while self.monitoring:
            try:
                logger.info("🔍 Escaneando red...")
                self.sniffer.scan_network()
                
                # Detectar intrusos automáticamente
                unknown = self.sniffer.get_unknown_devices()
                if unknown:
                    logger.warning(f"⚠️  {len(unknown)} dispositivos desconocidos detectados")
                
                time.sleep(self.scan_interval)
            
            except Exception as e:
                logger.error(f"❌ Error en monitoreo: {e}")
                time.sleep(5)
    
    def scan_now(self):
        """Escanear ahora"""
        logger.info("🔍 Escaneando red...")
        return self.sniffer.scan_network()
    
    def mark_trusted(self, ip: str):
        """Marcar como confiable"""
        self.sniffer.mark_trusted(ip)
    
    def mark_intruder(self, ip: str):
        """Marcar como intruso"""
        self.sniffer.mark_intruder(ip)
    
    def get_status(self) -> Dict:
        """Obtener estado actual"""
        return {
            'monitoring': self.monitoring,
            'timestamp': str(datetime.now()),
            'devices': {
                'total': len(self.sniffer.devices),
                'trusted': len(self.sniffer.get_trusted_devices()),
                'unknown': len(self.sniffer.get_unknown_devices()),
                'intruders': len(self.sniffer.get_intruders())
            },
            'traffic': {
                'total_packets': self.analyzer.stats['total_packets'],
                'total_bytes': self.analyzer.stats['total_bytes'],
                'unique_flows': self.analyzer.stats['unique_flows']
            }
        }
    
    def get_intruders(self) -> List[Dict]:
        """Obtener intrusos"""
        return [d.to_dict() for d in self.sniffer.get_intruders()]
    
    def get_unknown_devices(self) -> List[Dict]:
        """Obtener dispositivos desconocidos"""
        return [d.to_dict() for d in self.sniffer.get_unknown_devices()]
    
    def get_device_analysis(self, ip: str) -> Dict:
        """Analizar dispositivo"""
        device_analysis = self.sniffer.analyze_device(ip)
        traffic_analysis = self.analyzer.get_device_traffic(ip)
        
        return {
            'device': device_analysis,
            'traffic': traffic_analysis
        }
    
    def get_report(self) -> str:
        """Obtener reporte"""
        return self.report_gen.generate_simple_report()
    
    def save_report(self, filename: str, format: str = 'txt'):
        """Guardar reporte"""
        self.report_gen.save_report(filename, format)
    
    def display_dashboard(self):
        """Mostrar dashboard en consola"""
        while True:
            try:
                os.system('clear' if os.name == 'posix' else 'cls')
                
                status = self.get_status()
                
                print("\n" + "="*80)
                print("🔍 NETWORK MONITOR - DASHBOARD EN TIEMPO REAL")
                print("="*80)
                print(f"Actualizado: {status['timestamp']}")
                print(f"Estado: {'🟢 MONITOREANDO' if status['monitoring'] else '🔴 DETENIDO'}\n")
                
                # Estadísticas de dispositivos
                print("📱 DISPOSITIVOS:")
                print(f"  Total: {status['devices']['total']}")
                print(f"  ✅ Confiables: {status['devices']['trusted']}")
                print(f"  ⚠️  Desconocidos: {status['devices']['unknown']}")
                print(f"  🚨 Intrusos: {status['devices']['intruders']}\n")
                
                # Estadísticas de tráfico
                print("📊 TRÁFICO:")
                print(f"  Paquetes: {status['traffic']['total_packets']}")
                print(f"  Datos: {status['traffic']['total_bytes']/1_000_000:.2f}MB")
                print(f"  Flujos: {status['traffic']['unique_flows']}\n")
                
                # Intrusos
                intruders = self.get_intruders()
                if intruders:
                    print("🚨 INTRUSOS DETECTADOS:")
                    for device in intruders:
                        print(f"  • {device['hostname']} ({device['ip']})")
                        print(f"    MAC: {device['mac']}")
                        print(f"    Tráfico: {(device['bytes_sent'] + device['bytes_received'])/1_000_000:.2f}MB\n")
                
                # Dispositivos desconocidos
                unknown = self.get_unknown_devices()
                if unknown:
                    print("⚠️  DISPOSITIVOS DESCONOCIDOS:")
                    for device in unknown[:5]:
                        print(f"  • {device['hostname']} ({device['ip']})")
                        print(f"    MAC: {device['mac']}")
                        print(f"    Paquetes: {device['packets_sent'] + device['packets_received']}\n")
                
                print("="*80)
                print("Presiona Ctrl+C para salir")
                print("="*80 + "\n")
                
                time.sleep(5)
            
            except KeyboardInterrupt:
                print("\n\n👋 Dashboard cerrado")
                break
            except Exception as e:
                logger.error(f"Error en dashboard: {e}")
                time.sleep(5)


# Ejemplo de uso
if __name__ == '__main__':
    # Crear monitor
    monitor = NetworkMonitor()
    
    # Escanear inicialmente
    print("🔍 Escaneando red inicial...")
    monitor.scan_now()
    
    # Mostrar estado
    status = monitor.get_status()
    print(f"\n✅ Escaneo completado")
    print(f"  Total de dispositivos: {status['devices']['total']}")
    print(f"  Dispositivos desconocidos: {status['devices']['unknown']}\n")
    
    # Generar reporte
    print("📊 Generando reporte...")
    print(monitor.get_report())
    
    # Guardar reporte
    monitor.save_report('network_report.txt')
    monitor.save_report('network_report.json', format='json')
    print("✅ Reportes guardados\n")
