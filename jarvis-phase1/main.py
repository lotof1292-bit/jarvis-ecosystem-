"""
JARVIS CORE - FASE 1 ORCHESTRATOR
Integra todos los módulos de seguridad, sincronización, voz y apagado
"""

import os
import sys
import json
import logging
from datetime import datetime

# Agregar rutas de módulos
sys.path.insert(0, '/home/ubuntu/jarvis-phase1/security')
sys.path.insert(0, '/home/ubuntu/jarvis-phase1/sync')
sys.path.insert(0, '/home/ubuntu/jarvis-phase1/voice')

from security_manager import JarvisSecurityManager
from emergency_shutdown import JarvisEmergencyShutdown, ShutdownMonitor
from drive_sync_manager import JarvisDriveSyncManager
from voice_manager import JarvisVoiceManager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [JARVIS] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/jarvis-phase1/logs/jarvis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisCore:
    """
    Núcleo de Jarvis - FASE 1
    Orquestador principal que integra todos los módulos
    """
    
    def __init__(self, 
                 master_password: str = "jarvis_master_2024",
                 emergency_word: str = "Dixie",
                 user_id: str = "eli"):
        """
        Inicializa Jarvis Core
        
        Args:
            master_password: Contraseña maestra del vault
            emergency_word: Palabra de seguridad
            user_id: ID del usuario
        """
        self.user_id = user_id
        self.master_password = master_password
        self.emergency_word = emergency_word
        self.is_running = False
        self.modules = {}
        
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO JARVIS CORE - FASE 1")
        logger.info("=" * 60)
        
        # Inicializar módulos
        self._initialize_modules()
        
        logger.info("✓ Jarvis Core inicializado correctamente")
    
    def _initialize_modules(self):
        """Inicializa todos los módulos"""
        try:
            # 1. Security Manager
            logger.info("\n[1/4] Inicializando Security Manager...")
            self.modules['security'] = JarvisSecurityManager(
                master_password=self.master_password
            )
            logger.info("✓ Security Manager listo")
            
            # 2. Emergency Shutdown
            logger.info("\n[2/4] Inicializando Emergency Shutdown...")
            self.modules['shutdown'] = JarvisEmergencyShutdown(
                emergency_word=self.emergency_word
            )
            
            # Registrar callback de limpieza
            self.modules['shutdown'].register_cleanup_callback(
                self._cleanup_on_shutdown
            )
            logger.info("✓ Emergency Shutdown listo")
            
            # 3. Drive Sync Manager
            logger.info("\n[3/4] Inicializando Drive Sync Manager...")
            try:
                self.modules['sync'] = JarvisDriveSyncManager()
                logger.info("✓ Drive Sync Manager listo")
            except Exception as e:
                logger.warning(f"⚠ Drive Sync Manager no disponible: {e}")
                logger.info("  → Continuando sin sincronización en la nube")
                self.modules['sync'] = None
            
            # 4. Voice Manager
            logger.info("\n[4/4] Inicializando Voice Manager...")
            try:
                self.modules['voice'] = JarvisVoiceManager()
                logger.info("✓ Voice Manager listo")
            except Exception as e:
                logger.warning(f"⚠ Voice Manager no disponible: {e}")
                logger.info("  → Continuando sin reconocimiento de voz")
                self.modules['voice'] = None
            
            logger.info("\n" + "=" * 60)
            logger.info("✓ TODOS LOS MÓDULOS INICIALIZADOS")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"✗ Error inicializando módulos: {e}")
            raise
    
    def start(self):
        """Inicia Jarvis"""
        if self.is_running:
            logger.warning("⚠ Jarvis ya está en ejecución")
            return
        
        self.is_running = True
        
        logger.info("\n🎯 JARVIS INICIADO Y LISTO")
        logger.info(f"Usuario: {self.user_id}")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        # Iniciar monitor de apagado
        shutdown_monitor = ShutdownMonitor(self.modules['shutdown'])
        shutdown_monitor.start()
        
        # Loop principal
        self._main_loop()
    
    def _main_loop(self):
        """Loop principal de Jarvis"""
        logger.info("\n📍 Entrando en loop principal...")
        logger.info("Escribe 'help' para ver comandos disponibles")
        logger.info("Escribe 'salir' para terminar")
        
        while self.is_running and not self.modules['shutdown'].is_system_shutdown():
            try:
                # Prompt
                user_input = input("\n🤖 Jarvis> ").strip()
                
                if not user_input:
                    continue
                
                # Procesar comando
                self._process_command(user_input)
            
            except KeyboardInterrupt:
                logger.info("\n⏹ Interrupción del usuario")
                self.stop()
            except Exception as e:
                logger.error(f"✗ Error en loop principal: {e}")
    
    def _process_command(self, command: str):
        """Procesa comandos del usuario"""
        command = command.lower().strip()
        
        # Comandos especiales
        if command == "help":
            self._show_help()
        
        elif command == "salir":
            logger.info("👋 Hasta luego!")
            self.stop()
        
        elif command == "status":
            self._show_status()
        
        elif command == "vault":
            self._vault_menu()
        
        elif command == "sync":
            self._sync_menu()
        
        elif command == "voice":
            self._voice_menu()
        
        elif command == "security":
            self._security_menu()
        
        elif command.startswith("dixie"):
            self._handle_emergency_word(command)
        
        else:
            logger.info("❓ Comando no reconocido. Escribe 'help' para ayuda")
    
    def _show_help(self):
        """Muestra ayuda"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    JARVIS FASE 1 - COMANDOS                   ║
╚════════════════════════════════════════════════════════════════╝

📋 COMANDOS DISPONIBLES:

  help          - Muestra esta ayuda
  status        - Muestra estado de todos los módulos
  vault         - Acceder al vault de secretos
  sync          - Sincronización con Google Drive
  voice         - Gestión de voz y tono
  security      - Opciones de seguridad
  dixie         - PALABRA DE SEGURIDAD (apagado forzado)
  salir         - Terminar Jarvis

🔐 SEGURIDAD:

  La palabra de seguridad es: "Dixie"
  Úsala para apagar el sistema en caso de emergencia
  Ejemplo: dixie

⚠️  IMPORTANTE:

  - Todos los datos se guardan encriptados
  - La sincronización con Drive es automática
  - El reconocimiento de voz es local
  - Los intentos de exposición de datos disparan apagado

╔════════════════════════════════════════════════════════════════╗
        """)
    
    def _show_status(self):
        """Muestra estado de módulos"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    ESTADO DE MÓDULOS                          ║
╚════════════════════════════════════════════════════════════════╝
""")
        
        # Security
        security = self.modules['security']
        print(f"🔐 Security Manager:")
        print(f"   Estado: {'✓ Activo' if security else '✗ Inactivo'}")
        print(f"   Compromised: {security.is_system_compromised()}")
        print(f"   Exposición intentos: {len(security.get_exposure_attempts())}")
        
        # Shutdown
        shutdown = self.modules['shutdown']
        print(f"\n🚨 Emergency Shutdown:")
        print(f"   Estado: {'✓ Activo' if shutdown else '✗ Inactivo'}")
        print(f"   Intentos fallidos: {shutdown.failed_attempts}/{shutdown.max_failed_attempts}")
        
        # Sync
        sync = self.modules['sync']
        print(f"\n🔄 Drive Sync:")
        print(f"   Estado: {'✓ Activo' if sync else '✗ No disponible'}")
        if sync:
            print(f"   Última sincronización: {sync.get_last_sync_time()}")
        
        # Voice
        voice = self.modules['voice']
        print(f"\n🎤 Voice Manager:")
        print(f"   Estado: {'✓ Activo' if voice else '✗ No disponible'}")
        if voice:
            profile = voice.get_emotional_profile()
            print(f"   Emociones detectadas: {profile}")
        
        print("\n" + "=" * 60)
    
    def _vault_menu(self):
        """Menú del vault"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    VAULT DE SECRETOS                          ║
╚════════════════════════════════════════════════════════════════╝

1. Almacenar secreto
2. Obtener secreto
3. Ver log de acceso
4. Volver
        """)
        
        choice = input("Elige opción (1-4): ").strip()
        
        if choice == "1":
            key = input("Clave del secreto: ").strip()
            value = input("Valor del secreto: ").strip()
            category = input("Categoría (default: general): ").strip() or "general"
            
            if self.modules['security'].store_secret(key, value, category):
                print("✓ Secreto almacenado")
            else:
                print("✗ Error almacenando secreto")
        
        elif choice == "2":
            key = input("Clave del secreto: ").strip()
            value = self.modules['security'].get_secret(key, self.user_id)
            if value:
                print(f"✓ Secreto: {value[:20]}...")
            else:
                print("✗ Secreto no encontrado")
        
        elif choice == "3":
            log = self.modules['security'].get_access_log()
            print(f"\n📋 Log de acceso ({len(log)} registros):")
            for entry in log[-5:]:  # Últimos 5
                print(f"  {entry}")
    
    def _sync_menu(self):
        """Menú de sincronización"""
        if not self.modules['sync']:
            print("✗ Sincronización no disponible")
            return
        
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    SINCRONIZACIÓN DRIVE                       ║
╚════════════════════════════════════════════════════════════════╝

1. Subir memoria
2. Descargar memoria
3. Sincronización bidireccional
4. Ver historial
5. Volver
        """)
        
        choice = input("Elige opción (1-5): ").strip()
        
        if choice == "1":
            if self.modules['sync'].upload_memory():
                print("✓ Memoria subida")
            else:
                print("✗ Error subiendo memoria")
        
        elif choice == "2":
            data = self.modules['sync'].download_memory()
            if data:
                print(f"✓ Memoria descargada: {len(str(data))} bytes")
            else:
                print("✗ Error descargando memoria")
        
        elif choice == "3":
            if self.modules['sync'].sync_bidirectional():
                print("✓ Sincronización completada")
            else:
                print("✗ Error en sincronización")
        
        elif choice == "4":
            history = self.modules['sync'].get_sync_history()
            print(f"\n📋 Historial ({len(history)} eventos):")
            for event in history[-5:]:
                print(f"  {event}")
    
    def _voice_menu(self):
        """Menú de voz"""
        if not self.modules['voice']:
            print("✗ Voice Manager no disponible")
            return
        
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    GESTOR DE VOZ                              ║
╚════════════════════════════════════════════════════════════════╝

1. Grabar audio
2. Reconocer voz
3. Analizar tono
4. Ver perfil emocional
5. Volver
        """)
        
        choice = input("Elige opción (1-5): ").strip()
        
        if choice == "1":
            filepath = self.modules['voice'].record_audio(duration=3)
            print(f"✓ Audio grabado: {filepath}")
        
        elif choice == "2":
            text = self.modules['voice'].recognize_speech(timeout=5)
            print(f"✓ Texto: {text}")
        
        elif choice == "3":
            audio_file = input("Ruta del archivo de audio: ").strip()
            if os.path.exists(audio_file):
                result = self.modules['voice'].analyze_tone(audio_file)
                print(f"✓ Emoción: {result.get('emotion', {}).get('emotion')}")
            else:
                print("✗ Archivo no encontrado")
        
        elif choice == "4":
            profile = self.modules['voice'].get_emotional_profile()
            print(f"\n😊 Perfil Emocional:")
            for emotion, percentage in profile.items():
                print(f"  {emotion}: {percentage:.1%}")
    
    def _security_menu(self):
        """Menú de seguridad"""
        print("""
╔════════════════════════════════════════════════════════════════╗
║                    OPCIONES DE SEGURIDAD                      ║
╚════════════════════════════════════════════════════════════════╝

1. Ver log de seguridad
2. Ver intentos de exposición
3. Estado del sistema
4. Volver
        """)
        
        choice = input("Elige opción (1-4): ").strip()
        
        if choice == "1":
            log = self.modules['shutdown'].get_security_log()
            print(f"\n🔐 Log de seguridad ({len(log)} eventos):")
            for event in log[-10:]:
                print(f"  {event}")
        
        elif choice == "2":
            attempts = self.modules['security'].get_exposure_attempts()
            print(f"\n⚠️  Intentos de exposición ({len(attempts)}):")
            for attempt in attempts:
                print(f"  {attempt}")
        
        elif choice == "3":
            compromised = self.modules['security'].is_system_compromised()
            print(f"\n🔒 Estado del sistema:")
            print(f"   Comprometido: {'✗ SÍ' if compromised else '✓ NO'}")
    
    def _handle_emergency_word(self, command: str):
        """Maneja la palabra de seguridad"""
        # Extraer palabra (formato: "dixie palabra_aqui")
        parts = command.split(maxsplit=1)
        
        if len(parts) < 2:
            print("⚠️  Uso: dixie <palabra_de_seguridad>")
            return
        
        word = parts[1]
        
        if self.modules['shutdown'].verify_emergency_word(word):
            print("✓ Palabra verificada - Apagando...")
            self.modules['shutdown'].emergency_shutdown("user_command")
        else:
            print("✗ Palabra incorrecta")
    
    def _cleanup_on_shutdown(self):
        """Callback de limpieza al apagar"""
        logger.info("🧹 Ejecutando limpieza...")
        
        # Sincronizar antes de apagar
        if self.modules['sync']:
            try:
                self.modules['sync'].upload_memory()
                logger.info("✓ Última sincronización completada")
            except Exception as e:
                logger.warning(f"⚠ Error en sincronización final: {e}")
    
    def stop(self):
        """Detiene Jarvis"""
        self.is_running = False
        logger.info("👋 Jarvis detenido")


def main():
    """Función principal"""
    try:
        # Crear instancia de Jarvis
        jarvis = JarvisCore(
            master_password="jarvis_master_2024",
            emergency_word="Dixie",
            user_id="eli"
        )
        
        # Iniciar
        jarvis.start()
    
    except KeyboardInterrupt:
        logger.info("\n⏹ Interrupción")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
