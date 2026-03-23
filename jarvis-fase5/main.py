"""
JARVIS FASE 5 - MAIN ORCHESTRATOR
Control Total por Bluetooth + WiFi
"""

import logging
import json
import os
from typing import Dict, Optional
from datetime import datetime

from discovery.device_discovery import DeviceDiscovery
from commands.command_router import CommandExecutor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jarvis_fase5.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisFase5:
    """Orquestador principal de FASE 5"""
    
    def __init__(self, config_path: str = 'config/fase5_config.json'):
        """
        Inicializar FASE 5
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        logger.info("🚀 Inicializando JARVIS FASE 5...")
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Inicializar componentes
        self.discovery = DeviceDiscovery()
        self.executor = CommandExecutor(self.discovery)
        
        # Estadísticas
        self.stats = {
            'start_time': str(datetime.now()),
            'devices_discovered': 0,
            'commands_executed': 0
        }
        
        logger.info("✅ JARVIS FASE 5 inicializado")
    
    def _load_config(self, config_path: str) -> Dict:
        """Cargar configuración"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"⚠️ Archivo de config no encontrado: {config_path}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error cargando config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Obtener configuración por defecto"""
        return {
            'bluetooth_enabled': True,
            'wifi_enabled': True,
            'auto_discover': True,
            'discovery_interval': 60,
            'network_prefix': '192.168.1'
        }
    
    def discover_devices(self) -> Dict:
        """Descubrir todos los dispositivos"""
        try:
            logger.info("🔍 Descubriendo dispositivos...")
            devices = self.discovery.discover_all_devices()
            self.stats['devices_discovered'] = len(self.discovery.all_devices)
            
            logger.info(f"✅ {len(self.discovery.all_devices)} dispositivos encontrados")
            return devices
        
        except Exception as e:
            logger.error(f"❌ Error descubriendo: {e}")
            return {}
    
    def execute_command(self, command: str, params: Dict = None, 
                       device_id: str = None) -> Dict:
        """Ejecutar comando"""
        try:
            result = self.executor.execute(command, params, device_id)
            self.stats['commands_executed'] += 1
            return result
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando comando: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_sequence(self, commands: list) -> list:
        """Ejecutar secuencia de comandos"""
        try:
            results = self.executor.execute_sequence(commands)
            self.stats['commands_executed'] += len(commands)
            return results
        
        except Exception as e:
            logger.error(f"❌ Error ejecutando secuencia: {e}")
            return []
    
    def list_devices(self, device_type: str = None) -> list:
        """Listar dispositivos"""
        if device_type:
            return self.discovery.get_devices_by_type(device_type)
        else:
            return self.discovery.list_all_devices()
    
    def get_device_info(self, device_id: str) -> Optional[Dict]:
        """Obtener información de dispositivo"""
        return self.discovery.get_device_info(device_id)
    
    def connect_device(self, device_id: str) -> bool:
        """Conectar a dispositivo"""
        return self.discovery.connect_to_device(device_id)
    
    def interactive_mode(self):
        """Modo interactivo"""
        logger.info("🎤 Entrando en modo interactivo...")
        print("\n" + "="*60)
        print("🤖 JARVIS FASE 5 - CONTROL TOTAL")
        print("="*60)
        print("Comandos disponibles:")
        print("  discover       - Descubrir dispositivos")
        print("  list           - Listar dispositivos")
        print("  connect <id>   - Conectar a dispositivo")
        print("  on <id>        - Encender dispositivo")
        print("  off <id>       - Apagar dispositivo")
        print("  toggle <id>    - Alternar dispositivo")
        print("  brightness <id> <value> - Establecer brillo")
        print("  temp <id> <value> - Establecer temperatura")
        print("  status <id>    - Obtener estado")
        print("  commands       - Ver comandos disponibles")
        print("  stats          - Ver estadísticas")
        print("  salir          - Salir")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("jarvis> ").strip()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == 'salir':
                    print("\n👋 ¡Hasta luego!")
                    break
                
                elif command == 'discover':
                    print("\n🔍 Descubriendo dispositivos...")
                    devices = self.discover_devices()
                    self.discovery.print_summary()
                
                elif command == 'list':
                    devices = self.list_devices()
                    print(f"\n📱 {len(devices)} dispositivos encontrados:")
                    for device in devices:
                        status = "✅" if device['connected'] else "⭕"
                        print(f"  {status} {device['name']} ({device['identifier']})")
                
                elif command == 'connect':
                    if len(parts) < 2:
                        print("❌ Uso: connect <device_id>")
                        continue
                    
                    device_id = parts[1]
                    if self.connect_device(device_id):
                        print(f"✅ Conectado a {device_id}")
                    else:
                        print(f"❌ Error conectando a {device_id}")
                
                elif command == 'on':
                    if len(parts) < 2:
                        print("❌ Uso: on <device_id>")
                        continue
                    
                    device_id = parts[1]
                    result = self.execute_command('turn_on', {'device_id': device_id})
                    if result['success']:
                        print(f"✅ {device_id} encendido")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                
                elif command == 'off':
                    if len(parts) < 2:
                        print("❌ Uso: off <device_id>")
                        continue
                    
                    device_id = parts[1]
                    result = self.execute_command('turn_off', {'device_id': device_id})
                    if result['success']:
                        print(f"✅ {device_id} apagado")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                
                elif command == 'toggle':
                    if len(parts) < 2:
                        print("❌ Uso: toggle <device_id>")
                        continue
                    
                    device_id = parts[1]
                    result = self.execute_command('toggle', {'device_id': device_id})
                    if result['success']:
                        print(f"✅ {device_id} alternado")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                
                elif command == 'brightness':
                    if len(parts) < 3:
                        print("❌ Uso: brightness <device_id> <value>")
                        continue
                    
                    device_id = parts[1]
                    brightness = int(parts[2])
                    result = self.execute_command('set_brightness', 
                                                 {'device_id': device_id, 'brightness': brightness})
                    if result['success']:
                        print(f"✅ Brillo establecido a {brightness}%")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                
                elif command == 'temp':
                    if len(parts) < 3:
                        print("❌ Uso: temp <device_id> <value>")
                        continue
                    
                    device_id = parts[1]
                    temperature = float(parts[2])
                    result = self.execute_command('set_temperature',
                                                 {'device_id': device_id, 'temperature': temperature})
                    if result['success']:
                        print(f"✅ Temperatura establecida a {temperature}°C")
                    else:
                        print(f"❌ Error: {result.get('error')}")
                
                elif command == 'status':
                    if len(parts) < 2:
                        print("❌ Uso: status <device_id>")
                        continue
                    
                    device_id = parts[1]
                    result = self.execute_command('get_status', {'device_id': device_id})
                    if result['success']:
                        print(f"\n📊 Estado de {device_id}:")
                        print(json.dumps(result['device_info'], indent=2))
                    else:
                        print(f"❌ Error: {result.get('error')}")
                
                elif command == 'commands':
                    commands = self.executor.get_available_commands()
                    print(f"\n📋 Comandos disponibles ({len(commands)}):")
                    for cmd in commands:
                        print(f"  - {cmd}")
                
                elif command == 'stats':
                    stats = self.executor.get_stats()
                    print(f"\n📊 Estadísticas:")
                    print(f"  Total de comandos: {stats['total_commands']}")
                    print(f"  Exitosos: {stats['successful_commands']}")
                    print(f"  Fallidos: {stats['failed_commands']}")
                    print(f"  Tasa de éxito: {stats['success_rate']:.1f}%")
                    print(f"  Manejadores registrados: {stats['registered_handlers']}")
                
                else:
                    print(f"❌ Comando no reconocido: {command}")
            
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"❌ Error: {e}\n")
    
    def get_status(self) -> Dict:
        """Obtener estado del sistema"""
        return {
            'status': 'running',
            'stats': self.stats,
            'devices': len(self.discovery.all_devices),
            'connected_devices': len(self.discovery.get_connected_devices()),
            'available_commands': len(self.executor.get_available_commands())
        }


def main():
    """Función principal"""
    try:
        # Crear directorio de logs
        os.makedirs('logs', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        # Inicializar FASE 5
        jarvis = JarvisFase5()
        
        # Modo interactivo
        jarvis.interactive_mode()
    
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
