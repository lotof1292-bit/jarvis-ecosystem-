"""
MANUS CONNECTOR - Conexión inteligente a Manus para razonamiento avanzado
Fallback automático, sincronización de contexto, caché de respuestas
"""

import logging
import json
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class ManusConnector:
    """Conector inteligente a Manus API"""
    
    def __init__(self, 
                 api_url: str = "https://api.manus.im",
                 api_key: str = None,
                 timeout: int = 30,
                 cache_ttl: int = 3600):
        """
        Inicializar conector a Manus
        
        Args:
            api_url: URL de la API de Manus
            api_key: Clave API de Manus
            timeout: Timeout en segundos
            cache_ttl: TTL del caché en segundos
        """
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        
        # Caché de respuestas
        self.response_cache = {}
        
        # Estadísticas
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'fallback_used': 0
        }
        
        # Verificar disponibilidad
        self.available = self._check_availability()
        
        logger.info(f"✅ Manus Connector inicializado (Disponible: {self.available})")
    
    def _check_availability(self) -> bool:
        """Verificar si Manus está disponible"""
        try:
            response = requests.get(
                f"{self.api_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️ Manus no disponible: {e}")
            return False
    
    def query(self, 
              message: str, 
              context: str = "",
              use_cache: bool = True,
              fallback_fn: callable = None) -> Dict:
        """
        Enviar consulta a Manus
        
        Args:
            message: Mensaje a procesar
            context: Contexto adicional
            use_cache: Usar caché si está disponible
            fallback_fn: Función de fallback si Manus no está disponible
            
        Returns:
            Dict con respuesta
        """
        try:
            # Generar hash para caché
            cache_key = self._generate_cache_key(message, context)
            
            # Verificar caché
            if use_cache and cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                if not self._is_cache_expired(cached_response):
                    logger.info("✅ Respuesta obtenida del caché")
                    self.stats['cache_hits'] += 1
                    return {
                        'success': True,
                        'response': cached_response['response'],
                        'source': 'cache',
                        'timestamp': cached_response['timestamp']
                    }
            
            # Si Manus no está disponible, usar fallback
            if not self.available:
                logger.warning("⚠️ Manus no disponible, usando fallback")
                self.stats['fallback_used'] += 1
                
                if fallback_fn:
                    fallback_response = fallback_fn(message, context)
                    return {
                        'success': True,
                        'response': fallback_response,
                        'source': 'fallback',
                        'timestamp': str(datetime.now())
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Manus no disponible y sin fallback',
                        'response': None
                    }
            
            # Enviar a Manus
            response = self._send_to_manus(message, context)
            
            if response['success']:
                # Guardar en caché
                if use_cache:
                    self.response_cache[cache_key] = {
                        'response': response['response'],
                        'timestamp': str(datetime.now()),
                        'expires_at': str(datetime.now() + timedelta(seconds=self.cache_ttl))
                    }
                
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
            
            self.stats['total_requests'] += 1
            return response
        
        except Exception as e:
            logger.error(f"❌ Error en query: {e}")
            self.stats['failed_requests'] += 1
            
            # Intentar fallback
            if fallback_fn:
                try:
                    fallback_response = fallback_fn(message, context)
                    return {
                        'success': True,
                        'response': fallback_response,
                        'source': 'fallback_error',
                        'timestamp': str(datetime.now())
                    }
                except Exception as fb_e:
                    logger.error(f"Fallback también falló: {fb_e}")
            
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def _send_to_manus(self, message: str, context: str) -> Dict:
        """Enviar consulta a Manus API"""
        try:
            payload = {
                'message': message,
                'context': context,
                'model': 'advanced',
                'temperature': 0.7
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            if self.api_key:
                headers['Authorization'] = f"Bearer {self.api_key}"
            
            response = requests.post(
                f"{self.api_url}/chat/query",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info("✅ Respuesta obtenida de Manus")
                return {
                    'success': True,
                    'response': result.get('response', ''),
                    'source': 'manus',
                    'timestamp': str(datetime.now()),
                    'metadata': result.get('metadata', {})
                }
            else:
                logger.error(f"Error de Manus: {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'response': None
                }
        
        except requests.Timeout:
            logger.error("Timeout conectando a Manus")
            return {
                'success': False,
                'error': 'Timeout',
                'response': None
            }
        except Exception as e:
            logger.error(f"Error enviando a Manus: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def _generate_cache_key(self, message: str, context: str) -> str:
        """Generar clave de caché"""
        try:
            combined = f"{message}:{context}"
            return hashlib.md5(combined.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error generando cache key: {e}")
            return ""
    
    def _is_cache_expired(self, cached_item: Dict) -> bool:
        """Verificar si el caché ha expirado"""
        try:
            expires_at = datetime.fromisoformat(cached_item['expires_at'])
            return datetime.now() > expires_at
        except Exception as e:
            logger.error(f"Error verificando expiración: {e}")
            return True
    
    def batch_query(self, messages: List[str], context: str = "") -> List[Dict]:
        """Procesar múltiples mensajes"""
        try:
            results = []
            for msg in messages:
                result = self.query(msg, context)
                results.append(result)
            
            logger.info(f"✅ {len(results)} consultas procesadas")
            return results
        
        except Exception as e:
            logger.error(f"Error en batch_query: {e}")
            return []
    
    def clear_cache(self) -> bool:
        """Limpiar caché"""
        try:
            self.response_cache.clear()
            logger.info("✅ Caché limpiado")
            return True
        except Exception as e:
            logger.error(f"Error limpiando caché: {e}")
            return False
    
    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del caché"""
        try:
            stats = {
                'cache_size': len(self.response_cache),
                'cache_ttl': self.cache_ttl,
                'total_items': len(self.response_cache),
                'expired_items': sum(
                    1 for item in self.response_cache.values()
                    if self._is_cache_expired(item)
                )
            }
            return stats
        except Exception as e:
            logger.error(f"Error obteniendo cache stats: {e}")
            return {}
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de uso"""
        try:
            total = self.stats['total_requests']
            success_rate = (
                self.stats['successful_requests'] / total * 100 
                if total > 0 else 0
            )
            
            stats = {
                **self.stats,
                'success_rate': round(success_rate, 2),
                'manus_available': self.available,
                'cache_stats': self.get_cache_stats()
            }
            
            logger.info(f"✅ Estadísticas obtenidas")
            return stats
        
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    def set_api_key(self, api_key: str) -> bool:
        """Establecer clave API"""
        try:
            self.api_key = api_key
            logger.info("✅ Clave API actualizada")
            return True
        except Exception as e:
            logger.error(f"Error estableciendo API key: {e}")
            return False
    
    def test_connection(self) -> Dict:
        """Probar conexión a Manus"""
        try:
            test_message = "¿Estás disponible?"
            response = self.query(test_message, use_cache=False)
            
            return {
                'success': response['success'],
                'available': self.available,
                'response_time': response.get('timestamp'),
                'message': 'Conexión exitosa' if response['success'] else 'Conexión fallida'
            }
        
        except Exception as e:
            logger.error(f"Error en test_connection: {e}")
            return {
                'success': False,
                'available': False,
                'error': str(e)
            }
