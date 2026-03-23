"""
JARVIS FASE 5 - Remote Control Client
Cliente para controlar dispositivos Android remotamente
"""

import logging
import json
import socket
import subprocess
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RemoteControl:
    """Cliente de control remoto"""
    
    def __init__(self, device_ip: str, device_port: int = 5555):
        """
        Inicializar cliente
        
        Args:
            device_ip: IP del dispositivo (Tailscale)
            device_port: Puerto del dispositivo
        """
        logger.info(f"🎮 Inicializando Remote Control para {device_ip}...")
        
        self.device_ip = device_ip
        self.device_port = device_port
        
        logger.info("✅ Remote Control inicializado")
    
    def send_command(self, command: str, params: Dict = None) -> Dict:
        """
        Enviar comando al dispositivo
        
        Args:
            command: Comando a ejecutar
            params: Parámetros del comando
            
        Returns:
            Resultado del comando
        """
        try:
            # Construir datos
            data = {
                'command': command,
                'params': params or {},
                'timestamp': str(datetime.now())
            }
            
            # Conectar y enviar
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.device_ip, self.device_port))
            sock.send(json.dumps(data).encode())
            
            # Recibir respuesta
            response = sock.recv(8192).decode()
            sock.close()
            
            result = json.loads(response)
            logger.info(f"✅ Comando ejecutado: {command}")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Error enviando comando: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_shell(self, cmd: str) -> Dict:
        """Ejecutar comando shell"""
        return self.send_command('shell', {'cmd': cmd})
    
    def get_files(self, path: str = None) -> Dict:
        """Listar archivos"""
        return self.send_command('get_files', {'path': path})
    
    def get_file(self, filepath: str) -> Dict:
        """Descargar archivo"""
        return self.send_command('get_file', {'filepath': filepath})
    
    def get_info(self) -> Dict:
        """Obtener información del dispositivo"""
        return self.send_command('get_info')
    
    def take_screenshot(self) -> Dict:
        """Tomar screenshot"""
        return self.send_command('screenshot')
    
    def get_clipboard(self) -> Dict:
        """Obtener contenido del portapapeles"""
        return self.send_command('get_clipboard')
    
    def set_clipboard(self, text: str) -> Dict:
        """Establecer contenido del portapapeles"""
        return self.send_command('set_clipboard', {'text': text})
    
    def install_app(self, app_url: str) -> Dict:
        """Instalar aplicación"""
        cmd = f"curl -o /sdcard/app.apk {app_url} && pm install /sdcard/app.apk"
        return self.execute_shell(cmd)
    
    def uninstall_app(self, package_name: str) -> Dict:
        """Desinstalar aplicación"""
        cmd = f"pm uninstall {package_name}"
        return self.execute_shell(cmd)
    
    def list_apps(self) -> Dict:
        """Listar aplicaciones instaladas"""
        cmd = "pm list packages"
        return self.execute_shell(cmd)
    
    def open_app(self, package_name: str) -> Dict:
        """Abrir aplicación"""
        cmd = f"am start -n {package_name}/.MainActivity"
        return self.execute_shell(cmd)
    
    def send_sms(self, phone: str, message: str) -> Dict:
        """Enviar SMS"""
        cmd = f"termux-sms-send -n {phone} '{message}'"
        return self.execute_shell(cmd)
    
    def make_call(self, phone: str) -> Dict:
        """Hacer llamada"""
        cmd = f"am start -a android.intent.action.CALL -d tel:{phone}"
        return self.execute_shell(cmd)
    
    def get_location(self) -> Dict:
        """Obtener ubicación"""
        cmd = "termux-location"
        return self.execute_shell(cmd)
    
    def get_contacts(self) -> Dict:
        """Obtener contactos"""
        cmd = "termux-contact-list"
        return self.execute_shell(cmd)
    
    def record_audio(self, duration: int = 10) -> Dict:
        """Grabar audio"""
        cmd = f"termux-microphone-record -f /sdcard/recording.wav -d {duration}"
        return self.execute_shell(cmd)
    
    def play_audio(self, filepath: str) -> Dict:
        """Reproducir audio"""
        cmd = f"termux-media-player play {filepath}"
        return self.execute_shell(cmd)
    
    def print_status(self):
        """Imprimir estado"""
        result = self.get_info()
        
        if result['success']:
            info = result['result']
            print("\n" + "="*60)
            print("📱 DISPOSITIVO REMOTO - ESTADO")
            print("="*60)
            print(f"Dispositivo: {info.get('device_name')}")
            print(f"IP: {info.get('device_ip')}")
            print(f"Uptime: {info.get('uptime')}")
            print(f"Batería: {info.get('battery')}")
            print(f"Almacenamiento: {info.get('storage')}")
            print("="*60 + "\n")
        else:
            print(f"❌ Error: {result.get('error')}")


# Ejemplo de uso
if __name__ == '__main__':
    # Crear cliente
    remote = RemoteControl('100.64.0.1')  # IP de Tailscale del dispositivo
    
    # Obtener información
    info = remote.get_info()
    print(f"Info: {info}")
    
    # Ejecutar comando
    result = remote.execute_shell('ls -la')
    print(f"Resultado: {result}")
    
    # Mostrar estado
    remote.print_status()
