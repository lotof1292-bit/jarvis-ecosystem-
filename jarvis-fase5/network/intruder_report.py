"""
JARVIS FASE 5 - Intruder Report Generator
Generador de reportes simplificados para análisis de intrusos
"""

import logging
import json
from typing import Dict, List
from datetime import datetime
from network_sniffer import NetworkSniffer, NetworkDevice
from traffic_analyzer import TrafficAnalyzer

logger = logging.getLogger(__name__)


class IntruderReport:
    """Generador de reportes de intrusos"""
    
    def __init__(self, sniffer: NetworkSniffer, analyzer: TrafficAnalyzer):
        """
        Inicializar generador de reportes
        
        Args:
            sniffer: Network Sniffer
            analyzer: Traffic Analyzer
        """
        self.sniffer = sniffer
        self.analyzer = analyzer
    
    def generate_simple_report(self) -> str:
        """
        Generar reporte simple y legible
        
        Returns:
            Reporte en formato texto
        """
        report = []
        report.append("\n" + "="*80)
        report.append("🚨 REPORTE DE INTRUSOS - ANÁLISIS SIMPLIFICADO")
        report.append("="*80)
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # RESUMEN EJECUTIVO
        report.append("📊 RESUMEN EJECUTIVO")
        report.append("-" * 80)
        
        intruders = self.sniffer.get_intruders()
        unknown = self.sniffer.get_unknown_devices()
        trusted = self.sniffer.get_trusted_devices()
        
        report.append(f"✅ Dispositivos confiables: {len(trusted)}")
        report.append(f"⚠️  Dispositivos desconocidos: {len(unknown)}")
        report.append(f"🚨 Intrusos detectados: {len(intruders)}\n")
        
        # INTRUSOS DETECTADOS
        if intruders:
            report.append("🚨 INTRUSOS DETECTADOS")
            report.append("-" * 80)
            
            for i, device in enumerate(intruders, 1):
                report.append(f"\n{i}. {device.hostname.upper()}")
                report.append(f"   IP: {device.ip}")
                report.append(f"   MAC: {device.mac}")
                report.append(f"   Visto por primera vez: {device.first_seen}")
                report.append(f"   Último visto: {device.last_seen}")
                report.append(f"   Paquetes enviados: {device.packets_sent}")
                report.append(f"   Paquetes recibidos: {device.packets_received}")
                report.append(f"   Datos enviados: {device.bytes_sent/1_000_000:.2f}MB")
                report.append(f"   Datos recibidos: {device.bytes_received/1_000_000:.2f}MB")
                
                if device.protocols:
                    report.append(f"   Protocolos usados: {', '.join(device.protocols.keys())}")
                
                if device.ports:
                    report.append(f"   Puertos accedidos: {', '.join(map(str, list(device.ports)[:10]))}")
        
        # DISPOSITIVOS DESCONOCIDOS
        if unknown:
            report.append("\n\n⚠️  DISPOSITIVOS DESCONOCIDOS")
            report.append("-" * 80)
            
            for i, device in enumerate(unknown, 1):
                report.append(f"\n{i}. {device.hostname}")
                report.append(f"   IP: {device.ip}")
                report.append(f"   MAC: {device.mac}")
                report.append(f"   Paquetes: {device.packets_sent + device.packets_received}")
                report.append(f"   Tráfico: {(device.bytes_sent + device.bytes_received)/1_000_000:.2f}MB")
        
        # ANÁLISIS DE TRÁFICO
        report.append("\n\n📈 ANÁLISIS DE TRÁFICO")
        report.append("-" * 80)
        
        stats = self.analyzer.get_stats()
        report.append(f"Total de paquetes: {stats['total_packets']}")
        report.append(f"Total de datos: {stats['total_bytes']/1_000_000:.2f}MB")
        report.append(f"Flujos de tráfico: {stats['unique_flows']}")
        
        if stats['protocols']:
            report.append(f"\nProtocolos utilizados:")
            for protocol, count in sorted(stats['protocols'].items(), key=lambda x: x[1], reverse=True):
                report.append(f"  - {protocol}: {count} paquetes")
        
        # FLUJOS SOSPECHOSOS
        suspicious = self.analyzer.get_suspicious_flows()
        if suspicious:
            report.append("\n\n🚨 FLUJOS SOSPECHOSOS DETECTADOS")
            report.append("-" * 80)
            
            for i, item in enumerate(suspicious, 1):
                flow = item['flow']
                report.append(f"\n{i}. {flow['source']} → {flow['destination']}")
                report.append(f"   Paquetes: {flow['packets']}")
                report.append(f"   Datos: {flow['bytes']/1_000_000:.2f}MB")
                report.append(f"   Nivel de amenaza: {item['threat_level']}")
                
                for reason in item['reasons']:
                    report.append(f"   ⚠️  {reason}")
        
        # RECOMENDACIONES
        report.append("\n\n💡 RECOMENDACIONES")
        report.append("-" * 80)
        
        if intruders:
            report.append("🔴 CRÍTICO:")
            for device in intruders:
                report.append(f"  • Bloquear IP {device.ip} en el router")
                report.append(f"  • Investigar MAC {device.mac}")
        
        if unknown:
            report.append("\n🟡 IMPORTANTE:")
            report.append("  • Revisar dispositivos desconocidos")
            report.append("  • Marcar como confiables o bloquear")
        
        if suspicious:
            report.append("\n🟠 ATENCIÓN:")
            report.append("  • Monitorear flujos sospechosos")
            report.append("  • Implementar reglas de firewall")
        
        report.append("\n" + "="*80 + "\n")
        
        return "\n".join(report)
    
    def generate_json_report(self) -> Dict:
        """Generar reporte en JSON"""
        return {
            'timestamp': str(datetime.now()),
            'summary': {
                'total_devices': len(self.sniffer.devices),
                'trusted_devices': len(self.sniffer.get_trusted_devices()),
                'unknown_devices': len(self.sniffer.get_unknown_devices()),
                'intruders': len(self.sniffer.get_intruders())
            },
            'intruders': [d.to_dict() for d in self.sniffer.get_intruders()],
            'unknown_devices': [d.to_dict() for d in self.sniffer.get_unknown_devices()],
            'traffic_stats': self.analyzer.get_stats(),
            'suspicious_flows': self.analyzer.get_suspicious_flows()
        }
    
    def save_report(self, filename: str, format: str = 'txt'):
        """
        Guardar reporte
        
        Args:
            filename: Nombre del archivo
            format: Formato (txt o json)
        """
        try:
            if format == 'json':
                report = self.generate_json_report()
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
            else:
                report = self.generate_simple_report()
                with open(filename, 'w') as f:
                    f.write(report)
            
            logger.info(f"✅ Reporte guardado: {filename}")
        except Exception as e:
            logger.error(f"❌ Error guardando reporte: {e}")
    
    def print_report(self):
        """Imprimir reporte en consola"""
        print(self.generate_simple_report())


# Ejemplo de uso
if __name__ == '__main__':
    # Crear componentes
    sniffer = NetworkSniffer()
    analyzer = TrafficAnalyzer()
    
    # Escanear red
    sniffer.scan_network()
    
    # Marcar dispositivos
    devices = list(sniffer.devices.values())
    if len(devices) > 0:
        sniffer.mark_trusted(devices[0].ip)
    if len(devices) > 1:
        sniffer.mark_intruder(devices[1].ip)
    
    # Agregar tráfico
    analyzer.add_traffic('192.168.1.100', '192.168.1.50', 'TCP', 22, 50000)
    analyzer.add_traffic('192.168.1.100', '8.8.8.8', 'UDP', 53, 1000)
    
    # Generar reporte
    report_gen = IntruderReport(sniffer, analyzer)
    report_gen.print_report()
    
    # Guardar reportes
    report_gen.save_report('intruder_report.txt', format='txt')
    report_gen.save_report('intruder_report.json', format='json')
