"""
LOCAL CHAT ENGINE - Sistema de chat local con Ollama
Conversación natural, historial de contexto, respuestas rápidas
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import deque
import requests

logger = logging.getLogger(__name__)


class LocalChatEngine:
    """Motor de chat local usando Ollama"""
    
    def __init__(self, 
                 model: str = "mistral:7b",
                 ollama_url: str = "http://localhost:11434",
                 max_history: int = 20,
                 context_window: int = 4096):
        """
        Inicializar motor de chat local
        
        Args:
            model: Modelo de Ollama a usar
            ollama_url: URL del servidor Ollama
            max_history: Máximo de mensajes en historial
            context_window: Tamaño de ventana de contexto
        """
        self.model = model
        self.ollama_url = ollama_url
        self.max_history = max_history
        self.context_window = context_window
        
        # Historial de conversación
        self.conversation_history = deque(maxlen=max_history)
        
        # Información del usuario
        self.user_context = {
            'name': 'Usuario',
            'preferences': {},
            'history': []
        }
        
        # Verificar disponibilidad de Ollama
        self.ollama_available = self._check_ollama()
        
        logger.info(f"✅ Local Chat Engine inicializado (Modelo: {model})")
    
    def _check_ollama(self) -> bool:
        """Verificar si Ollama está disponible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️ Ollama no disponible: {e}")
            return False
    
    def chat(self, message: str, use_context: bool = True) -> Dict:
        """
        Procesar mensaje del usuario y generar respuesta
        
        Args:
            message: Mensaje del usuario
            use_context: Usar historial de conversación
            
        Returns:
            Dict con respuesta y metadatos
        """
        try:
            if not self.ollama_available:
                return {
                    'success': False,
                    'error': 'Ollama no disponible',
                    'response': 'El servicio de chat local no está disponible'
                }
            
            # Agregar mensaje al historial
            self.conversation_history.append({
                'role': 'user',
                'content': message,
                'timestamp': str(datetime.now())
            })
            
            # Construir contexto
            context = self._build_context(message) if use_context else ""
            
            # Generar respuesta
            response = self._generate_response(message, context)
            
            # Agregar respuesta al historial
            self.conversation_history.append({
                'role': 'assistant',
                'content': response,
                'timestamp': str(datetime.now())
            })
            
            # Analizar complejidad
            complexity = self._analyze_complexity(message, response)
            
            logger.info(f"✅ Chat procesado (Complejidad: {complexity})")
            
            return {
                'success': True,
                'response': response,
                'complexity': complexity,
                'timestamp': str(datetime.now()),
                'model': self.model
            }
        
        except Exception as e:
            logger.error(f"❌ Error en chat: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': 'Error procesando tu mensaje'
            }
    
    def _build_context(self, message: str) -> str:
        """Construir contexto de conversación"""
        try:
            context_parts = []
            
            # Agregar información del usuario
            if self.user_context['name']:
                context_parts.append(f"Usuario: {self.user_context['name']}")
            
            # Agregar últimos mensajes
            recent_messages = list(self.conversation_history)[-5:]
            if recent_messages:
                context_parts.append("\nHistorial reciente:")
                for msg in recent_messages:
                    role = "Usuario" if msg['role'] == 'user' else "Asistente"
                    context_parts.append(f"{role}: {msg['content'][:100]}...")
            
            return "\n".join(context_parts)
        
        except Exception as e:
            logger.error(f"Error construyendo contexto: {e}")
            return ""
    
    def _generate_response(self, message: str, context: str) -> str:
        """Generar respuesta usando Ollama"""
        try:
            # Construir prompt
            prompt = f"""Eres Jarvis, un asistente virtual inteligente y amable.

{context}

Usuario: {message}

Responde de manera concisa, útil y natural. Si necesitas información adicional, pídela."""
            
            # Llamar a Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No pude generar una respuesta')
            else:
                logger.error(f"Error de Ollama: {response.status_code}")
                return "Error generando respuesta"
        
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Disculpa, tuve un error generando la respuesta"
    
    def _analyze_complexity(self, message: str, response: str) -> str:
        """Analizar complejidad de la pregunta"""
        try:
            # Palabras clave por nivel
            simple_keywords = ['qué', 'cuál', 'cuándo', 'dónde', 'quién', 'hora', 'clima']
            complex_keywords = ['diseña', 'analiza', 'explica', 'resuelve', 'crea', 'genera']
            advanced_keywords = ['arquitectura', 'estrategia', 'optimiza', 'predice', 'simula']
            
            message_lower = message.lower()
            response_length = len(response)
            
            # Determinar complejidad
            if any(kw in message_lower for kw in advanced_keywords) or response_length > 500:
                return "avanzada"
            elif any(kw in message_lower for kw in complex_keywords) or response_length > 200:
                return "moderada"
            else:
                return "simple"
        
        except Exception as e:
            logger.error(f"Error analizando complejidad: {e}")
            return "desconocida"
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Obtener historial de conversación"""
        try:
            history = list(self.conversation_history)[-limit:]
            logger.info(f"✅ Historial obtenido ({len(history)} mensajes)")
            return history
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def clear_history(self) -> bool:
        """Limpiar historial de conversación"""
        try:
            self.conversation_history.clear()
            logger.info("✅ Historial limpiado")
            return True
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")
            return False
    
    def set_user_context(self, name: str = None, preferences: Dict = None) -> bool:
        """Establecer contexto del usuario"""
        try:
            if name:
                self.user_context['name'] = name
            if preferences:
                self.user_context['preferences'].update(preferences)
            
            logger.info(f"✅ Contexto de usuario actualizado")
            return True
        except Exception as e:
            logger.error(f"Error actualizando contexto: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas del chat"""
        try:
            total_messages = len(self.conversation_history)
            user_messages = sum(1 for m in self.conversation_history if m['role'] == 'user')
            assistant_messages = total_messages - user_messages
            
            avg_response_length = 0
            if assistant_messages > 0:
                total_length = sum(
                    len(m['content']) 
                    for m in self.conversation_history 
                    if m['role'] == 'assistant'
                )
                avg_response_length = total_length / assistant_messages
            
            stats = {
                'total_messages': total_messages,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'avg_response_length': avg_response_length,
                'ollama_available': self.ollama_available,
                'model': self.model
            }
            
            logger.info(f"✅ Estadísticas obtenidas")
            return stats
        
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def save_conversation(self, filepath: str) -> bool:
        """Guardar conversación a archivo"""
        try:
            data = {
                'timestamp': str(datetime.now()),
                'model': self.model,
                'messages': list(self.conversation_history),
                'user_context': self.user_context
            }
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Conversación guardada: {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Error guardando conversación: {e}")
            return False
    
    def load_conversation(self, filepath: str) -> bool:
        """Cargar conversación desde archivo"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.conversation_history.clear()
            for msg in data.get('messages', []):
                self.conversation_history.append(msg)
            
            self.user_context = data.get('user_context', self.user_context)
            
            logger.info(f"✅ Conversación cargada: {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Error cargando conversación: {e}")
            return False
