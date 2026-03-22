"""
COMPLEXITY DETECTOR - Detecta el nivel de complejidad de preguntas
Decide si usar local, híbrido o conectar a Manus
"""

import logging
import re
from typing import Dict, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ComplexityLevel(Enum):
    """Niveles de complejidad"""
    SIMPLE = 1          # Preguntas simples, búsquedas
    MODERATE = 2        # Análisis moderado
    ADVANCED = 3        # Razonamiento avanzado


class ComplexityDetector:
    """Detector de complejidad de preguntas"""
    
    def __init__(self, threshold_moderate: float = 0.4, threshold_advanced: float = 0.7):
        """
        Inicializar detector
        
        Args:
            threshold_moderate: Umbral para complejidad moderada (0-1)
            threshold_advanced: Umbral para complejidad avanzada (0-1)
        """
        self.threshold_moderate = threshold_moderate
        self.threshold_advanced = threshold_advanced
        
        # Palabras clave por nivel
        self.simple_keywords = {
            'qué', 'cuál', 'cuándo', 'dónde', 'quién',
            'hora', 'clima', 'reproduce', 'envía', 'abre',
            'cierra', 'enciende', 'apaga', 'busca', 'dime'
        }
        
        self.moderate_keywords = {
            'analiza', 'explica', 'resume', 'genera', 'crea',
            'compara', 'traduce', 'convierte', 'calcula', 'estima',
            'sugiere', 'recomienda', 'clasifica', 'organiza'
        }
        
        self.advanced_keywords = {
            'diseña', 'arquitectura', 'estrategia', 'optimiza',
            'predice', 'simula', 'modela', 'investiga', 'resuelve',
            'demuestra', 'prueba', 'valida', 'implementa', 'refactoriza'
        }
        
        logger.info("✅ Complexity Detector inicializado")
    
    def detect(self, message: str, context: str = "") -> Tuple[ComplexityLevel, float, Dict]:
        """
        Detectar complejidad de un mensaje
        
        Args:
            message: Mensaje del usuario
            context: Contexto adicional
            
        Returns:
            Tupla (nivel, score, detalles)
        """
        try:
            # Calcular puntuación
            score = self._calculate_score(message, context)
            
            # Determinar nivel
            if score >= self.threshold_advanced:
                level = ComplexityLevel.ADVANCED
            elif score >= self.threshold_moderate:
                level = ComplexityLevel.MODERATE
            else:
                level = ComplexityLevel.SIMPLE
            
            # Obtener detalles
            details = self._get_details(message, score, level)
            
            logger.info(f"✅ Complejidad detectada: {level.name} (score: {score:.2f})")
            
            return level, score, details
        
        except Exception as e:
            logger.error(f"❌ Error detectando complejidad: {e}")
            return ComplexityLevel.SIMPLE, 0.0, {}
    
    def _calculate_score(self, message: str, context: str = "") -> float:
        """Calcular puntuación de complejidad"""
        try:
            score = 0.0
            message_lower = message.lower()
            
            # 1. Análisis de palabras clave
            advanced_count = sum(1 for kw in self.advanced_keywords if kw in message_lower)
            moderate_count = sum(1 for kw in self.moderate_keywords if kw in message_lower)
            simple_count = sum(1 for kw in self.simple_keywords if kw in message_lower)
            
            # Puntuación por palabras clave
            score += advanced_count * 0.3
            score += moderate_count * 0.15
            score -= simple_count * 0.05
            
            # 2. Longitud del mensaje
            message_length = len(message.split())
            if message_length > 30:
                score += 0.2
            elif message_length > 15:
                score += 0.1
            
            # 3. Presencia de operadores lógicos
            logical_operators = ['y', 'o', 'pero', 'aunque', 'porque', 'si', 'entonces']
            operator_count = sum(1 for op in logical_operators if op in message_lower)
            score += operator_count * 0.05
            
            # 4. Presencia de números y datos
            if re.search(r'\d+', message):
                score += 0.1
            
            # 5. Presencia de código o sintaxis técnica
            if re.search(r'[{}\[\]()]', message):
                score += 0.15
            
            # 6. Preguntas anidadas
            question_count = message.count('?')
            if question_count > 1:
                score += 0.1
            
            # 7. Análisis de contexto
            if context:
                context_lower = context.lower()
                if any(kw in context_lower for kw in self.advanced_keywords):
                    score += 0.1
            
            # Normalizar a 0-1
            score = min(1.0, max(0.0, score))
            
            return score
        
        except Exception as e:
            logger.error(f"Error calculando score: {e}")
            return 0.0
    
    def _get_details(self, message: str, score: float, level: ComplexityLevel) -> Dict:
        """Obtener detalles del análisis"""
        try:
            message_lower = message.lower()
            
            details = {
                'level': level.name,
                'score': round(score, 2),
                'message_length': len(message.split()),
                'requires_manus': level == ComplexityLevel.ADVANCED,
                'can_use_local': level in [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE],
                'estimated_time_ms': self._estimate_time(level),
                'reasoning': self._get_reasoning(message, level)
            }
            
            return details
        
        except Exception as e:
            logger.error(f"Error obteniendo detalles: {e}")
            return {}
    
    def _estimate_time(self, level: ComplexityLevel) -> int:
        """Estimar tiempo de procesamiento"""
        times = {
            ComplexityLevel.SIMPLE: 100,
            ComplexityLevel.MODERATE: 1000,
            ComplexityLevel.ADVANCED: 3000
        }
        return times.get(level, 1000)
    
    def _get_reasoning(self, message: str, level: ComplexityLevel) -> str:
        """Obtener razonamiento del análisis"""
        try:
            message_lower = message.lower()
            reasons = []
            
            if level == ComplexityLevel.SIMPLE:
                if any(kw in message_lower for kw in self.simple_keywords):
                    reasons.append("Contiene palabras clave simples")
                if len(message.split()) < 10:
                    reasons.append("Mensaje corto")
                reasons.append("Puede resolverse localmente")
            
            elif level == ComplexityLevel.MODERATE:
                if any(kw in message_lower for kw in self.moderate_keywords):
                    reasons.append("Requiere análisis moderado")
                if len(message.split()) > 15:
                    reasons.append("Mensaje de longitud media")
                reasons.append("Ollama puede procesarlo")
            
            elif level == ComplexityLevel.ADVANCED:
                if any(kw in message_lower for kw in self.advanced_keywords):
                    reasons.append("Contiene palabras clave avanzadas")
                if len(message.split()) > 30:
                    reasons.append("Mensaje largo y complejo")
                reasons.append("Requiere conexión a Manus")
            
            return " | ".join(reasons) if reasons else "Análisis completado"
        
        except Exception as e:
            logger.error(f"Error obteniendo razonamiento: {e}")
            return "Error en análisis"
    
    def should_use_manus(self, level: ComplexityLevel) -> bool:
        """Determinar si debe usar Manus"""
        return level == ComplexityLevel.ADVANCED
    
    def should_use_cache(self, level: ComplexityLevel) -> bool:
        """Determinar si puede usar caché"""
        return level in [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE]
    
    def get_recommendation(self, level: ComplexityLevel) -> Dict:
        """Obtener recomendación de procesamiento"""
        try:
            recommendations = {
                ComplexityLevel.SIMPLE: {
                    'primary': 'cache',
                    'fallback': 'local',
                    'use_manus': False,
                    'priority': 'speed'
                },
                ComplexityLevel.MODERATE: {
                    'primary': 'local',
                    'fallback': 'manus',
                    'use_manus': False,
                    'priority': 'balance'
                },
                ComplexityLevel.ADVANCED: {
                    'primary': 'manus',
                    'fallback': 'local',
                    'use_manus': True,
                    'priority': 'quality'
                }
            }
            
            return recommendations.get(level, recommendations[ComplexityLevel.SIMPLE])
        
        except Exception as e:
            logger.error(f"Error obteniendo recomendación: {e}")
            return {}
    
    def batch_analyze(self, messages: list) -> list:
        """Analizar múltiples mensajes"""
        try:
            results = []
            for msg in messages:
                level, score, details = self.detect(msg)
                results.append({
                    'message': msg,
                    'level': level.name,
                    'score': score,
                    'details': details
                })
            
            logger.info(f"✅ {len(results)} mensajes analizados")
            return results
        
        except Exception as e:
            logger.error(f"Error en análisis por lotes: {e}")
            return []
