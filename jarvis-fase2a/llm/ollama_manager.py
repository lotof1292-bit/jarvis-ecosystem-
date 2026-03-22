"""
OLLAMA MANAGER - Gestión de LLM local
Integración con Ollama para procesamiento de lenguaje natural
"""

import requests
import json
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class OllamaManager:
    """Gestor de Ollama para LLM local"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.host = config.get('ollama_host', 'http://localhost:11434')
        self.model = config.get('llm_model', 'mistral:7b')
        self.is_running = False
        self.check_ollama()
    
    def check_ollama(self):
        """Verificar si Ollama está disponible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            if response.status_code == 200:
                self.is_running = True
                logger.info(f"✅ Ollama disponible en {self.host}")
                self.ensure_model()
            else:
                logger.warning("⚠️ Ollama no responde correctamente")
        except Exception as e:
            logger.warning(f"⚠️ Ollama no disponible: {e}")
            logger.info("💡 Instala Ollama desde https://ollama.ai")
    
    def ensure_model(self):
        """Asegurar que el modelo esté descargado"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if self.model not in model_names:
                logger.info(f"📥 Descargando modelo {self.model}...")
                self.pull_model()
            else:
                logger.info(f"✅ Modelo {self.model} disponible")
        
        except Exception as e:
            logger.error(f"❌ Error verificando modelo: {e}")
    
    def pull_model(self):
        """Descargar modelo"""
        try:
            response = requests.post(
                f"{self.host}/api/pull",
                json={"name": self.model},
                stream=True,
                timeout=300
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'status' in data:
                        logger.info(f"📥 {data['status']}")
            
            logger.info(f"✅ Modelo {self.model} descargado")
        
        except Exception as e:
            logger.error(f"❌ Error descargando modelo: {e}")
    
    def process(self, prompt: str, context: Optional[str] = None) -> str:
        """Procesar prompt con LLM"""
        if not self.is_running:
            return "❌ Ollama no está disponible. Instálalo desde https://ollama.ai"
        
        try:
            # Preparar prompt con contexto
            full_prompt = prompt
            if context:
                full_prompt = f"{context}\n\n{prompt}"
            
            # Llamar a Ollama
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"❌ Error de Ollama: {response.status_code}")
                return "Error procesando solicitud"
        
        except requests.Timeout:
            logger.error("❌ Timeout esperando respuesta de Ollama")
            return "Timeout: Ollama tardó demasiado en responder"
        except Exception as e:
            logger.error(f"❌ Error procesando: {e}")
            return f"Error: {str(e)}"
    
    def stream_response(self, prompt: str):
        """Procesar prompt con streaming"""
        if not self.is_running:
            yield "❌ Ollama no está disponible"
            return
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": True,
                    "temperature": 0.7
                },
                stream=True,
                timeout=60
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get('response', '')
                    if token:
                        yield token
        
        except Exception as e:
            logger.error(f"❌ Error en streaming: {e}")
            yield f"Error: {str(e)}"
    
    def get_status(self) -> Dict:
        """Obtener estado de Ollama"""
        return {
            'running': self.is_running,
            'host': self.host,
            'model': self.model,
            'status': '✅ Disponible' if self.is_running else '❌ No disponible'
        }
