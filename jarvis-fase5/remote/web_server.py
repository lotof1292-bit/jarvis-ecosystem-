"""
JARVIS FASE 5 - Remote Web Server
Servidor web para hosting de setup y deep links
"""

import logging
from flask import Flask, render_template_string, send_file, request
from remote_control import RemoteControl
from tailscale_deeplink import TailscaleDeepLink
import os

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración
TAILSCALE_API_KEY = os.getenv('TAILSCALE_API_KEY', 'your_api_key')
TAILSCALE_AUTH_KEY = os.getenv('TAILSCALE_AUTH_KEY', 'your_auth_key')


@app.route('/')
def index():
    """Página principal"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 JARVIS Remote Control</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px 5px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                cursor: pointer;
            }
            .button:hover { background: #764ba2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 JARVIS Remote Control</h1>
            <p>Controla tu dispositivo Android remotamente</p>
            
            <h2>Opciones:</h2>
            <a href="/setup" class="button">🔧 Setup Automático</a>
            <a href="/control" class="button">🎮 Panel de Control</a>
            <a href="/api" class="button">📡 API</a>
        </div>
    </body>
    </html>
    """)


@app.route('/setup')
def setup():
    """Página de setup"""
    generator = TailscaleDeepLink(TAILSCALE_API_KEY, TAILSCALE_AUTH_KEY)
    html = generator.generate_html_page(request.base_url.rstrip('/setup'))
    return html


@app.route('/control')
def control():
    """Panel de control"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎮 Panel de Control</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: 20px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .control-panel {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin-top: 20px;
            }
            .control-item {
                padding: 20px;
                background: #f9f9f9;
                border-radius: 5px;
                border-left: 4px solid #667eea;
            }
            .control-item h3 { margin-top: 0; }
            input, button {
                padding: 8px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 3px;
                width: 100%;
            }
            button {
                background: #667eea;
                color: white;
                cursor: pointer;
                border: none;
            }
            button:hover { background: #764ba2; }
            .output {
                background: #f0f0f0;
                padding: 10px;
                border-radius: 3px;
                margin-top: 10px;
                max-height: 200px;
                overflow-y: auto;
                font-family: monospace;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎮 Panel de Control Remoto</h1>
            
            <div class="control-panel">
                <div class="control-item">
                    <h3>📱 Información del Dispositivo</h3>
                    <button onclick="getInfo()">Obtener Info</button>
                    <div id="info-output" class="output"></div>
                </div>
                
                <div class="control-item">
                    <h3>⚙️ Ejecutar Comando</h3>
                    <input type="text" id="cmd" placeholder="Comando shell">
                    <button onclick="executeCmd()">Ejecutar</button>
                    <div id="cmd-output" class="output"></div>
                </div>
                
                <div class="control-item">
                    <h3>📁 Listar Archivos</h3>
                    <input type="text" id="path" placeholder="/sdcard" value="/sdcard">
                    <button onclick="listFiles()">Listar</button>
                    <div id="files-output" class="output"></div>
                </div>
                
                <div class="control-item">
                    <h3>📸 Screenshot</h3>
                    <button onclick="takeScreenshot()">Tomar Screenshot</button>
                    <div id="screenshot-output" class="output"></div>
                </div>
                
                <div class="control-item">
                    <h3>📋 Portapapeles</h3>
                    <button onclick="getClipboard()">Obtener</button>
                    <input type="text" id="clipboard" placeholder="Nuevo contenido">
                    <button onclick="setClipboard()">Establecer</button>
                    <div id="clipboard-output" class="output"></div>
                </div>
                
                <div class="control-item">
                    <h3>📱 Aplicaciones</h3>
                    <button onclick="listApps()">Listar Apps</button>
                    <input type="text" id="package" placeholder="com.example.app">
                    <button onclick="openApp()">Abrir App</button>
                    <div id="apps-output" class="output"></div>
                </div>
            </div>
        </div>
        
        <script>
            const API_URL = '/api/command';
            
            async function sendCommand(command, params = {}) {
                try {
                    const response = await fetch(API_URL, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command, params })
                    });
                    return await response.json();
                } catch (e) {
                    return { success: false, error: e.message };
                }
            }
            
            async function getInfo() {
                const result = await sendCommand('get_info');
                document.getElementById('info-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function executeCmd() {
                const cmd = document.getElementById('cmd').value;
                const result = await sendCommand('shell', { cmd });
                document.getElementById('cmd-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function listFiles() {
                const path = document.getElementById('path').value;
                const result = await sendCommand('get_files', { path });
                document.getElementById('files-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function takeScreenshot() {
                const result = await sendCommand('screenshot');
                document.getElementById('screenshot-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function getClipboard() {
                const result = await sendCommand('get_clipboard');
                document.getElementById('clipboard-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function setClipboard() {
                const text = document.getElementById('clipboard').value;
                const result = await sendCommand('set_clipboard', { text });
                document.getElementById('clipboard-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function listApps() {
                const result = await sendCommand('shell', { cmd: 'pm list packages' });
                document.getElementById('apps-output').textContent = JSON.stringify(result, null, 2);
            }
            
            async function openApp() {
                const pkg = document.getElementById('package').value;
                const result = await sendCommand('shell', { cmd: `am start -n ${pkg}/.MainActivity` });
                document.getElementById('apps-output').textContent = JSON.stringify(result, null, 2);
            }
        </script>
    </body>
    </html>
    """)


@app.route('/api/command', methods=['POST'])
def api_command():
    """API para enviar comandos"""
    data = request.json
    command = data.get('command')
    params = data.get('params', {})
    device_ip = data.get('device_ip', '100.64.0.1')
    
    try:
        remote = RemoteControl(device_ip)
        result = remote.send_command(command, params)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}


@app.route('/script/setup.sh')
def download_setup_script():
    """Descargar script de setup"""
    generator = TailscaleDeepLink(TAILSCALE_API_KEY, TAILSCALE_AUTH_KEY)
    script = generator.generate_setup_script()
    
    with open('/tmp/setup.sh', 'w') as f:
        f.write(script)
    
    return send_file('/tmp/setup.sh', as_attachment=True, download_name='setup.sh')


@app.route('/qr/<filename>')
def get_qr(filename):
    """Obtener código QR"""
    filepath = f'/tmp/{filename}'
    if os.path.exists(filepath):
        return send_file(filepath)
    return 'QR not found', 404


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8000, debug=True)
