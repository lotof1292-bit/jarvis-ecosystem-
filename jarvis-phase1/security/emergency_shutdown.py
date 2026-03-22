"""
JARVIS EMERGENCY SHUTDOWN MODULE - FASE 1
Palabra de seguridad y apagado forzado
Módulo Independiente - No depende de otros
"""

import os
import json
import logging
import signal
import sys
import hashlib
from datetime import datetime
from threading import Thread, Event

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [SHUTDOWN] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/jarvis-phase1/logs/shutdown.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisEmergencyShutdown:
    """
    Gestor de Apagado de Emergencia
    - Palabra de seguridad (Dixie)
    - Apagado forzado
    - Limpieza de datos sensibles
    - Registro de eventos de seguridad
    """
    
    def __init__(self, 
                 emergency_word: str = "Dixie",
                 config_path: str = "/home/ubuntu/jarvis-phase1/config/shutdown_config.json"):
        """
        Inicializa el gestor de apagado
        
        Args:
            emergency_word: Palabra de seguridad para apagado
            config_path: Ruta de configuración
        """
        self.emergency_word = emergency_word
        self.emergency_word_hash = hashlib.sha256(emergency_word.encode()).hexdigest()
        self.config_path = config_path
        self.is_shutdown_active = False
        self.shutdown_event = Event()
        self.failed_attempts = 0
        self.max_failed_attempts = 3
        self.security_log = []
        self.cleanup_callbacks = []
        
        # Cargar configuración
        self._load_config()
        
        # Registrar handlers de señales
        self._register_signal_handlers()
        
        logger.info("✓ Emergency Shutdown Manager inicializado")
    
    def _load_config(self):
        """Carga configuración de apagado"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self._create_default_config()
                self._save_config()
        except Exception as e:
            logger.error(f"✗ Error cargando config: {e}")
            self.config = self._create_default_config()
    
    def _create_default_config(self) -> dict:
        """Crea configuración por defecto"""
        return {
            "emergency_word_hash": self.emergency_word_hash,
            "max_failed_attempts": self.max_failed_attempts,
            "cleanup_on_shutdown": True,
            "wipe_memory": True,
            "wipe_cache": True,
            "wipe_logs": False,  # Mantener logs para auditoría
            "backup_before_wipe": True,
            "shutdown_delay_seconds": 2
        }
    
    def _save_config(self):
        """Guarda configuración"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"✗ Error guardando config: {e}")
    
    def _register_signal_handlers(self):
        """Registra handlers para señales del sistema"""
        def signal_handler(signum, frame):
            logger.warning(f"🚨 Señal recibida: {signum}")
            self.emergency_shutdown("signal_received")
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def verify_emergency_word(self, word: str) -> bool:
        """
        Verifica la palabra de seguridad
        
        Args:
            word: Palabra a verificar
        
        Returns:
            True si es correcta
        """
        try:
            word_hash = hashlib.sha256(word.encode()).hexdigest()
            
            if word_hash == self.emergency_word_hash:
                logger.info("✓ Palabra de seguridad verificada")
                self.failed_attempts = 0
                return True
            else:
                self.failed_attempts += 1
                logger.warning(f"✗ Palabra incorrecta (Intento {self.failed_attempts}/{self.max_failed_attempts})")
                
                # Registrar intento fallido
                self.security_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "event": "failed_emergency_word",
                    "attempt": self.failed_attempts
                })
                
                # Apagado forzado si demasiados intentos
                if self.failed_attempts >= self.max_failed_attempts:
                    logger.critical("🚨 DEMASIADOS INTENTOS - APAGADO FORZADO")
                    self.emergency_shutdown("max_failed_attempts")
                
                return False
        except Exception as e:
            logger.error(f"✗ Error verificando palabra: {e}")
            return False
    
    def register_cleanup_callback(self, callback):
        """
        Registra función de limpieza a ejecutar en apagado
        
        Args:
            callback: Función a ejecutar (debe ser callable)
        """
        if callable(callback):
            self.cleanup_callbacks.append(callback)
            logger.debug(f"✓ Callback de limpieza registrado")
        else:
            logger.warning("✗ Callback no es callable")
    
    def emergency_shutdown(self, reason: str = "manual"):
        """
        Ejecuta apagado de emergencia
        
        Args:
            reason: Razón del apagado
        """
        if self.is_shutdown_active:
            logger.warning("⚠ Apagado ya en progreso")
            return
        
        self.is_shutdown_active = True
        
        logger.critical(f"🚨 APAGADO DE EMERGENCIA ACTIVADO - Razón: {reason}")
        
        # Registrar evento
        self.security_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "emergency_shutdown",
            "reason": reason
        })
        
        # Ejecutar callbacks de limpieza
        self._execute_cleanup_callbacks()
        
        # Limpiar datos sensibles
        if self.config.get("cleanup_on_shutdown"):
            self._cleanup_sensitive_data()
        
        # Guardar log de seguridad
        self._save_security_log()
        
        # Esperar antes de apagar
        import time
        delay = self.config.get("shutdown_delay_seconds", 2)
        logger.info(f"⏳ Apagando en {delay} segundos...")
        time.sleep(delay)
        
        # Señalar evento de apagado
        self.shutdown_event.set()
        
        logger.critical("✓ Sistema apagado")
        sys.exit(0)
    
    def _execute_cleanup_callbacks(self):
        """Ejecuta todos los callbacks de limpieza registrados"""
        logger.info("🧹 Ejecutando callbacks de limpieza...")
        
        for callback in self.cleanup_callbacks:
            try:
                callback()
                logger.debug("✓ Callback ejecutado")
            except Exception as e:
                logger.error(f"✗ Error en callback: {e}")
    
    def _cleanup_sensitive_data(self):
        """Limpia datos sensibles antes de apagar"""
        try:
            logger.info("🧹 Limpiando datos sensibles...")
            
            # Limpiar memoria
            if self.config.get("wipe_memory"):
                memory_path = "/home/ubuntu/jarvis-phase1/config/memory.json"
                if os.path.exists(memory_path):
                    with open(memory_path, 'w') as f:
                        json.dump({"wiped": True, "timestamp": datetime.now().isoformat()}, f)
                    logger.info("✓ Memoria limpiada")
            
            # Limpiar caché
            if self.config.get("wipe_cache"):
                cache_path = "/home/ubuntu/jarvis-phase1/config/cache"
                if os.path.exists(cache_path):
                    import shutil
                    shutil.rmtree(cache_path)
                    logger.info("✓ Caché limpiado")
            
            # Limpiar archivos temporales
            temp_path = "/tmp/jarvis_*"
            os.system(f"rm -f {temp_path}")
            logger.info("✓ Archivos temporales limpiados")
            
            logger.info("✓ Limpieza completada")
        except Exception as e:
            logger.error(f"✗ Error limpiando datos: {e}")
    
    def _save_security_log(self):
        """Guarda log de seguridad"""
        try:
            log_path = "/home/ubuntu/jarvis-phase1/logs/security_events.json"
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            
            with open(log_path, 'w') as f:
                json.dump(self.security_log, f, indent=4)
            
            logger.info(f"✓ Log de seguridad guardado: {log_path}")
        except Exception as e:
            logger.error(f"✗ Error guardando log: {e}")
    
    def get_security_log(self) -> list:
        """Retorna log de seguridad"""
        return self.security_log
    
    def is_system_shutdown(self) -> bool:
        """Verifica si el sistema está en proceso de apagado"""
        return self.shutdown_event.is_set()
    
    def wait_for_shutdown(self):
        """Espera a que se active el apagado"""
        self.shutdown_event.wait()


class ShutdownMonitor(Thread):
    """
    Monitor de apagado que ejecuta en background
    Detecta intentos de exposición y apaga si es necesario
    """
    
    def __init__(self, shutdown_manager: JarvisEmergencyShutdown):
        """
        Inicializa monitor
        
        Args:
            shutdown_manager: Instancia de JarvisEmergencyShutdown
        """
        super().__init__(daemon=True)
        self.shutdown_manager = shutdown_manager
        self.running = True
    
    def run(self):
        """Ejecuta monitor en background"""
        logger.info("✓ Shutdown Monitor iniciado")
        
        while self.running and not self.shutdown_manager.is_system_shutdown():
            # Aquí se pueden agregar chequeos periódicos
            import time
            time.sleep(1)
        
        logger.info("✓ Shutdown Monitor detenido")
    
    def stop(self):
        """Detiene el monitor"""
        self.running = False


if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS EMERGENCY SHUTDOWN MODULE - TEST")
    print("=" * 60)
    
    # Inicializar
    shutdown = JarvisEmergencyShutdown(emergency_word="Dixie")
    
    print("\nTest de palabra de seguridad:")
    print("Palabra correcta: Dixie")
    print("Palabra incorrecta: test123")
    
    # Test 1: Palabra incorrecta
    print("\n--- Test 1: Palabra incorrecta ---")
    result = shutdown.verify_emergency_word("test123")
    print(f"Resultado: {result}")
    
    # Test 2: Palabra correcta
    print("\n--- Test 2: Palabra correcta ---")
    result = shutdown.verify_emergency_word("Dixie")
    print(f"Resultado: {result}")
    
    # Test 3: Registrar callback
    print("\n--- Test 3: Callback de limpieza ---")
    def cleanup_callback():
        print("  [CALLBACK] Limpiando recursos...")
    
    shutdown.register_cleanup_callback(cleanup_callback)
    print("✓ Callback registrado")
    
    # Ver log
    print(f"\n--- Security Log ---")
    for event in shutdown.get_security_log():
        print(f"  {event}")
    
    print("\n✓ Test completado")
