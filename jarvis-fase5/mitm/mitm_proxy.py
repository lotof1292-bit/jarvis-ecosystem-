"""
JARVIS FASE 5 - MITM Proxy Server
Servidor proxy para interceptar tráfico WiFi
"""

import logging
import json
import threading
import socket
from typing import Dict, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

from mitm_interceptor import MITMInterceptor, InterceptionMode

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mitm_proxy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MITMProxyHandler(BaseHTTPRequestHandler):
    """Manejador de proxy MITM"""
    
    # Referencia al interceptor (se asigna en la clase)
    interceptor: Optional[MITMInterceptor] = None
    
    def do_GET(self):
        """Manejar peticiones GET"""
        self._handle_request('GET')
    
    def do_POST(self):
        """Manejar peticiones POST"""
        self._handle_request('POST')
    
    def do_PUT(self):
        """Manejar peticiones PUT"""
        self._handle_request('PUT')
    
    def _handle_request(self, method: str):
        """Manejar petición"""
        try:
            # Obtener información
            source = self.client_address[0]
            path = self.path
            
            # Parsear comando
            parsed = urllib.parse.urlparse(path)
            params = urllib.parse.parse_qs(parsed.query)
            
            # Obtener body si existe
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            try:
                body_data = json.loads(body.decode('utf-8')) if body else {}
            except:
                body_data = {}
            
            # Extraer comando y parámetros
            command = body_data.get('command', parsed.path.split('/')[-1])
            params = body_data.get('params', body_data)
            target = body_data.get('target', self.headers.get('X-Target', 'unknown'))
            
            logger.info(f"📨 Petición: {source} -> {target} : {command}")
            
            # Interceptar
            if self.interceptor:
                allow, modified = self.interceptor.intercept_command(
                    source, target, command, params
                )
                
                if not allow:
                    # Comando bloqueado
                    self.send_response(403)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'error': 'Comando bloqueado por MITM'}
                    self.wfile.write(json.dumps(response).encode())
                    logger.warning(f"🚫 Comando bloqueado: {command}")
                    return
                
                # Comando permitido (posiblemente modificado)
                if modified:
                    command = modified.get('command', command)
                    params = modified.get('params', params)
            
            # Responder
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                'success': True,
                'command': command,
                'params': params,
                'intercepted': self.interceptor is not None,
                'timestamp': str(datetime.now())
            }
            
            self.wfile.write(json.dumps(response).encode())
            logger.info(f"✅ Respuesta enviada: {command}")
        
        except Exception as e:
            logger.error(f"❌ Error manejando petición: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Suprimir logs por defecto"""
        pass


class MITMProxyServer:
    """Servidor proxy MITM"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8888):
        """
        Inicializar servidor proxy
        
        Args:
            host: Host del servidor
            port: Puerto del servidor
        """
        logger.info(f"🔧 Inicializando MITM Proxy Server en {host}:{port}...")
        
        self.host = host
        self.port = port
        self.interceptor = MITMInterceptor(mode=InterceptionMode.ACTIVE)
        self.server = None
        self.thread = None
        
        # Asignar interceptor al manejador
        MITMProxyHandler.interceptor = self.interceptor
        
        logger.info("✅ MITM Proxy Server inicializado")
    
    def start(self):
        """Iniciar servidor"""
        try:
            logger.info(f"🚀 Iniciando servidor proxy en {self.host}:{self.port}...")
            
            self.server = HTTPServer((self.host, self.port), MITMProxyHandler)
            
            # Ejecutar en thread
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            
            logger.info(f"✅ Servidor proxy iniciado en http://{self.host}:{self.port}")
        
        except Exception as e:
            logger.error(f"❌ Error iniciando servidor: {e}")
    
    def stop(self):
        """Detener servidor"""
        if self.server:
            self.server.shutdown()
            logger.info("✅ Servidor proxy detenido")
    
    def add_rule(self, rule_id: str, rule: Dict):
        """Agregar regla"""
        self.interceptor.add_rule(rule_id, rule)
    
    def remove_rule(self, rule_id: str):
        """Remover regla"""
        self.interceptor.remove_rule(rule_id)
    
    def add_to_blacklist(self, device_id: str):
        """Agregar a blacklist"""
        self.interceptor.add_to_blacklist(device_id)
    
    def add_to_whitelist(self, device_id: str):
        """Agregar a whitelist"""
        self.interceptor.add_to_whitelist(device_id)
    
    def get_traffic_log(self, limit: int = 100):
        """Obtener log de tráfico"""
        return self.interceptor.get_traffic_log(limit)
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas"""
        return self.interceptor.get_stats()
    
    def print_summary(self):
        """Imprimir resumen"""
        self.interceptor.print_summary()


# Ejemplo de uso
if __name__ == '__main__':
    # Crear servidor
    proxy = MITMProxyServer(host='0.0.0.0', port=8888)
    
    # Agregar reglas
    proxy.add_rule('rule_brightness', {
        'source': '*',
        'target': '*',
        'command': 'set_brightness',
        'action': 'modify',
        'modification': {'brightness': 100},
        'enabled': True
    })
    
    proxy.add_rule('rule_block_off', {
        'source': '*',
        'target': '*',
        'command': 'turn_off',
        'action': 'block',
        'enabled': True
    })
    
    # Iniciar servidor
    proxy.start()
    
    # Mantener servidor activo
    try:
        print("\n🔧 Servidor proxy MITM activo...")
        print("Presiona Ctrl+C para detener\n")
        
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n👋 Deteniendo servidor...")
        proxy.stop()
