"""
JARVIS SECURITY MODULE - FASE 1
Encriptación, Vault, Detección de Exposición de Datos
Módulo Independiente - No depende de otros
"""

import os
import json
import hashlib
import hmac
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [SECURITY] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/jarvis-phase1/logs/security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisSecurityManager:
    """
    Gestor de Seguridad de Jarvis
    - Encriptación de datos sensibles
    - Vault encriptado
    - Detección de intentos de exposición
    - Auditoría de acceso
    """
    
    def __init__(self, master_password: str, vault_path: str = "/home/ubuntu/jarvis-phase1/config/vault.json"):
        """
        Inicializa el gestor de seguridad
        
        Args:
            master_password: Contraseña maestra para el vault
            vault_path: Ruta del archivo vault encriptado
        """
        self.vault_path = vault_path
        self.master_password = master_password
        self.cipher_suite = self._generate_cipher(master_password)
        self.vault = {}
        self.access_log = []
        self.exposure_attempts = []
        self.is_compromised = False
        
        # Crear vault si no existe
        if not os.path.exists(vault_path):
            self._create_vault()
        else:
            self._load_vault()
        
        logger.info("✓ Security Manager inicializado")
    
    def _generate_cipher(self, password: str) -> Fernet:
        """Genera cipher Fernet a partir de contraseña maestra"""
        # Derivar clave de la contraseña
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'jarvis_salt_2024',  # En producción, usar salt aleatorio
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key)
    
    def _create_vault(self):
        """Crea un nuevo vault encriptado"""
        vault_data = {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "data": {},
            "access_log": [],
            "exposure_attempts": []
        }
        self._save_vault(vault_data)
        logger.info("✓ Nuevo vault creado")
    
    def _save_vault(self, data: dict):
        """Guarda vault encriptado"""
        try:
            json_data = json.dumps(data).encode()
            encrypted_data = self.cipher_suite.encrypt(json_data)
            
            with open(self.vault_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.debug("✓ Vault guardado encriptado")
        except Exception as e:
            logger.error(f"✗ Error guardando vault: {e}")
            raise
    
    def _load_vault(self):
        """Carga y desencripta vault"""
        try:
            with open(self.vault_path, 'rb') as f:
                encrypted_data = f.read()
            
            json_data = self.cipher_suite.decrypt(encrypted_data)
            vault_data = json.loads(json_data.decode())
            
            self.vault = vault_data.get('data', {})
            self.access_log = vault_data.get('access_log', [])
            self.exposure_attempts = vault_data.get('exposure_attempts', [])
            
            logger.info("✓ Vault cargado y desencriptado")
        except Exception as e:
            logger.error(f"✗ Error cargando vault: {e}")
            raise
    
    def store_secret(self, key: str, value: str, category: str = "general"):
        """
        Almacena un secreto en el vault encriptado
        
        Args:
            key: Identificador del secreto
            value: Valor del secreto
            category: Categoría (api_keys, passwords, tokens, etc)
        """
        if self.is_compromised:
            logger.warning("⚠ Sistema comprometido. Almacenamiento bloqueado.")
            return False
        
        try:
            self.vault[key] = {
                "value": value,
                "category": category,
                "created": datetime.now().isoformat(),
                "access_count": 0
            }
            
            # Guardar cambios
            vault_data = {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "data": self.vault,
                "access_log": self.access_log,
                "exposure_attempts": self.exposure_attempts
            }
            self._save_vault(vault_data)
            
            logger.info(f"✓ Secreto '{key}' almacenado en vault")
            return True
        except Exception as e:
            logger.error(f"✗ Error almacenando secreto: {e}")
            return False
    
    def get_secret(self, key: str, user_id: str = "system") -> str:
        """
        Obtiene un secreto del vault (con auditoría)
        
        Args:
            key: Identificador del secreto
            user_id: ID del usuario que accede
        
        Returns:
            Valor del secreto o None
        """
        if key not in self.vault:
            logger.warning(f"✗ Secreto '{key}' no encontrado")
            return None
        
        try:
            secret_data = self.vault[key]
            secret_data["access_count"] += 1
            
            # Registrar acceso
            access_record = {
                "key": key,
                "user": user_id,
                "timestamp": datetime.now().isoformat(),
                "action": "read"
            }
            self.access_log.append(access_record)
            
            # Guardar cambios
            vault_data = {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "data": self.vault,
                "access_log": self.access_log,
                "exposure_attempts": self.exposure_attempts
            }
            self._save_vault(vault_data)
            
            logger.debug(f"✓ Secreto '{key}' accedido por {user_id}")
            return secret_data["value"]
        except Exception as e:
            logger.error(f"✗ Error obteniendo secreto: {e}")
            return None
    
    def detect_data_exposure(self, data: str, sensitive_patterns: list = None) -> bool:
        """
        Detecta si datos contienen información sensible
        
        Args:
            data: Datos a analizar
            sensitive_patterns: Patrones a detectar (emails, tokens, etc)
        
        Returns:
            True si se detecta exposición
        """
        if sensitive_patterns is None:
            sensitive_patterns = [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'sk_[a-zA-Z0-9]{32,}',  # API keys
                r'password\s*[:=]\s*[^\s]+',  # Passwords
                r'token\s*[:=]\s*[^\s]+',  # Tokens
                r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}',  # Credit cards
            ]
        
        import re
        
        exposed = False
        for pattern in sensitive_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                exposed = True
                break
        
        if exposed:
            logger.warning(f"⚠ EXPOSICIÓN DETECTADA: Datos sensibles encontrados")
            exposure_record = {
                "timestamp": datetime.now().isoformat(),
                "data_preview": data[:100],
                "pattern_matched": True
            }
            self.exposure_attempts.append(exposure_record)
            return True
        
        return False
    
    def block_if_exposed(self, data: str) -> bool:
        """
        Bloquea operación si se detecta exposición de datos
        
        Args:
            data: Datos a verificar
        
        Returns:
            True si está seguro, False si se bloqueó
        """
        if self.detect_data_exposure(data):
            logger.critical("🚨 INTENTO DE EXPOSICIÓN BLOQUEADO - APAGANDO SISTEMA")
            self.is_compromised = True
            return False
        
        return True
    
    def get_access_log(self) -> list:
        """Retorna log de acceso a secretos"""
        return self.access_log
    
    def get_exposure_attempts(self) -> list:
        """Retorna intentos de exposición de datos"""
        return self.exposure_attempts
    
    def is_system_compromised(self) -> bool:
        """Verifica si el sistema está comprometido"""
        return self.is_compromised
    
    def emergency_shutdown(self):
        """Apagado de emergencia - Limpia datos sensibles"""
        logger.critical("🚨 APAGADO DE EMERGENCIA ACTIVADO")
        self.vault = {}
        self.is_compromised = True
        
        # Guardar estado comprometido
        vault_data = {
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "data": {},
            "access_log": self.access_log,
            "exposure_attempts": self.exposure_attempts,
            "compromised": True
        }
        self._save_vault(vault_data)
        logger.critical("✓ Datos sensibles limpiados")


if __name__ == "__main__":
    # Test del módulo
    print("=" * 60)
    print("JARVIS SECURITY MODULE - TEST")
    print("=" * 60)
    
    # Inicializar
    security = JarvisSecurityManager(master_password="test_password_123")
    
    # Almacenar secretos
    security.store_secret("api_key_openai", "sk_test_123456789", "api_keys")
    security.store_secret("db_password", "super_secure_pass", "passwords")
    
    # Acceder a secretos
    api_key = security.get_secret("api_key_openai", "user_eli")
    print(f"✓ API Key obtenida: {api_key[:10]}...")
    
    # Detectar exposición
    print("\n--- Test de Detección de Exposición ---")
    safe_data = "Este es un mensaje seguro"
    unsafe_data = "Mi email es eli@example.com y mi token es sk_test_123456789"
    
    print(f"Datos seguros: {security.detect_data_exposure(safe_data)}")
    print(f"Datos inseguros: {security.detect_data_exposure(unsafe_data)}")
    
    # Ver logs
    print(f"\n--- Access Log ---")
    for log in security.get_access_log():
        print(f"  {log}")
    
    print("\n✓ Test completado")
