"""
JARVIS FASE 5 - Configuration Manager
Gestor de configuración centralizado
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class ConfigManager:
    """Gestor de configuración de Jarvis"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicializar gestor de configuración
        
        Args:
            config_file: Ruta del archivo de configuración
        """
        logger.info("📋 Inicializando Configuration Manager...")
        
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.env_vars: Dict[str, str] = {}
        
        # Cargar configuración
        self._load_config()
        self._load_env_vars()
        self._interpolate_env_vars()
        self._validate_config()
        
        logger.info("✅ Configuration Manager inicializado")
    
    def _load_config(self):
        """Cargar archivo de configuración"""
        try:
            if not os.path.exists(self.config_file):
                logger.error(f"❌ Archivo de configuración no encontrado: {self.config_file}")
                raise FileNotFoundError(f"Config file not found: {self.config_file}")
            
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            
            logger.info(f"✅ Configuración cargada desde {self.config_file}")
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parseando JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error cargando configuración: {e}")
            raise
    
    def _load_env_vars(self):
        """Cargar variables de entorno"""
        try:
            # Cargar desde archivo .env si existe
            env_file = ".env"
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            self.env_vars[key] = value
            
            # Cargar desde variables de entorno del sistema
            for key, value in os.environ.items():
                self.env_vars[key] = value
            
            logger.info(f"✅ {len(self.env_vars)} variables de entorno cargadas")
        
        except Exception as e:
            logger.warning(f"⚠️ Error cargando variables de entorno: {e}")
    
    def _interpolate_env_vars(self):
        """Reemplazar variables de entorno en la configuración"""
        def replace_vars(obj):
            if isinstance(obj, dict):
                return {k: replace_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_vars(item) for item in obj]
            elif isinstance(obj, str):
                # Reemplazar ${VAR_NAME} con valor de variable de entorno
                pattern = r'\$\{([^}]+)\}'
                
                def replacer(match):
                    var_name = match.group(1)
                    return self.env_vars.get(var_name, match.group(0))
                
                return re.sub(pattern, replacer, obj)
            else:
                return obj
        
        self.config = replace_vars(self.config)
        logger.info("✅ Variables de entorno interpoladas")
    
    def _validate_config(self):
        """Validar configuración"""
        try:
            # Validaciones básicas
            required_sections = ['system', 'security', 'personality']
            
            for section in required_sections:
                if section not in self.config:
                    logger.warning(f"⚠️ Sección requerida faltante: {section}")
            
            # Validar APIs
            apis = self.config.get('apis', {})
            for api_name, api_config in apis.items():
                if api_config.get('enabled'):
                    if 'api_key' in api_config and api_config['api_key'].startswith('${'):
                        logger.warning(f"⚠️ API key no configurada para {api_name}")
            
            # Validar email
            email_config = self.config.get('email', {})
            if email_config.get('enabled'):
                if email_config.get('account', {}).get('email', '').startswith('${'):
                    logger.warning("⚠️ Email no configurado")
            
            logger.info("✅ Configuración validada")
        
        except Exception as e:
            logger.error(f"❌ Error validando configuración: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtener valor de configuración
        
        Args:
            key: Clave (ej: "apis.openai.api_key")
            default: Valor por defecto
            
        Returns:
            Valor de configuración
        """
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                else:
                    return default
            
            return value if value is not None else default
        
        except Exception as e:
            logger.error(f"Error obteniendo configuración {key}: {e}")
            return default
    
    def set(self, key: str, value: Any):
        """
        Establecer valor de configuración
        
        Args:
            key: Clave (ej: "apis.openai.api_key")
            value: Nuevo valor
        """
        try:
            keys = key.split('.')
            config = self.config
            
            # Navegar hasta la penúltima clave
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Establecer valor
            config[keys[-1]] = value
            
            logger.info(f"✅ Configuración actualizada: {key}")
        
        except Exception as e:
            logger.error(f"Error estableciendo configuración {key}: {e}")
    
    def save(self):
        """Guardar configuración en archivo"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"✅ Configuración guardada en {self.config_file}")
        
        except Exception as e:
            logger.error(f"❌ Error guardando configuración: {e}")
    
    def get_personality(self) -> Dict[str, Any]:
        """Obtener configuración de personalidad"""
        return self.config.get('personality', {})
    
    def get_interaction_mode(self, mode: str = None) -> Dict[str, Any]:
        """Obtener modo de interacción"""
        if mode is None:
            mode = self.config.get('interaction_modes', {}).get('default', 'professional')
        
        modes = self.config.get('interaction_modes', {}).get('modes', {})
        return modes.get(mode, modes.get('professional', {}))
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """Obtener configuración de API"""
        return self.config.get('apis', {}).get(api_name, {})
    
    def get_email_config(self) -> Dict[str, Any]:
        """Obtener configuración de email"""
        return self.config.get('email', {})
    
    def get_rules(self) -> Dict[str, Any]:
        """Obtener reglas"""
        return self.config.get('rules', {})
    
    def get_behavior(self) -> Dict[str, Any]:
        """Obtener comportamiento"""
        return self.config.get('behavior', {})
    
    def is_api_enabled(self, api_name: str) -> bool:
        """Verificar si API está habilitada"""
        return self.get_api_config(api_name).get('enabled', False)
    
    def print_summary(self):
        """Imprimir resumen de configuración"""
        print("\n" + "="*70)
        print("📋 JARVIS - CONFIGURACIÓN")
        print("="*70)
        
        print(f"\n🔧 SISTEMA:")
        print(f"  Nombre: {self.get('system.name')}")
        print(f"  Versión: {self.get('system.version')}")
        print(f"  Entorno: {self.get('system.environment')}")
        print(f"  Idioma: {self.get('system.language')}")
        
        print(f"\n🤖 PERSONALIDAD:")
        personality = self.get_personality()
        print(f"  Nombre: {personality.get('name')}")
        print(f"  Rol: {personality.get('role')}")
        print(f"  Tono: {personality.get('tone')}")
        print(f"  Nivel de formalidad: {personality.get('formality_level')}")
        
        print(f"\n🔌 APIs HABILITADAS:")
        apis = self.config.get('apis', {})
        for api_name, api_config in apis.items():
            status = "✅" if api_config.get('enabled') else "❌"
            print(f"  {status} {api_name}")
        
        print(f"\n📧 EMAIL:")
        email = self.get_email_config()
        print(f"  Habilitado: {'✅' if email.get('enabled') else '❌'}")
        print(f"  SMTP: {email.get('smtp', {}).get('server')}")
        
        print(f"\n📋 REGLAS:")
        rules = self.get_rules()
        print(f"  Timeout de comando: {rules.get('general', {}).get('command_timeout_seconds')}s")
        print(f"  Rate limit: {rules.get('general', {}).get('rate_limit_per_minute')}/min")
        print(f"  Requiere confirmación: {rules.get('device_control', {}).get('require_confirmation')}")
        
        print("\n" + "="*70 + "\n")
    
    def export_safe_config(self) -> Dict[str, Any]:
        """Exportar configuración sin datos sensibles"""
        safe_config = json.loads(json.dumps(self.config))
        
        # Ocultar datos sensibles
        def mask_sensitive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Ocultar keys, tokens, passwords
                    if any(x in key.lower() for x in ['key', 'token', 'password', 'secret', 'credential']):
                        obj[key] = "***REDACTED***"
                    else:
                        mask_sensitive(value, current_path)
            
            elif isinstance(obj, list):
                for item in obj:
                    mask_sensitive(item, path)
        
        mask_sensitive(safe_config)
        return safe_config


# Ejemplo de uso
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Crear gestor
    config = ConfigManager()
    
    # Mostrar resumen
    config.print_summary()
    
    # Obtener valores
    print(f"Nombre de sistema: {config.get('system.name')}")
    print(f"API OpenAI habilitada: {config.is_api_enabled('openai')}")
    print(f"Modo de interacción: {config.get_interaction_mode()}")
    
    # Exportar configuración segura
    safe_config = config.export_safe_config()
    print(f"\nConfiguración segura (sin datos sensibles):")
    print(json.dumps(safe_config, indent=2)[:500] + "...")
