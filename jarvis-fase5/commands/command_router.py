"""
JARVIS FASE 5 - Command Router
Enrutador y ejecutor universal de comandos
"""

import logging
import json
from typing import Dict, Callable, Optional, Any
from datetime import datetime
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/commands.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CommandType(Enum):
    """Tipos de comandos"""
    CONTROL = "control"          # Controlar dispositivo
    QUERY = "query"              # Consultar información
    AUTOMATION = "automation"    # Ejecutar automatización
    SYSTEM = "system"            # Comando del sistema
    CUSTOM = "custom"            # Comando personalizado


class CommandRouter:
    """Enrutador universal de comandos"""
    
    def __init__(self):
        """Inicializar router de comandos"""
        logger.info("🔀 Inicializando Command Router...")
        
        self.handlers: Dict[str, Callable] = {}
        self.command_history: List[Dict] = []
        self.max_history = 1000
        
        # Estadísticas
        self.stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'start_time': str(datetime.now())
        }
        
        logger.info("✅ Command Router inicializado")
    
    def register_handler(self, command_name: str, handler: Callable):
        """
        Registrar manejador de comando
        
        Args:
            command_name: Nombre del comando
            handler: Función que maneja el comando
        """
        self.handlers[command_name.lower()] = handler
        logger.info(f"✅ Manejador registrado: {command_name}")
    
    def execute_command(self, command: str, params: Dict = None, 
                       device_id: str = None) -> Dict[str, Any]:
        """
        Ejecutar comando
        
        Args:
            command: Nombre del comando
            params: Parámetros del comando
            device_id: ID del dispositivo (opcional)
            
        Returns:
            Resultado de la ejecución
        """
        try:
            command_lower = command.lower()
            self.stats['total_commands'] += 1
            
            logger.info(f"⚙️ Ejecutando comando: {command}")
            
            # Buscar manejador
            if command_lower not in self.handlers:
                logger.error(f"❌ Comando no encontrado: {command}")
                self.stats['failed_commands'] += 1
                return {
                    'success': False,
                    'error': f'Comando no encontrado: {command}',
                    'timestamp': str(datetime.now())
                }
            
            # Ejecutar manejador
            handler = self.handlers[command_lower]
            result = handler(params or {}, device_id)
            
            # Registrar en historial
            self._add_to_history(command, params, device_id, result)
            
            if result.get('success', False):
                self.stats['successful_commands'] += 1
                logger.info(f"✅ Comando ejecutado: {command}")
            else:
                self.stats['failed_commands'] += 1
                logger.error(f"❌ Error ejecutando comando: {result.get('error')}")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Excepción ejecutando comando: {e}")
            self.stats['failed_commands'] += 1
            return {
                'success': False,
                'error': str(e),
                'timestamp': str(datetime.now())
            }
    
    def execute_command_sequence(self, commands: list) -> list:
        """
        Ejecutar secuencia de comandos
        
        Args:
            commands: Lista de comandos a ejecutar
            
        Returns:
            Lista de resultados
        """
        results = []
        
        for cmd in commands:
            command = cmd.get('command')
            params = cmd.get('params', {})
            device_id = cmd.get('device_id')
            
            result = self.execute_command(command, params, device_id)
            results.append(result)
            
            # Detener si hay error
            if not result.get('success', False):
                logger.warning("⚠️ Deteniendo secuencia por error")
                break
        
        return results
    
    def _add_to_history(self, command: str, params: Dict, 
                       device_id: str, result: Dict):
        """Agregar comando al historial"""
        history_entry = {
            'command': command,
            'params': params,
            'device_id': device_id,
            'result': result,
            'timestamp': str(datetime.now())
        }
        
        self.command_history.append(history_entry)
        
        # Limitar tamaño del historial
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def get_command_history(self, limit: int = 50) -> list:
        """Obtener historial de comandos"""
        return self.command_history[-limit:]
    
    def clear_history(self):
        """Limpiar historial"""
        self.command_history = []
        logger.info("✅ Historial limpiado")
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return {
            **self.stats,
            'registered_handlers': len(self.handlers),
            'history_size': len(self.command_history),
            'success_rate': (
                self.stats['successful_commands'] / max(self.stats['total_commands'], 1) * 100
            )
        }
    
    def list_available_commands(self) -> list:
        """Listar comandos disponibles"""
        return sorted(list(self.handlers.keys()))


class CommandExecutor:
    """Ejecutor de comandos específicos"""
    
    def __init__(self, discovery):
        """
        Inicializar ejecutor
        
        Args:
            discovery: Sistema de descubrimiento de dispositivos
        """
        self.discovery = discovery
        self.router = CommandRouter()
        
        # Registrar manejadores
        self._register_handlers()
    
    def _register_handlers(self):
        """Registrar manejadores de comandos"""
        
        # Comandos de control
        self.router.register_handler('turn_on', self._handle_turn_on)
        self.router.register_handler('turn_off', self._handle_turn_off)
        self.router.register_handler('toggle', self._handle_toggle)
        self.router.register_handler('set_brightness', self._handle_set_brightness)
        self.router.register_handler('set_temperature', self._handle_set_temperature)
        
        # Comandos de consulta
        self.router.register_handler('get_status', self._handle_get_status)
        self.router.register_handler('get_temperature', self._handle_get_temperature)
        self.router.register_handler('list_devices', self._handle_list_devices)
        
        # Comandos del sistema
        self.router.register_handler('discover_devices', self._handle_discover_devices)
        self.router.register_handler('connect_device', self._handle_connect_device)
        self.router.register_handler('disconnect_device', self._handle_disconnect_device)
        
        logger.info("✅ Manejadores registrados")
    
    # Manejadores de comandos
    
    def _handle_turn_on(self, params: Dict, device_id: str) -> Dict:
        """Encender dispositivo"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            success = self.discovery.send_command_to_device(
                device_id, 'turn_on', params
            )
            
            return {
                'success': success,
                'command': 'turn_on',
                'device_id': device_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_turn_off(self, params: Dict, device_id: str) -> Dict:
        """Apagar dispositivo"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            success = self.discovery.send_command_to_device(
                device_id, 'turn_off', params
            )
            
            return {
                'success': success,
                'command': 'turn_off',
                'device_id': device_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_toggle(self, params: Dict, device_id: str) -> Dict:
        """Alternar dispositivo"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            success = self.discovery.send_command_to_device(
                device_id, 'toggle', params
            )
            
            return {
                'success': success,
                'command': 'toggle',
                'device_id': device_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_set_brightness(self, params: Dict, device_id: str) -> Dict:
        """Establecer brillo"""
        try:
            device_id = params.get('device_id') or device_id
            brightness = params.get('brightness', 50)
            
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            success = self.discovery.send_command_to_device(
                device_id, 'set_brightness', {'brightness': brightness}
            )
            
            return {
                'success': success,
                'command': 'set_brightness',
                'device_id': device_id,
                'brightness': brightness
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_set_temperature(self, params: Dict, device_id: str) -> Dict:
        """Establecer temperatura"""
        try:
            device_id = params.get('device_id') or device_id
            temperature = params.get('temperature', 22)
            
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            success = self.discovery.send_command_to_device(
                device_id, 'set_temperature', {'temperature': temperature}
            )
            
            return {
                'success': success,
                'command': 'set_temperature',
                'device_id': device_id,
                'temperature': temperature
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_get_status(self, params: Dict, device_id: str) -> Dict:
        """Obtener estado del dispositivo"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            device_info = self.discovery.get_device_info(device_id)
            
            return {
                'success': True,
                'command': 'get_status',
                'device_id': device_id,
                'device_info': device_info
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_get_temperature(self, params: Dict, device_id: str) -> Dict:
        """Obtener temperatura"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            # Enviar comando al dispositivo
            self.discovery.send_command_to_device(
                device_id, 'get_temperature', params
            )
            
            return {
                'success': True,
                'command': 'get_temperature',
                'device_id': device_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_list_devices(self, params: Dict, device_id: str) -> Dict:
        """Listar dispositivos"""
        try:
            devices = self.discovery.list_all_devices()
            
            return {
                'success': True,
                'command': 'list_devices',
                'devices': devices,
                'count': len(devices)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_discover_devices(self, params: Dict, device_id: str) -> Dict:
        """Descubrir dispositivos"""
        try:
            devices = self.discovery.discover_all_devices()
            
            return {
                'success': True,
                'command': 'discover_devices',
                'devices': devices
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_connect_device(self, params: Dict, device_id: str) -> Dict:
        """Conectar a dispositivo"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            success = self.discovery.connect_to_device(device_id)
            
            return {
                'success': success,
                'command': 'connect_device',
                'device_id': device_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _handle_disconnect_device(self, params: Dict, device_id: str) -> Dict:
        """Desconectar de dispositivo"""
        try:
            device_id = params.get('device_id') or device_id
            if not device_id:
                return {'success': False, 'error': 'Device ID requerido'}
            
            # Implementar desconexión
            
            return {
                'success': True,
                'command': 'disconnect_device',
                'device_id': device_id
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute(self, command: str, params: Dict = None, device_id: str = None) -> Dict:
        """Ejecutar comando"""
        return self.router.execute_command(command, params, device_id)
    
    def execute_sequence(self, commands: list) -> list:
        """Ejecutar secuencia de comandos"""
        return self.router.execute_command_sequence(commands)
    
    def get_available_commands(self) -> list:
        """Obtener comandos disponibles"""
        return self.router.list_available_commands()
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return self.router.get_stats()
