"""
BIOMETRIC AUTHENTICATION - Autenticación Biométrica
Huella dactilar, reconocimiento facial, etc.
"""

import logging
from typing import Dict, Optional, List
import subprocess
import json
import os

logger = logging.getLogger(__name__)


class BiometricAuth:
    """Autenticación biométrica"""
    
    def __init__(self):
        self.fingerprint_data = {}
        self.facial_data = {}
        self.load_biometric_data()
    
    def load_biometric_data(self):
        """Cargar datos biométricos guardados"""
        try:
            if os.path.exists('config/biometric_data.json'):
                with open('config/biometric_data.json', 'r') as f:
                    data = json.load(f)
                    self.fingerprint_data = data.get('fingerprints', {})
                    self.facial_data = data.get('faces', {})
                logger.info(f"✅ Datos biométricos cargados")
        except Exception as e:
            logger.error(f"❌ Error cargando datos: {e}")
    
    def save_biometric_data(self):
        """Guardar datos biométricos"""
        try:
            os.makedirs('config', exist_ok=True)
            data = {
                'fingerprints': self.fingerprint_data,
                'faces': self.facial_data
            }
            with open('config/biometric_data.json', 'w') as f:
                json.dump(data, f)
            logger.info(f"✅ Datos biométricos guardados")
        except Exception as e:
            logger.error(f"❌ Error guardando datos: {e}")
    
    def enroll_fingerprint(self, user_id: str) -> bool:
        """Registrar huella dactilar"""
        try:
            # Simular captura de huella
            logger.info(f"📱 Coloca tu dedo en el lector...")
            
            # Generar datos simulados
            import hashlib
            import secrets
            
            fingerprint_hash = hashlib.sha256(
                (user_id + secrets.token_hex(16)).encode()
            ).hexdigest()
            
            self.fingerprint_data[user_id] = {
                'hash': fingerprint_hash,
                'enrolled_at': str(__import__('datetime').datetime.now()),
                'attempts': 0
            }
            
            self.save_biometric_data()
            logger.info(f"✅ Huella registrada para {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error registrando huella: {e}")
            return False
    
    def verify_fingerprint(self, user_id: str) -> bool:
        """Verificar huella dactilar"""
        try:
            if user_id not in self.fingerprint_data:
                logger.warning(f"⚠️ Usuario no registrado: {user_id}")
                return False
            
            logger.info(f"📱 Verifica tu huella...")
            
            # Simular verificación
            import random
            success = random.random() > 0.1  # 90% de éxito
            
            if success:
                self.fingerprint_data[user_id]['attempts'] = 0
                logger.info(f"✅ Huella verificada correctamente")
                return True
            else:
                self.fingerprint_data[user_id]['attempts'] += 1
                logger.warning(f"❌ Huella no coincide (intento {self.fingerprint_data[user_id]['attempts']})")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error verificando huella: {e}")
            return False
    
    def enroll_face(self, user_id: str, image_path: Optional[str] = None) -> bool:
        """Registrar reconocimiento facial"""
        try:
            logger.info(f"📷 Capturando imagen facial...")
            
            import hashlib
            import secrets
            
            # Generar datos simulados
            face_hash = hashlib.sha256(
                (user_id + secrets.token_hex(16)).encode()
            ).hexdigest()
            
            self.facial_data[user_id] = {
                'hash': face_hash,
                'image_path': image_path,
                'enrolled_at': str(__import__('datetime').datetime.now()),
                'attempts': 0
            }
            
            self.save_biometric_data()
            logger.info(f"✅ Rostro registrado para {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error registrando rostro: {e}")
            return False
    
    def verify_face(self, user_id: str, image_path: Optional[str] = None) -> bool:
        """Verificar reconocimiento facial"""
        try:
            if user_id not in self.facial_data:
                logger.warning(f"⚠️ Usuario no registrado: {user_id}")
                return False
            
            logger.info(f"📷 Verificando rostro...")
            
            # Simular verificación
            import random
            success = random.random() > 0.15  # 85% de éxito
            
            if success:
                self.facial_data[user_id]['attempts'] = 0
                logger.info(f"✅ Rostro verificado correctamente")
                return True
            else:
                self.facial_data[user_id]['attempts'] += 1
                logger.warning(f"❌ Rostro no coincide (intento {self.facial_data[user_id]['attempts']})")
                return False
        
        except Exception as e:
            logger.error(f"❌ Error verificando rostro: {e}")
            return False
    
    def multi_factor_auth(self, user_id: str, methods: List[str] = ['fingerprint', 'face']) -> bool:
        """Autenticación multifactor"""
        try:
            logger.info(f"🔐 Iniciando autenticación multifactor...")
            
            for method in methods:
                if method == 'fingerprint':
                    if not self.verify_fingerprint(user_id):
                        logger.error(f"❌ Falló verificación de huella")
                        return False
                
                elif method == 'face':
                    if not self.verify_face(user_id):
                        logger.error(f"❌ Falló verificación facial")
                        return False
            
            logger.info(f"✅ Autenticación multifactor exitosa")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error en autenticación: {e}")
            return False
    
    def get_enrolled_users(self) -> List[str]:
        """Obtener usuarios registrados"""
        try:
            fingerprint_users = set(self.fingerprint_data.keys())
            facial_users = set(self.facial_data.keys())
            all_users = list(fingerprint_users | facial_users)
            
            logger.info(f"✅ {len(all_users)} usuarios registrados")
            return all_users
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo usuarios: {e}")
            return []
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Obtener información biométrica del usuario"""
        try:
            info = {
                'user_id': user_id,
                'fingerprint_enrolled': user_id in self.fingerprint_data,
                'face_enrolled': user_id in self.facial_data
            }
            
            if user_id in self.fingerprint_data:
                info['fingerprint_data'] = self.fingerprint_data[user_id]
            
            if user_id in self.facial_data:
                info['facial_data'] = self.facial_data[user_id]
            
            logger.info(f"✅ Información obtenida para {user_id}")
            return info
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo información: {e}")
            return None
    
    def delete_user_biometric_data(self, user_id: str) -> bool:
        """Eliminar datos biométricos del usuario"""
        try:
            if user_id in self.fingerprint_data:
                del self.fingerprint_data[user_id]
            
            if user_id in self.facial_data:
                del self.facial_data[user_id]
            
            self.save_biometric_data()
            logger.info(f"✅ Datos biométricos eliminados para {user_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error eliminando datos: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas biométricas"""
        try:
            stats = {
                'total_fingerprints': len(self.fingerprint_data),
                'total_faces': len(self.facial_data),
                'total_users': len(set(list(self.fingerprint_data.keys()) + list(self.facial_data.keys()))),
                'fingerprint_users': list(self.fingerprint_data.keys()),
                'facial_users': list(self.facial_data.keys())
            }
            logger.info(f"✅ Estadísticas obtenidas")
            return stats
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
