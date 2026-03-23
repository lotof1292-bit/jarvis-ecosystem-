"""
JARVIS FASE 5 - MITM Integration
Integración de MITM con el controlador principal
"""

import logging
from typing import Dict, Optional
from mitm_interceptor import MITMInterceptor, InterceptionMode

logger = logging.getLogger(__name__)


class MITMController:
    """Controlador MITM integrado"""
    
    def __init__(self, executor):
        """
        Inicializar controlador MITM
        
        Args:
            executor: Ejecutor de comandos principal
        """
        self.executor = executor
        self.mitm = MITMInterceptor(mode=InterceptionMode.ACTIVE)
        self.enabled = True
        
        logger.info("✅ MITM Controller inicializado")
    
    def execute_with_mitm(self, command: str, params: Dict = None, 
                         device_id: str = None) -> Dict:
        """
        Ejecutar comando con interceptación MITM
        
        Args:
            command: Comando a ejecutar
            params: Parámetros
            device_id: ID del dispositivo
            
        Returns:
            Resultado de ejecución
        """
        if not self.enabled:
            # Si MITM está deshabilitado, ejecutar normalmente
            return self.executor.execute(command, params, device_id)
        
        try:
            # Interceptar comando
            source = 'jarvis'  # Origen es siempre Jarvis
            target = device_id or 'unknown'
            
            allow, modified = self.mitm.intercept_command(
                source, target, command, params
            )
            
            if not allow:
                # Comando bloqueado
                return {
                    'success': False,
                    'error': 'Comando bloqueado por MITM',
                    'blocked': True
                }
            
            # Usar comando modificado si existe
            if modified:
                command = modified.get('command', command)
                params = modified.get('params', params)
            
            # Ejecutar comando
            result = self.executor.execute(command, params, device_id)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error en ejecución MITM: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def enable_mitm(self):
        """Habilitar MITM"""
        self.enabled = True
        logger.info("✅ MITM habilitado")
    
    def disable_mitm(self):
        """Deshabilitar MITM"""
        self.enabled = False
        logger.info("⏹️ MITM deshabilitado")
    
    def set_mode(self, mode: InterceptionMode):
        """Cambiar modo MITM"""
        self.mitm.set_mode(mode)
        logger.info(f"🔄 Modo MITM cambiado a: {mode.value}")
    
    def add_rule(self, rule_id: str, rule: Dict):
        """Agregar regla MITM"""
        self.mitm.add_rule(rule_id, rule)
    
    def remove_rule(self, rule_id: str):
        """Remover regla MITM"""
        self.mitm.remove_rule(rule_id)
    
    def list_rules(self) -> Dict:
        """Listar reglas activas"""
        return self.mitm.rules
    
    def add_to_blacklist(self, device_id: str):
        """Agregar dispositivo a blacklist"""
        self.mitm.add_to_blacklist(device_id)
    
    def add_to_whitelist(self, device_id: str):
        """Agregar dispositivo a whitelist"""
        self.mitm.add_to_whitelist(device_id)
    
    def remove_from_blacklist(self, device_id: str):
        """Remover de blacklist"""
        self.mitm.remove_from_blacklist(device_id)
    
    def remove_from_whitelist(self, device_id: str):
        """Remover de whitelist"""
        self.mitm.remove_from_whitelist(device_id)
    
    def get_blacklist(self) -> list:
        """Obtener blacklist"""
        return self.mitm.blacklist
    
    def get_whitelist(self) -> list:
        """Obtener whitelist"""
        return self.mitm.whitelist
    
    def get_traffic_log(self, limit: int = 100) -> list:
        """Obtener log de tráfico"""
        return self.mitm.get_traffic_log(limit)
    
    def get_traffic_by_device(self, device_id: str, limit: int = 100) -> list:
        """Obtener tráfico de dispositivo"""
        return self.mitm.get_traffic_by_device(device_id, limit)
    
    def get_traffic_by_command(self, command: str, limit: int = 100) -> list:
        """Obtener tráfico de comando"""
        return self.mitm.get_traffic_by_command(command, limit)
    
    def analyze_patterns(self) -> Dict:
        """Analizar patrones de tráfico"""
        return self.mitm.analyze_traffic_patterns()
    
    def export_traffic(self, filename: str):
        """Exportar log de tráfico"""
        self.mitm.export_traffic_log(filename)
    
    def clear_traffic_log(self):
        """Limpiar log de tráfico"""
        self.mitm.clear_traffic_log()
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas MITM"""
        return self.mitm.get_stats()
    
    def print_summary(self):
        """Imprimir resumen"""
        print(f"\n{'='*60}")
        print("🕵️ MITM CONTROLLER - RESUMEN")
        print(f"{'='*60}")
        print(f"Estado: {'✅ HABILITADO' if self.enabled else '⏹️ DESHABILITADO'}")
        self.mitm.print_summary()


# Ejemplo de uso
if __name__ == '__main__':
    from commands.command_router import CommandExecutor
    from discovery.device_discovery import DeviceDiscovery
    
    # Crear componentes
    discovery = DeviceDiscovery()
    executor = CommandExecutor(discovery)
    
    # Crear controlador MITM
    mitm_controller = MITMController(executor)
    
    # Agregar regla: modificar brillo
    mitm_controller.add_rule('rule_brightness', {
        'source': '*',
        'target': '*',
        'command': 'set_brightness',
        'action': 'modify',
        'modification': {'brightness': 100},
        'enabled': True
    })
    
    # Agregar regla: bloquear apagado
    mitm_controller.add_rule('rule_block_off', {
        'source': '*',
        'target': '*',
        'command': 'turn_off',
        'action': 'block',
        'enabled': True
    })
    
    # Ejecutar comando con MITM
    result = mitm_controller.execute_with_mitm(
        'set_brightness',
        {'brightness': 50, 'device_id': '192.168.1.50'},
        '192.168.1.50'
    )
    
    print(f"\nResultado: {result}")
    
    # Mostrar resumen
    mitm_controller.print_summary()
