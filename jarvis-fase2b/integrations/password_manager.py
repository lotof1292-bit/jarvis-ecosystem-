"""
PASSWORD MANAGER - Gestor de Contraseñas Integrado
Almacenamiento seguro de credenciales
"""

import logging
import json
import os
from typing import Dict, Optional, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

logger = logging.getLogger(__name__)


class PasswordManager:
    """Gestor de contraseñas seguro"""
    
    def __init__(self, master_password: str, storage_path: str = 'config/passwords.enc'):
        self.master_password = master_password
        self.storage_path = storage_path
        self.cipher = self._create_cipher()
        self.passwords = self._load_passwords()
    
    def _create_cipher(self) -> Fernet:
        """Crear cipher a partir de contraseña maestra"""
        try:
            # Derivar clave de la contraseña maestra
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'jarvis_salt_2024',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
            cipher = Fernet(key)
            logger.info(f"✅ Cipher creado")
            return cipher
        except Exception as e:
            logger.error(f"❌ Error creando cipher: {e}")
            return None
    
    def _load_passwords(self) -> Dict:
        """Cargar contraseñas encriptadas"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'rb') as f:
                    encrypted_data = f.read()
                    decrypted = self.cipher.decrypt(encrypted_data)
                    passwords = json.loads(decrypted.decode())
                    logger.info(f"✅ Contraseñas cargadas")
                    return passwords
            return {}
        except Exception as e:
            logger.error(f"❌ Error cargando contraseñas: {e}")
            return {}
    
    def _save_passwords(self) -> bool:
        """Guardar contraseñas encriptadas"""
        try:
            json_data = json.dumps(self.passwords).encode()
            encrypted = self.cipher.encrypt(json_data)
            
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'wb') as f:
                f.write(encrypted)
            
            logger.info(f"✅ Contraseñas guardadas")
            return True
        except Exception as e:
            logger.error(f"❌ Error guardando contraseñas: {e}")
            return False
    
    def add_password(self, service: str, username: str, password: str, email: str = '', notes: str = '') -> bool:
        """Agregar nueva contraseña"""
        try:
            self.passwords[service] = {
                'username': username,
                'password': password,
                'email': email,
                'notes': notes,
                'created_at': str(__import__('datetime').datetime.now())
            }
            return self._save_passwords()
        except Exception as e:
            logger.error(f"❌ Error agregando contraseña: {e}")
            return False
    
    def get_password(self, service: str) -> Optional[Dict]:
        """Obtener contraseña de servicio"""
        try:
            if service in self.passwords:
                logger.info(f"✅ Contraseña obtenida para {service}")
                return self.passwords[service]
            logger.warning(f"⚠️ Servicio no encontrado: {service}")
            return None
        except Exception as e:
            logger.error(f"❌ Error obteniendo contraseña: {e}")
            return None
    
    def update_password(self, service: str, new_password: str) -> bool:
        """Actualizar contraseña"""
        try:
            if service in self.passwords:
                self.passwords[service]['password'] = new_password
                self.passwords[service]['updated_at'] = str(__import__('datetime').datetime.now())
                return self._save_passwords()
            logger.warning(f"⚠️ Servicio no encontrado: {service}")
            return False
        except Exception as e:
            logger.error(f"❌ Error actualizando contraseña: {e}")
            return False
    
    def delete_password(self, service: str) -> bool:
        """Eliminar contraseña"""
        try:
            if service in self.passwords:
                del self.passwords[service]
                return self._save_passwords()
            logger.warning(f"⚠️ Servicio no encontrado: {service}")
            return False
        except Exception as e:
            logger.error(f"❌ Error eliminando contraseña: {e}")
            return False
    
    def list_services(self) -> List[str]:
        """Listar servicios almacenados"""
        try:
            services = list(self.passwords.keys())
            logger.info(f"✅ {len(services)} servicios listados")
            return services
        except Exception as e:
            logger.error(f"❌ Error listando servicios: {e}")
            return []
    
    def search_service(self, query: str) -> List[str]:
        """Buscar servicios"""
        try:
            results = [s for s in self.passwords.keys() if query.lower() in s.lower()]
            logger.info(f"✅ {len(results)} servicios encontrados")
            return results
        except Exception as e:
            logger.error(f"❌ Error buscando servicios: {e}")
            return []
    
    def export_passwords(self, export_path: str, password_protected: bool = True) -> bool:
        """Exportar contraseñas"""
        try:
            if password_protected:
                json_data = json.dumps(self.passwords, indent=2).encode()
                encrypted = self.cipher.encrypt(json_data)
                with open(export_path, 'wb') as f:
                    f.write(encrypted)
            else:
                with open(export_path, 'w') as f:
                    json.dump(self.passwords, f, indent=2)
            
            logger.info(f"✅ Contraseñas exportadas a {export_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Error exportando: {e}")
            return False
    
    def import_passwords(self, import_path: str) -> bool:
        """Importar contraseñas"""
        try:
            if import_path.endswith('.enc'):
                with open(import_path, 'rb') as f:
                    encrypted = f.read()
                    decrypted = self.cipher.decrypt(encrypted)
                    imported = json.loads(decrypted.decode())
            else:
                with open(import_path, 'r') as f:
                    imported = json.load(f)
            
            self.passwords.update(imported)
            return self._save_passwords()
        except Exception as e:
            logger.error(f"❌ Error importando: {e}")
            return False
    
    def generate_password(self, length: int = 16, special_chars: bool = True) -> str:
        """Generar contraseña segura"""
        try:
            import string
            import secrets
            
            chars = string.ascii_letters + string.digits
            if special_chars:
                chars += string.punctuation
            
            password = ''.join(secrets.choice(chars) for _ in range(length))
            logger.info(f"✅ Contraseña generada ({length} caracteres)")
            return password
        except Exception as e:
            logger.error(f"❌ Error generando contraseña: {e}")
            return ""
    
    def check_password_strength(self, password: str) -> Dict:
        """Verificar fortaleza de contraseña"""
        try:
            strength = {
                'length': len(password) >= 12,
                'uppercase': any(c.isupper() for c in password),
                'lowercase': any(c.islower() for c in password),
                'digits': any(c.isdigit() for c in password),
                'special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
            }
            
            score = sum(strength.values())
            strength['score'] = score
            strength['level'] = ['Débil', 'Regular', 'Buena', 'Fuerte', 'Muy Fuerte'][min(score, 4)]
            
            logger.info(f"✅ Fortaleza verificada: {strength['level']}")
            return strength
        except Exception as e:
            logger.error(f"❌ Error verificando fortaleza: {e}")
            return {}
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas"""
        try:
            stats = {
                'total_services': len(self.passwords),
                'services': list(self.passwords.keys()),
                'storage_size': os.path.getsize(self.storage_path) if os.path.exists(self.storage_path) else 0
            }
            logger.info(f"✅ Estadísticas obtenidas")
            return stats
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
