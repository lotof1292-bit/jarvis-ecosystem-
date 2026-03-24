"""
JARVIS FASE 5 - Tailscale Deep Link Generator
Generador de deep links para setup "click 0" con Tailscale
"""

import logging
import json
import base64
import qrcode
from typing import Dict, Optional
from datetime import datetime
import urllib.parse

logger = logging.getLogger(__name__)


class TailscaleDeepLink:
    """Generador de deep links para Tailscale"""
    
    def __init__(self, tailscale_api_key: str, tailscale_auth_key: str):
        """
        Inicializar generador
        
        Args:
            tailscale_api_key: API Key de Tailscale
            tailscale_auth_key: Auth Key de Tailscale
        """
        logger.info("🔗 Inicializando Tailscale Deep Link Generator...")
        
        self.api_key = tailscale_api_key
        self.auth_key = tailscale_auth_key
        self.base_url = "https://login.tailscale.com/a"
        
        logger.info("✅ Tailscale Deep Link Generator inicializado")
    
    def generate_android_deeplink(self, device_name: str = "jarvis-android",
                                  tags: list = None) -> str:
        """
        Generar deep link para Android
        
        Args:
            device_name: Nombre del dispositivo
            tags: Tags para el dispositivo
            
        Returns:
            Deep link para Android
        """
        try:
            # Parámetros
            params = {
                'authkey': self.auth_key,
                'device_name': device_name,
                'tags': ','.join(tags or ['tag:android', 'tag:remote']),
                'os': 'android'
            }
            
            # Crear deep link
            deeplink = f"tailscale://login?{urllib.parse.urlencode(params)}"
            
            logger.info(f"✅ Deep link generado para Android")
            return deeplink
        
        except Exception as e:
            logger.error(f"❌ Error generando deep link: {e}")
            return None
    
    def generate_termux_install_link(self, server_url: str) -> str:
        """
        Generar link para instalar Termux
        
        Args:
            server_url: URL del servidor de instalación
            
        Returns:
            Link de instalación
        """
        try:
            # Play Store link
            termux_link = "https://play.google.com/store/apps/details?id=com.termux"
            
            # Crear link con redirección
            redirect_link = f"{server_url}/install/termux?redirect={urllib.parse.quote(termux_link)}"
            
            logger.info(f"✅ Link de instalación de Termux generado")
            return redirect_link
        
        except Exception as e:
            logger.error(f"❌ Error generando link: {e}")
            return None
    
    def generate_tailscale_install_link(self, server_url: str) -> str:
        """
        Generar link para instalar Tailscale
        
        Args:
            server_url: URL del servidor
            
        Returns:
            Link de instalación
        """
        try:
            # Play Store link
            tailscale_link = "https://play.google.com/store/apps/details?id=com.tailscale.ipn"
            
            # Crear link con redirección
            redirect_link = f"{server_url}/install/tailscale?redirect={urllib.parse.quote(tailscale_link)}"
            
            logger.info(f"✅ Link de instalación de Tailscale generado")
            return redirect_link
        
        except Exception as e:
            logger.error(f"❌ Error generando link: {e}")
            return None
    
    def generate_setup_script(self, device_name: str = "jarvis-android") -> str:
        """
        Generar script de setup para Termux
        
        Args:
            device_name: Nombre del dispositivo
            
        Returns:
            Script bash
        """
        script = f"""#!/bin/bash

# JARVIS FASE 5 - Termux Auto Setup
# Setup automático de Tailscale y Jarvis

echo "🚀 Iniciando setup automático..."

# Actualizar paquetes
apt update && apt upgrade -y

# Instalar dependencias
apt install -y python3 python3-pip curl wget git openssh

# Instalar Tailscale
echo "📥 Instalando Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# Conectar a Tailscale
echo "🔗 Conectando a Tailscale..."
tailscale up --authkey={self.auth_key} --hostname={device_name}

# Clonar repositorio de Jarvis
echo "📦 Descargando Jarvis..."
cd ~
git clone https://github.com/lotof1292-bit/jarvis-ecosystem-.git
cd jarvis-ecosystem/jarvis-fase5

# Instalar dependencias de Python
pip install -r requirements.txt

# Crear servicio de Jarvis
echo "⚙️  Configurando servicio..."
cat > ~/.termux/startup.sh << 'EOF'
#!/bin/bash
cd ~/jarvis-ecosystem/jarvis-fase5
python3 remote/termux_agent.py
EOF

chmod +x ~/.termux/startup.sh

echo "✅ Setup completado!"
echo "🔗 Dispositivo conectado a Tailscale"
echo "📡 Jarvis listo para recibir comandos"
"""
        
        return script
    
    def generate_qr_code(self, deeplink: str, filename: str = "tailscale_qr.png"):
        """
        Generar código QR
        
        Args:
            deeplink: Deep link a codificar
            filename: Nombre del archivo
        """
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(deeplink)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(filename)
            
            logger.info(f"✅ Código QR generado: {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"❌ Error generando QR: {e}")
            return None
    
    def generate_html_page(self, server_url: str, device_name: str = "jarvis-android") -> str:
        """
        Generar página HTML con setup automático
        
        Args:
            server_url: URL del servidor
            device_name: Nombre del dispositivo
            
        Returns:
            HTML page
        """
        deeplink = self.generate_android_deeplink(device_name)
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 JARVIS - Setup Remoto</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
            padding: 40px;
            text-align: center;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        
        .steps {{
            text-align: left;
            margin: 30px 0;
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
        }}
        
        .step {{
            margin: 15px 0;
            padding: 15px;
            background: white;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        
        .step-number {{
            font-weight: bold;
            color: #667eea;
            font-size: 1.2em;
        }}
        
        .step-text {{
            color: #333;
            margin-top: 5px;
        }}
        
        .button-group {{
            display: flex;
            gap: 10px;
            margin-top: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        
        .btn {{
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-secondary {{
            background: #f0f0f0;
            color: #333;
            border: 2px solid #667eea;
        }}
        
        .btn-secondary:hover {{
            background: #667eea;
            color: white;
        }}
        
        .qr-code {{
            margin: 30px 0;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 10px;
        }}
        
        .qr-code img {{
            max-width: 300px;
            border-radius: 10px;
        }}
        
        .info-box {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
            color: #1565c0;
        }}
        
        .success {{
            background: #e8f5e9;
            border-left-color: #4caf50;
            color: #2e7d32;
        }}
        
        .warning {{
            background: #fff3e0;
            border-left-color: #ff9800;
            color: #e65100;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 JARVIS REMOTO</h1>
        <p class="subtitle">Setup automático en 1 click</p>
        
        <div class="info-box warning">
            ⚠️ Asegúrate de estar en tu celular de trabajo
        </div>
        
        <div class="steps">
            <div class="step">
                <span class="step-number">1️⃣ Instalar Termux</span>
                <div class="step-text">
                    Descarga e instala Termux desde Play Store
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">2️⃣ Instalar Tailscale</span>
                <div class="step-text">
                    Descarga e instala Tailscale desde Play Store
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">3️⃣ Conectar a Tailscale</span>
                <div class="step-text">
                    Toca el botón de abajo para conectarte automáticamente
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">4️⃣ Ejecutar Setup</span>
                <div class="step-text">
                    Abre Termux y ejecuta el script de instalación
                </div>
            </div>
        </div>
        
        <div class="qr-code">
            <p style="color: #666; margin-bottom: 15px;">Escanea para conectar a Tailscale:</p>
            <img src="{server_url}/qr/tailscale.png" alt="QR Code">
        </div>
        
        <div class="info-box success">
            ✅ Una vez conectado, podrás controlar tu celular desde tu PI o Windows
        </div>
        
        <div class="button-group">
            <a href="{deeplink}" class="btn btn-primary">
                🔗 Conectar a Tailscale
            </a>
            <a href="{server_url}/script/setup.sh" class="btn btn-secondary">
                📥 Descargar Script
            </a>
        </div>
        
        <p style="color: #999; margin-top: 30px; font-size: 0.9em;">
            Dispositivo: {device_name}
        </p>
    </div>
    
    <script>
        // Detectar si es Android
        if (!navigator.userAgent.toLowerCase().includes('android')) {{
            alert('⚠️ Este link debe abrirse en un celular Android');
        }}
    </script>
</body>
</html>
"""
        
        return html


# Ejemplo de uso
if __name__ == '__main__':
    # Crear generador
    generator = TailscaleDeepLink(
        tailscale_api_key="your_api_key",
        tailscale_auth_key="your_auth_key"
    )
    
    # Generar deep link
    deeplink = generator.generate_android_deeplink("jarvis-android")
    print(f"Deep Link: {deeplink}")
    
    # Generar QR
    generator.generate_qr_code(deeplink)
    
    # Generar script
    script = generator.generate_setup_script()
    with open('setup.sh', 'w') as f:
        f.write(script)
    
    # Generar HTML
    html = generator.generate_html_page("http://localhost:8000")
    with open('setup.html', 'w') as f:
        f.write(html)
    
    print("✅ Setup completado")
