"""
JARVIS FASE 5 - API Server
Servidor API para el dashboard
"""

import logging
from flask import Flask, render_template_string, jsonify, request, send_file
from flask_cors import CORS
import json
import os
from datetime import datetime
from remote_control import RemoteControl
from network.network_monitor import NetworkMonitor
import threading

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración
TAILSCALE_API_KEY = os.getenv('TAILSCALE_API_KEY', 'your_api_key')
TAILSCALE_AUTH_KEY = os.getenv('TAILSCALE_AUTH_KEY', 'your_auth_key')

# Instancias globales
remote_control = None
network_monitor = None
chat_history = []

# Inicializar
def init_services():
    global remote_control, network_monitor
    
    try:
        remote_control = RemoteControl('100.64.0.1')  # IP Tailscale por defecto
        logger.info("✅ Remote Control inicializado")
    except Exception as e:
        logger.error(f"❌ Error inicializando Remote Control: {e}")
    
    try:
        network_monitor = NetworkMonitor()
        network_monitor.scan_now()
        logger.info("✅ Network Monitor inicializado")
    except Exception as e:
        logger.error(f"❌ Error inicializando Network Monitor: {e}")


@app.route('/')
def index():
    """Servir dashboard"""
    with open('dashboard.html', 'r') as f:
        return f.read()


# API ENDPOINTS

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Obtener dispositivos conectados"""
    try:
        if network_monitor:
            devices = []
            for ip, device in network_monitor.sniffer.devices.items():
                devices.append({
                    'name': device.hostname,
                    'ip': ip,
                    'mac': device.mac,
                    'status': 'online' if device.last_seen else 'offline'
                })
            
            return jsonify({'success': True, 'devices': devices})
        
        return jsonify({'success': False, 'devices': []})
    except Exception as e:
        logger.error(f"Error obteniendo dispositivos: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/network/wifi', methods=['GET'])
def get_wifi_devices():
    """Obtener dispositivos WiFi"""
    try:
        if network_monitor:
            devices = []
            for device in network_monitor.sniffer.devices.values():
                devices.append({
                    'hostname': device.hostname,
                    'ip': device.ip,
                    'mac': device.mac,
                    'status': 'online'
                })
            
            return jsonify({'success': True, 'devices': devices})
        
        return jsonify({'success': False, 'devices': []})
    except Exception as e:
        logger.error(f"Error obteniendo WiFi: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/network/tailscale', methods=['GET'])
def get_tailscale_devices():
    """Obtener dispositivos Tailscale"""
    try:
        # Simular dispositivos Tailscale
        devices = [
            {
                'name': 'Android Device',
                'ip': '100.64.0.1',
                'status': 'connected'
            },
            {
                'name': 'Raspberry Pi',
                'ip': '100.64.0.2',
                'status': 'connected'
            }
        ]
        
        return jsonify({'success': True, 'devices': devices})
    except Exception as e:
        logger.error(f"Error obteniendo Tailscale: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/command', methods=['POST'])
def execute_command():
    """Ejecutar comando"""
    try:
        data = request.json
        command = data.get('command')
        
        if not remote_control:
            return jsonify({'success': False, 'error': 'Remote control no inicializado'})
        
        # Mapear comandos
        if command == 'info':
            result = remote_control.get_info()
        elif command == 'files':
            result = remote_control.get_files()
        elif command == 'apps':
            result = remote_control.list_apps()
        elif command == 'screenshot':
            result = remote_control.take_screenshot()
        elif command == 'battery':
            result = remote_control.get_info()
        elif command == 'storage':
            result = remote_control.get_info()
        elif command == 'location':
            result = remote_control.get_location()
        elif command == 'network':
            result = remote_control.execute_shell('ifconfig')
        else:
            result = remote_control.execute_shell(command)
        
        return jsonify({
            'success': result.get('success', False),
            'result': str(result.get('result', result.get('error', 'Sin resultado')))[:500]
        })
    
    except Exception as e:
        logger.error(f"Error ejecutando comando: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat con Jarvis"""
    try:
        data = request.json
        message = data.get('message')
        
        # Agregar a historial
        chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': str(datetime.now())
        })
        
        # Simular respuesta de Jarvis
        response = generate_jarvis_response(message)
        
        chat_history.append({
            'role': 'jarvis',
            'content': response,
            'timestamp': str(datetime.now())
        })
        
        return jsonify({
            'success': True,
            'response': response,
            'history': chat_history[-10:]  # Últimos 10 mensajes
        })
    
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        return jsonify({'success': False, 'error': str(e)})


def generate_jarvis_response(message: str) -> str:
    """Generar respuesta de Jarvis"""
    message_lower = message.lower()
    
    # Respuestas predefinidas
    responses = {
        'hola': '¡Hola! Soy Jarvis. ¿Cómo puedo ayudarte?',
        'qué eres': 'Soy JARVIS, tu asistente de control remoto inteligente. Puedo controlar dispositivos, ejecutar comandos y monitorear tu red.',
        'dispositivos': 'Tengo acceso a todos los dispositivos en tu red WiFi y Tailscale. Puedo controlarlos remotamente.',
        'ayuda': 'Puedo: 1) Ejecutar comandos 2) Controlar dispositivos 3) Monitorear red 4) Gestionar archivos 5) Tomar screenshots',
        'estado': 'Sistema funcionando correctamente. Todos los dispositivos están conectados.',
        'red': 'Tu red WiFi tiene 5 dispositivos activos. Tailscale tiene 2 dispositivos conectados.',
    }
    
    # Buscar coincidencia
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    # Respuesta por defecto
    return f'Entendido: "{message}". ¿Hay algo específico que necesites?'


@app.route('/api/terminal', methods=['POST'])
def terminal():
    """Ejecutar comando en terminal"""
    try:
        data = request.json
        cmd = data.get('cmd')
        
        if not remote_control:
            return jsonify({'success': False, 'error': 'Remote control no inicializado'})
        
        result = remote_control.execute_shell(cmd)
        
        return jsonify({
            'success': result.get('success', False),
            'output': result.get('result', result.get('error', ''))
        })
    
    except Exception as e:
        logger.error(f"Error en terminal: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/status', methods=['GET'])
def get_status():
    """Obtener estado general"""
    try:
        devices_count = len(network_monitor.sniffer.devices) if network_monitor else 0
        
        return jsonify({
            'success': True,
            'status': 'online',
            'devices': devices_count,
            'timestamp': str(datetime.now()),
            'uptime': '24h 30m'
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': str(datetime.now())})


if __name__ == '__main__':
    logger.info("🚀 Iniciando API Server...")
    
    # Inicializar servicios
    init_services()
    
    # Iniciar servidor
    logger.info("📡 Servidor escuchando en http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
