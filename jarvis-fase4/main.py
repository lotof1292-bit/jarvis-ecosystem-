"""
JARVIS FASE 4 - MAIN ORCHESTRATOR
Sistema híbrido de inteligencia: Local + Manus
"""

import logging
import json
import os
from typing import Dict, Optional
from datetime import datetime

from chat.local_chat_engine import LocalChatEngine
from chat.complexity_detector import ComplexityDetector, ComplexityLevel
from chat.manus_connector import ManusConnector

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/jarvis_fase4.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisFase4:
    """Orquestador principal de FASE 4"""
    
    def __init__(self, config_path: str = 'config/fase4_config.json'):
        """
        Inicializar FASE 4
        
        Args:
            config_path: Ruta al archivo de configuración
        """
        logger.info("🚀 Inicializando JARVIS FASE 4...")
        
        # Cargar configuración
        self.config = self._load_config(config_path)
        
        # Inicializar componentes
        self.local_chat = LocalChatEngine(
            model=self.config.get('local_model', 'mistral:7b'),
            ollama_url=self.config.get('ollama_url', 'http://localhost:11434')
        )
        
        self.complexity_detector = ComplexityDetector(
            threshold_moderate=self.config.get('threshold_moderate', 0.4),
            threshold_advanced=self.config.get('threshold_advanced', 0.7)
        )
        
        self.manus_connector = ManusConnector(
            api_url=self.config.get('manus_url', 'https://api.manus.im'),
            api_key=self.config.get('manus_api_key'),
            cache_ttl=self.config.get('cache_ttl', 3600)
        )
        
        # Estadísticas
        self.stats = {
            'total_queries': 0,
            'local_queries': 0,
            'manus_queries': 0,
            'cache_hits': 0,
            'start_time': str(datetime.now())
        }
        
        logger.info("✅ JARVIS FASE 4 inicializado correctamente")
    
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
            'local_model': 'mistral:7b',
            'ollama_url': 'http://localhost:11434',
            'manus_url': 'https://api.manus.im',
            'manus_api_key': None,
            'threshold_moderate': 0.4,
            'threshold_advanced': 0.7,
            'cache_ttl': 3600,
            'offline_mode': True
        }
    
    def process_query(self, message: str, context: str = "") -> Dict:
        """
        Procesar consulta del usuario
        
        Args:
            message: Mensaje del usuario
            context: Contexto adicional
            
        Returns:
            Dict con respuesta
        """
        try:
            logger.info(f"📨 Procesando: {message[:50]}...")
            
            # 1. Detectar complejidad
            level, score, details = self.complexity_detector.detect(message, context)
            logger.info(f"📊 Complejidad: {level.name} (score: {score:.2f})")
            
            # 2. Obtener recomendación
            recommendation = self.complexity_detector.get_recommendation(level)
            
            # 3. Procesar según nivel
            response = None
            source = None
            
            if level == ComplexityLevel.SIMPLE:
                # Intentar caché primero
                response = self.local_chat.chat(message, use_context=True)
                source = 'local'
                self.stats['local_queries'] += 1
            
            elif level == ComplexityLevel.MODERATE:
                # Usar Ollama local
                response = self.local_chat.chat(message, use_context=True)
                source = 'local'
                self.stats['local_queries'] += 1
            
            elif level == ComplexityLevel.ADVANCED:
                # Intentar Manus, fallback a local
                def fallback(msg, ctx):
                    result = self.local_chat.chat(msg, use_context=True)
                    return result.get('response', 'Error procesando')
                
                manus_response = self.manus_connector.query(
                    message, 
                    context,
                    fallback_fn=fallback
                )
                
                response = {
                    'success': manus_response['success'],
                    'response': manus_response.get('response', ''),
                    'complexity': level.name
                }
                source = manus_response.get('source', 'unknown')
                
                if source == 'manus':
                    self.stats['manus_queries'] += 1
                elif source == 'cache':
                    self.stats['cache_hits'] += 1
            
            # 4. Actualizar estadísticas
            self.stats['total_queries'] += 1
            
            # 5. Construir respuesta final
            final_response = {
                'success': response.get('success', False),
                'response': response.get('response', ''),
                'complexity': {
                    'level': level.name,
                    'score': score,
                    'details': details
                },
                'source': source,
                'recommendation': recommendation,
                'timestamp': str(datetime.now())
            }
            
            logger.info(f"✅ Respuesta generada desde {source}")
            return final_response
        
        except Exception as e:
            logger.error(f"❌ Error procesando query: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Error procesando tu consulta'
            }
    
    def interactive_mode(self):
        """Modo interactivo de chat"""
        logger.info("🎤 Entrando en modo interactivo...")
        print("\n" + "="*60)
        print("🤖 JARVIS FASE 4 - INTELIGENCIA HÍBRIDA")
        print("="*60)
        print("Escribe 'salir' para terminar")
        print("Escribe 'stats' para ver estadísticas")
        print("Escribe 'historia' para ver historial")
        print("="*60 + "\n")
        
        while True:
            try:
                user_input = input("jarvis> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'salir':
                    print("\n👋 ¡Hasta luego!")
                    break
                
                elif user_input.lower() == 'stats':
                    self._show_stats()
                
                elif user_input.lower() == 'historia':
                    self._show_history()
                
                else:
                    # Procesar consulta
                    result = self.process_query(user_input)
                    
                    print(f"\n💬 {result['response']}")
                    print(f"📊 Complejidad: {result['complexity']['level']} | Fuente: {result['source']}")
                    print()
            
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                logger.error(f"Error en modo interactivo: {e}")
                print(f"❌ Error: {e}\n")
    
    def _show_stats(self):
        """Mostrar estadísticas"""
        print("\n" + "="*60)
        print("📊 ESTADÍSTICAS")
        print("="*60)
        print(f"Total de consultas: {self.stats['total_queries']}")
        print(f"Consultas locales: {self.stats['local_queries']}")
        print(f"Consultas a Manus: {self.stats['manus_queries']}")
        print(f"Hits de caché: {self.stats['cache_hits']}")
        print(f"Inicio: {self.stats['start_time']}")
        
        # Estadísticas de componentes
        print("\n🔹 Local Chat:")
        local_stats = self.local_chat.get_stats()
        print(f"  - Mensajes: {local_stats.get('total_messages', 0)}")
        print(f"  - Modelo: {local_stats.get('model', 'N/A')}")
        
        print("\n🔹 Manus Connector:")
        manus_stats = self.manus_connector.get_stats()
        print(f"  - Disponible: {manus_stats.get('manus_available', False)}")
        print(f"  - Tasa de éxito: {manus_stats.get('success_rate', 0)}%")
        print(f"  - Items en caché: {manus_stats.get('cache_stats', {}).get('cache_size', 0)}")
        
        print("="*60 + "\n")
    
    def _show_history(self):
        """Mostrar historial de conversación"""
        print("\n" + "="*60)
        print("📜 HISTORIAL DE CONVERSACIÓN")
        print("="*60)
        
        history = self.local_chat.get_history(limit=10)
        
        if not history:
            print("No hay historial")
        else:
            for i, msg in enumerate(history, 1):
                role = "👤 Usuario" if msg['role'] == 'user' else "🤖 Jarvis"
                content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
                print(f"{i}. {role}: {content}")
        
        print("="*60 + "\n")
    
    def get_status(self) -> Dict:
        """Obtener estado del sistema"""
        return {
            'local_chat_available': self.local_chat.ollama_available,
            'manus_available': self.manus_connector.available,
            'stats': self.stats,
            'local_stats': self.local_chat.get_stats(),
            'manus_stats': self.manus_connector.get_stats()
        }


def main():
    """Función principal"""
    try:
        # Crear directorio de logs
        os.makedirs('logs', exist_ok=True)
        os.makedirs('config', exist_ok=True)
        
        # Inicializar FASE 4
        jarvis = JarvisFase4()
        
        # Modo interactivo
        jarvis.interactive_mode()
    
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}")
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()
