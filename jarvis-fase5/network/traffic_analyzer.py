"""
JARVIS FASE 5 - Traffic Analyzer
Analizador de tráfico para ver qué hacen los intrusos
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class TrafficFlow:
    """Flujo de tráfico entre dispositivos"""
    
    def __init__(self, source: str, destination: str):
        self.source = source
        self.destination = destination
        self.packets = 0
        self.bytes = 0
        self.protocols = defaultdict(int)
        self.ports = defaultdict(int)
        self.first_seen = str(datetime.now())
        self.last_seen = str(datetime.now())
    
    def to_dict(self) -> Dict:
        return {
            'source': self.source,
            'destination': self.destination,
            'packets': self.packets,
            'bytes': self.bytes,
            'protocols': dict(self.protocols),
            'ports': dict(self.ports),
            'first_seen': self.first_seen,
            'last_seen': self.last_seen
        }


class TrafficAnalyzer:
    """Analizador de tráfico de red"""
    
    def __init__(self):
        """Inicializar analizador"""
        logger.info("📊 Inicializando Traffic Analyzer...")
        
        self.flows: Dict[str, TrafficFlow] = {}
        self.protocol_stats = defaultdict(int)
        self.port_stats = defaultdict(int)
        
        # Estadísticas
        self.stats = {
            'total_packets': 0,
            'total_bytes': 0,
            'unique_flows': 0,
            'start_time': str(datetime.now())
        }
        
        logger.info("✅ Traffic Analyzer inicializado")
    
    def add_traffic(self, source: str, destination: str, protocol: str, 
                   port: int, bytes_count: int):
        """
        Agregar tráfico
        
        Args:
            source: IP origen
            destination: IP destino
            protocol: Protocolo (TCP, UDP, ICMP, etc.)
            port: Puerto
            bytes_count: Bytes transferidos
        """
        # Crear clave de flujo
        flow_key = f"{source} -> {destination}"
        
        # Crear flujo si no existe
        if flow_key not in self.flows:
            self.flows[flow_key] = TrafficFlow(source, destination)
            self.stats['unique_flows'] = len(self.flows)
        
        flow = self.flows[flow_key]
        flow.packets += 1
        flow.bytes += bytes_count
        flow.protocols[protocol] += 1
        if port:
            flow.ports[port] += 1
        flow.last_seen = str(datetime.now())
        
        # Estadísticas globales
        self.stats['total_packets'] += 1
        self.stats['total_bytes'] += bytes_count
        self.protocol_stats[protocol] += 1
        if port:
            self.port_stats[port] += 1
    
    def get_device_traffic(self, ip: str) -> Dict:
        """Obtener tráfico de dispositivo"""
        outgoing = []
        incoming = []
        
        for flow_key, flow in self.flows.items():
            if flow.source == ip:
                outgoing.append(flow.to_dict())
            elif flow.destination == ip:
                incoming.append(flow.to_dict())
        
        return {
            'ip': ip,
            'outgoing': outgoing,
            'incoming': incoming,
            'total_outgoing_bytes': sum(f['bytes'] for f in outgoing),
            'total_incoming_bytes': sum(f['bytes'] for f in incoming)
        }
    
    def get_suspicious_flows(self) -> List[Dict]:
        """Obtener flujos sospechosos"""
        suspicious = []
        
        for flow_key, flow in self.flows.items():
            # Criterios de sospecha
            is_suspicious = False
            reasons = []
            
            # Muchos paquetes
            if flow.packets > 1000:
                is_suspicious = True
                reasons.append(f"Muchos paquetes ({flow.packets})")
            
            # Mucho tráfico
            if flow.bytes > 100_000_000:  # 100MB
                is_suspicious = True
                reasons.append(f"Mucho tráfico ({flow.bytes/1_000_000:.1f}MB)")
            
            # Puertos sospechosos
            suspicious_ports = [22, 23, 3389, 445, 139, 135]
            for port in suspicious_ports:
                if port in flow.ports:
                    is_suspicious = True
                    reasons.append(f"Puerto sospechoso ({port})")
            
            if is_suspicious:
                suspicious.append({
                    'flow': flow.to_dict(),
                    'reasons': reasons,
                    'threat_level': 'ALTO' if flow.packets > 5000 else 'MEDIO'
                })
        
        return suspicious
    
    def get_protocol_summary(self) -> Dict:
        """Obtener resumen de protocolos"""
        return dict(self.protocol_stats)
    
    def get_port_summary(self) -> Dict:
        """Obtener resumen de puertos"""
        return dict(self.port_stats)
    
    def get_top_flows(self, limit: int = 10) -> List[Dict]:
        """Obtener flujos principales"""
        sorted_flows = sorted(
            self.flows.values(),
            key=lambda f: f.bytes,
            reverse=True
        )
        
        return [f.to_dict() for f in sorted_flows[:limit]]
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return {
            **self.stats,
            'protocols': dict(self.protocol_stats),
            'top_ports': dict(sorted(self.port_stats.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def print_summary(self):
        """Imprimir resumen"""
        print("\n" + "="*70)
        print("📊 TRAFFIC ANALYZER - RESUMEN")
        print("="*70)
        
        print(f"\n📈 ESTADÍSTICAS GLOBALES:")
        print(f"  Total de paquetes: {self.stats['total_packets']}")
        print(f"  Total de bytes: {self.stats['total_bytes']/1_000_000:.2f}MB")
        print(f"  Flujos únicos: {self.stats['unique_flows']}")
        
        print(f"\n🔌 PROTOCOLOS UTILIZADOS:")
        for protocol, count in sorted(self.protocol_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {protocol}: {count} paquetes")
        
        print(f"\n🔗 PUERTOS PRINCIPALES:")
        for port, count in sorted(self.port_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - Puerto {port}: {count} paquetes")
        
        print(f"\n⚠️ FLUJOS PRINCIPALES:")
        for flow in self.get_top_flows(5):
            print(f"  - {flow['source']} -> {flow['destination']}: {flow['bytes']/1_000_000:.2f}MB")
        
        print(f"\n🚨 FLUJOS SOSPECHOSOS:")
        suspicious = self.get_suspicious_flows()
        if suspicious:
            for item in suspicious[:5]:
                flow = item['flow']
                print(f"  - {flow['source']} -> {flow['destination']}")
                for reason in item['reasons']:
                    print(f"    • {reason}")
        else:
            print("  Ninguno detectado")
        
        print("\n" + "="*70 + "\n")


# Ejemplo de uso
if __name__ == '__main__':
    analyzer = TrafficAnalyzer()
    
    # Agregar tráfico de ejemplo
    analyzer.add_traffic('192.168.1.100', '192.168.1.50', 'TCP', 80, 5000)
    analyzer.add_traffic('192.168.1.100', '192.168.1.50', 'TCP', 80, 3000)
    analyzer.add_traffic('192.168.1.100', '8.8.8.8', 'UDP', 53, 1000)
    analyzer.add_traffic('192.168.1.101', '192.168.1.50', 'TCP', 22, 10000)
    
    # Mostrar resumen
    analyzer.print_summary()
    
    # Analizar dispositivo
    device_traffic = analyzer.get_device_traffic('192.168.1.100')
    print(f"\n📊 Tráfico de 192.168.1.100:")
    print(json.dumps(device_traffic, indent=2))
