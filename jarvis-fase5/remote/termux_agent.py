"""
JARVIS FASE 5 - Termux Agent
Agente en Termux para recibir y ejecutar comandos desde Jarvis
"""

import logging
import json
import subprocess
import socket
import os
from typing import Dict, Optional
from datetime import datetime
import threading
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jarvis_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TermuxAgent:
    """Agente de Termux para ejecutar comandos remotos"""
    
    def __init__(self, server_ip: str = None, server_port: int = 5555):
        """
        Inicializar agente
        
        Args:
            server_ip: IP del servidor Jarvis
            server_port: Puerto del servidor
        """
        logger.info("🤖 Inicializando Termux Agent...")
        
        self.server_ip = server_ip or self._get_tailscale_ip()
        self.server_port = server_port
        self.device_name = self._get_device_name()
        self.running = False
        
        # Estadísticas
        self.stats = {
            'commands_received': 0,
            'commands_executed': 0,
            'commands_failed': 0,
            'start_time': str(datetime.now())
        }
        
        logger.info(f"✅ Termux Agent inicializado")
        logger.info(f"   Dispositivo: {self.device_name}")
        logger.info(f"   Servidor: {self.server_ip}:{self.server_port}")
    
    def _get_tailscale_ip(self) -> str:
        """Obtener IP de Tailscale"""
        try:
            result = subprocess.run(
                ['tailscale', 'ip'],
                capture_output=True,
                text=True
            )
            
            ips = result.stdout.strip().split('\n')
            return ips[0] if ips else '127.0.0.1'
        except:
            return '127.0.0.1'
    
    def _get_device_name(self) -> str:
        """Obtener nombre del dispositivo"""
        try:
            result = subprocess.run(
                ['getprop', 'ro.product.model'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip() or 'Android Device'
        except:
            return 'Android Device'
    
    def register_with_server(self) -> bool:
        """Registrarse con el servidor Jarvis"""
        try:
            logger.info(f"📡 Registrando con servidor {self.server_ip}...")
            
            data = {
                'action': 'register',
                'device_name': self.device_name,
                'device_ip': self._get_tailscale_ip(),
                'timestamp': str(datetime.now())
            }
            
            # Enviar registro
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.server_ip, self.server_port))
            sock.send(json.dumps(data).encode())
            sock.close()
            
            logger.info("✅ Registrado con servidor")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error registrando: {e}")
            return False
    
    def listen_for_commands(self):
        """Escuchar comandos del servidor"""
        try:
            logger.info(f"👂 Escuchando comandos en puerto {self.server_port}...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', self.server_port))
            sock.listen(5)
            
            self.running = True
            
            while self.running:
                try:
                    client, addr = sock.accept()
                    logger.info(f"📨 Conexión desde {addr}")
                    
                    # Recibir datos
                    data = client.recv(4096).decode()
                    
                    if data:
                        command_data = json.loads(data)
                        self._handle_command(command_data, client)
                    
                    client.close()
                
                except Exception as e:
                    logger.error(f"Error procesando conexión: {e}")
            
            sock.close()
        
        except Exception as e:
            logger.error(f"❌ Error escuchando: {e}")
    
    def _handle_command(self, command_data: Dict, client: socket.socket):
        """Manejar comando recibido"""
        try:
            command = command_data.get('command')
            params = command_data.get('params', {})
            
            logger.info(f"⚙️  Ejecutando comando: {command}")
            self.stats['commands_received'] += 1
            
            # Ejecutar comando
            result = self._execute_command(command, params)
            
            # Enviar resultado
            response = {
                'success': result['success'],
                'command': command,
                'result': result.get('result'),
                'error': result.get('error'),
                'timestamp': str(datetime.now())
            }
            
            client.send(json.dumps(response).encode())
            
            if result['success']:
                self.stats['commands_executed'] += 1
                logger.info(f"✅ Comando ejecutado: {command}")
            else:
                self.stats['commands_failed'] += 1
                logger.error(f"❌ Error ejecutando comando: {result.get('error')}")
        
        except Exception as e:
            logger.error(f"❌ Error manejando comando: {e}")
            response = {
                'success': False,
                'error': str(e)
            }
            client.send(json.dumps(response).encode())
    
    def _execute_command(self, command: str, params: Dict) -> Dict:
        """Ejecutar comando en Termux"""
        try:
            if command == 'shell':
                # Ejecutar comando shell
                cmd = params.get('cmd', '')
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    'success': result.returncode == 0,
                    'result': result.stdout,
                    'error': result.stderr
                }
            
            elif command == 'get_files':
                # Listar archivos
                path = params.get('path', os.path.expanduser('~'))
                files = os.listdir(path)
                
                return {
                    'success': True,
                    'result': files
                }
            
            elif command == 'get_file':
                # Descargar archivo
                filepath = params.get('filepath')
                
                if not os.path.exists(filepath):
                    return {
                        'success': False,
                        'error': 'Archivo no encontrado'
                    }
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                return {
                    'success': True,
                    'result': content
                }
            
            elif command == 'get_info':
                # Obtener información del dispositivo
                info = {
                    'device_name': self.device_name,
                    'device_ip': self._get_tailscale_ip(),
                    'uptime': self._get_uptime(),
                    'storage': self._get_storage_info(),
                    'battery': self._get_battery_info()
                }
                
                return {
                    'success': True,
                    'result': info
                }
            
            elif command == 'screenshot':
                # Tomar screenshot
                result = subprocess.run(
                    ['screencap', '-p', '/sdcard/screenshot.png'],
                    capture_output=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {
                        'success': True,
                        'result': '/sdcard/screenshot.png'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No se pudo tomar screenshot'
                    }
            
            elif command == 'get_clipboard':
                # Obtener contenido del portapapeles
                result = subprocess.run(
                    ['termux-clipboard-get'],
                    capture_output=True,
                    text=True
                )
                
                return {
                    'success': result.returncode == 0,
                    'result': result.stdout
                }
            
            elif command == 'set_clipboard':
                # Establecer contenido del portapapeles
                text = params.get('text', '')
                
                result = subprocess.run(
                    ['termux-clipboard-set'],
                    input=text.encode(),
                    capture_output=True
                )
                
                return {
                    'success': result.returncode == 0
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Comando desconocido: {command}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_uptime(self) -> str:
        """Obtener uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        except:
            return "Unknown"
    
    def _get_storage_info(self) -> Dict:
        """Obtener información de almacenamiento"""
        try:
            result = subprocess.run(
                ['df', '/sdcard'],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    'total': parts[1],
                    'used': parts[2],
                    'available': parts[3]
                }
        except:
            pass
        
        return {}
    
    def _get_battery_info(self) -> Dict:
        """Obtener información de batería"""
        try:
            result = subprocess.run(
                ['dumpsys', 'battery'],
                capture_output=True,
                text=True
            )
            
            info = {}
            for line in result.stdout.split('\n'):
                if 'level' in line.lower():
                    info['level'] = line.split(':')[-1].strip()
                elif 'temperature' in line.lower():
                    info['temperature'] = line.split(':')[-1].strip()
            
            return info
        except:
            pass
        
        return {}
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return self.stats
    
    def print_status(self):
        """Imprimir estado"""
        print("\n" + "="*60)
        print("🤖 TERMUX AGENT - ESTADO")
        print("="*60)
        print(f"Dispositivo: {self.device_name}")
        print(f"IP Tailscale: {self._get_tailscale_ip()}")
        print(f"Puerto: {self.server_port}")
        print(f"Estado: {'🟢 ACTIVO' if self.running else '🔴 INACTIVO'}")
        print(f"\n📊 Estadísticas:")
        print(f"  Comandos recibidos: {self.stats['commands_received']}")
        print(f"  Comandos ejecutados: {self.stats['commands_executed']}")
        print(f"  Comandos fallidos: {self.stats['commands_failed']}")
        print("="*60 + "\n")


def main():
    """Función principal"""
    try:
        # Crear agente
        agent = TermuxAgent()
        
        # Registrarse con servidor
        agent.register_with_server()
        
        # Mostrar estado
        agent.print_status()
        
        # Escuchar comandos
        agent.listen_for_commands()
    
    except KeyboardInterrupt:
        logger.info("\n👋 Agente detenido")
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
