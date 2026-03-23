"""
JARVIS FASE 5 - MITM Interceptor
Man in the Middle para interceptar y controlar comunicaciones
"""

import logging
import json
import threading
import socket
from typing import Dict, List, Callable, Optional, Tuple
from datetime import datetime
from enum import Enum
import hashlib

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mitm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InterceptionMode(Enum):
    """Modos de interceptación"""
    PASSIVE = "passive"        # Solo monitorear
    ACTIVE = "active"          # Modificar comandos
    BLOCKING = "blocking"      # Bloquear comandos
    INJECTION = "injection"    # Inyectar comandos


class MITMInterceptor:
    """Interceptor Man in the Middle"""
    
    def __init__(self, mode: InterceptionMode = InterceptionMode.PASSIVE):
        """
        Inicializar MITM Interceptor
        
        Args:
            mode: Modo de interceptación
        """
        logger.info(f"🕵️ Inicializando MITM Interceptor (Modo: {mode.value})...")
        
        self.mode = mode
        self.intercepted_traffic: List[Dict] = []
        self.max_traffic_log = 10000
        
        # Reglas de interceptación
        self.rules: Dict[str, Dict] = {}
        
        # Dispositivos bloqueados/permitidos
        self.blacklist: List[str] = []
        self.whitelist: List[str] = []
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            'traffic_intercepted': [],
            'command_modified': [],
            'command_blocked': [],
            'command_injected': [],
            'anomaly_detected': []
        }
        
        # Estadísticas
        self.stats = {
            'total_intercepted': 0,
            'commands_modified': 0,
            'commands_blocked': 0,
            'commands_injected': 0,
            'anomalies_detected': 0,
            'start_time': str(datetime.now())
        }
        
        logger.info("✅ MITM Interceptor inicializado")
    
    def set_mode(self, mode: InterceptionMode):
        """Cambiar modo de interceptación"""
        self.mode = mode
        logger.info(f"🔄 Modo cambiado a: {mode.value}")
    
    def add_rule(self, rule_id: str, rule: Dict):
        """
        Agregar regla de interceptación
        
        Args:
            rule_id: ID único de la regla
            rule: Configuración de la regla
                {
                    'source': 'device_id',
                    'target': 'device_id',
                    'command': 'command_name',
                    'action': 'modify|block|inject',
                    'modification': {...},
                    'enabled': True
                }
        """
        self.rules[rule_id] = rule
        logger.info(f"✅ Regla agregada: {rule_id}")
    
    def remove_rule(self, rule_id: str):
        """Remover regla"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"✅ Regla removida: {rule_id}")
    
    def add_to_blacklist(self, device_id: str):
        """Agregar dispositivo a lista negra"""
        if device_id not in self.blacklist:
            self.blacklist.append(device_id)
            logger.info(f"🚫 Dispositivo agregado a blacklist: {device_id}")
    
    def add_to_whitelist(self, device_id: str):
        """Agregar dispositivo a lista blanca"""
        if device_id not in self.whitelist:
            self.whitelist.append(device_id)
            logger.info(f"✅ Dispositivo agregado a whitelist: {device_id}")
    
    def remove_from_blacklist(self, device_id: str):
        """Remover de lista negra"""
        if device_id in self.blacklist:
            self.blacklist.remove(device_id)
    
    def remove_from_whitelist(self, device_id: str):
        """Remover de lista blanca"""
        if device_id in self.whitelist:
            self.whitelist.remove(device_id)
    
    def intercept_command(self, source: str, target: str, command: str, 
                         params: Dict = None) -> Tuple[bool, Optional[Dict]]:
        """
        Interceptar comando
        
        Args:
            source: Dispositivo origen
            target: Dispositivo destino
            command: Comando
            params: Parámetros
            
        Returns:
            (permitir, comando_modificado)
        """
        try:
            self.stats['total_intercepted'] += 1
            
            # Verificar listas negra/blanca
            if self.whitelist and target not in self.whitelist:
                logger.warning(f"🚫 Dispositivo no en whitelist: {target}")
                self.stats['commands_blocked'] += 1
                self._trigger_callback('command_blocked', {
                    'source': source,
                    'target': target,
                    'command': command,
                    'reason': 'not_in_whitelist'
                })
                return False, None
            
            if target in self.blacklist:
                logger.warning(f"🚫 Dispositivo en blacklist: {target}")
                self.stats['commands_blocked'] += 1
                self._trigger_callback('command_blocked', {
                    'source': source,
                    'target': target,
                    'command': command,
                    'reason': 'in_blacklist'
                })
                return False, None
            
            # Aplicar reglas
            modified_command = {
                'command': command,
                'params': params or {}
            }
            
            for rule_id, rule in self.rules.items():
                if not rule.get('enabled', True):
                    continue
                
                # Verificar si la regla aplica
                if (rule.get('source') == source or rule.get('source') == '*') and \
                   (rule.get('target') == target or rule.get('target') == '*') and \
                   (rule.get('command') == command or rule.get('command') == '*'):
                    
                    action = rule.get('action', 'modify')
                    
                    if action == 'block':
                        logger.warning(f"🚫 Comando bloqueado por regla: {rule_id}")
                        self.stats['commands_blocked'] += 1
                        self._trigger_callback('command_blocked', {
                            'source': source,
                            'target': target,
                            'command': command,
                            'rule': rule_id
                        })
                        return False, None
                    
                    elif action == 'modify':
                        modification = rule.get('modification', {})
                        modified_command['params'].update(modification)
                        self.stats['commands_modified'] += 1
                        logger.info(f"✏️ Comando modificado por regla: {rule_id}")
                        self._trigger_callback('command_modified', {
                            'source': source,
                            'target': target,
                            'command': command,
                            'rule': rule_id,
                            'modification': modification
                        })
                    
                    elif action == 'inject':
                        # Inyectar comando adicional
                        self.stats['commands_injected'] += 1
                        logger.info(f"💉 Comando inyectado por regla: {rule_id}")
                        self._trigger_callback('command_injected', {
                            'source': source,
                            'target': target,
                            'command': command,
                            'rule': rule_id
                        })
            
            # Registrar tráfico
            self._log_traffic(source, target, command, modified_command['params'])
            
            # Detectar anomalías
            self._detect_anomalies(source, target, command, params)
            
            return True, modified_command
        
        except Exception as e:
            logger.error(f"❌ Error interceptando: {e}")
            return True, None
    
    def _log_traffic(self, source: str, target: str, command: str, params: Dict):
        """Registrar tráfico interceptado"""
        traffic_entry = {
            'source': source,
            'target': target,
            'command': command,
            'params': params,
            'timestamp': str(datetime.now()),
            'hash': self._hash_command(source, target, command, params)
        }
        
        self.intercepted_traffic.append(traffic_entry)
        
        # Limitar tamaño del log
        if len(self.intercepted_traffic) > self.max_traffic_log:
            self.intercepted_traffic = self.intercepted_traffic[-self.max_traffic_log:]
    
    def _hash_command(self, source: str, target: str, command: str, params: Dict) -> str:
        """Generar hash de comando"""
        data = f"{source}{target}{command}{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _detect_anomalies(self, source: str, target: str, command: str, params: Dict):
        """Detectar anomalías en el tráfico"""
        try:
            # Anomalía 1: Comandos repetidos rápidamente
            recent_commands = [
                t for t in self.intercepted_traffic[-100:]
                if t['source'] == source and t['command'] == command
            ]
            
            if len(recent_commands) > 10:
                logger.warning(f"⚠️ Anomalía: Comando repetido {len(recent_commands)} veces")
                self.stats['anomalies_detected'] += 1
                self._trigger_callback('anomaly_detected', {
                    'type': 'repeated_command',
                    'source': source,
                    'command': command,
                    'count': len(recent_commands)
                })
            
            # Anomalía 2: Comandos desde dispositivos desconocidos
            known_sources = set(t['source'] for t in self.intercepted_traffic[:-1])
            if source not in known_sources and len(self.intercepted_traffic) > 100:
                logger.warning(f"⚠️ Anomalía: Nuevo dispositivo origen: {source}")
                self.stats['anomalies_detected'] += 1
                self._trigger_callback('anomaly_detected', {
                    'type': 'new_source',
                    'source': source
                })
            
            # Anomalía 3: Comandos a dispositivos desconocidos
            known_targets = set(t['target'] for t in self.intercepted_traffic[:-1])
            if target not in known_targets and len(self.intercepted_traffic) > 100:
                logger.warning(f"⚠️ Anomalía: Nuevo dispositivo destino: {target}")
                self.stats['anomalies_detected'] += 1
                self._trigger_callback('anomaly_detected', {
                    'type': 'new_target',
                    'target': target
                })
        
        except Exception as e:
            logger.error(f"Error detectando anomalías: {e}")
    
    def get_traffic_log(self, limit: int = 100) -> List[Dict]:
        """Obtener log de tráfico"""
        return self.intercepted_traffic[-limit:]
    
    def get_traffic_by_device(self, device_id: str, limit: int = 100) -> List[Dict]:
        """Obtener tráfico de dispositivo específico"""
        traffic = [
            t for t in self.intercepted_traffic
            if t['source'] == device_id or t['target'] == device_id
        ]
        return traffic[-limit:]
    
    def get_traffic_by_command(self, command: str, limit: int = 100) -> List[Dict]:
        """Obtener tráfico de comando específico"""
        traffic = [
            t for t in self.intercepted_traffic
            if t['command'] == command
        ]
        return traffic[-limit:]
    
    def analyze_traffic_patterns(self) -> Dict:
        """Analizar patrones de tráfico"""
        analysis = {
            'total_commands': len(self.intercepted_traffic),
            'unique_sources': len(set(t['source'] for t in self.intercepted_traffic)),
            'unique_targets': len(set(t['target'] for t in self.intercepted_traffic)),
            'unique_commands': len(set(t['command'] for t in self.intercepted_traffic)),
            'command_frequency': {},
            'device_pairs': {}
        }
        
        # Frecuencia de comandos
        for traffic in self.intercepted_traffic:
            cmd = traffic['command']
            analysis['command_frequency'][cmd] = analysis['command_frequency'].get(cmd, 0) + 1
            
            # Pares de dispositivos
            pair = f"{traffic['source']} -> {traffic['target']}"
            analysis['device_pairs'][pair] = analysis['device_pairs'].get(pair, 0) + 1
        
        return analysis
    
    def export_traffic_log(self, filename: str):
        """Exportar log de tráfico a archivo"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.intercepted_traffic, f, indent=2)
            logger.info(f"✅ Log exportado a: {filename}")
        except Exception as e:
            logger.error(f"❌ Error exportando log: {e}")
    
    def clear_traffic_log(self):
        """Limpiar log de tráfico"""
        self.intercepted_traffic = []
        logger.info("✅ Log de tráfico limpiado")
    
    def register_callback(self, event: str, callback: Callable):
        """Registrar callback"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            logger.info(f"✅ Callback registrado: {event}")
    
    def _trigger_callback(self, event: str, data: any):
        """Disparar callbacks"""
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
            'mode': self.mode.value,
            'active_rules': len([r for r in self.rules.values() if r.get('enabled', True)]),
            'blacklisted_devices': len(self.blacklist),
            'whitelisted_devices': len(self.whitelist),
            'traffic_log_size': len(self.intercepted_traffic)
        }
    
    def print_summary(self):
        """Imprimir resumen"""
        print("\n" + "="*60)
        print("🕵️ RESUMEN MITM INTERCEPTOR")
        print("="*60)
        print(f"Modo: {self.mode.value}")
        print(f"Total interceptado: {self.stats['total_intercepted']}")
        print(f"Modificados: {self.stats['commands_modified']}")
        print(f"Bloqueados: {self.stats['commands_blocked']}")
        print(f"Inyectados: {self.stats['commands_injected']}")
        print(f"Anomalías: {self.stats['anomalies_detected']}")
        print(f"Reglas activas: {len([r for r in self.rules.values() if r.get('enabled', True)])}")
        print(f"Dispositivos bloqueados: {len(self.blacklist)}")
        print(f"Dispositivos permitidos: {len(self.whitelist)}")
        print("="*60 + "\n")


# Ejemplo de uso
if __name__ == '__main__':
    # Crear interceptor
    mitm = MITMInterceptor(mode=InterceptionMode.ACTIVE)
    
    # Agregar regla: modificar brillo
    mitm.add_rule('rule_brightness', {
        'source': '*',
        'target': '192.168.1.50',
        'command': 'set_brightness',
        'action': 'modify',
        'modification': {'brightness': 100},  # Siempre al máximo
        'enabled': True
    })
    
    # Agregar regla: bloquear apagado
    mitm.add_rule('rule_block_off', {
        'source': '*',
        'target': '192.168.1.50',
        'command': 'turn_off',
        'action': 'block',
        'enabled': True
    })
    
    # Interceptar comando
    allow, modified = mitm.intercept_command(
        '192.168.1.100',
        '192.168.1.50',
        'set_brightness',
        {'brightness': 50}
    )
    
    print(f"\nPermitido: {allow}")
    print(f"Modificado: {modified}")
    
    # Mostrar resumen
    mitm.print_summary()
    
    # Exportar log
    mitm.export_traffic_log('traffic_log.json')
