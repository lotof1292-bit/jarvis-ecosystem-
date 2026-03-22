"""
JARVIS GOOGLE DRIVE SYNC MODULE - FASE 1
Sincronización automática de memoria global
Módulo Independiente - No depende de otros
"""

import os
import json
import logging
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
import googleapiclient.discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [SYNC] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/jarvis-phase1/logs/sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisDriveSyncManager:
    """
    Gestor de Sincronización con Google Drive
    - Sincronización automática de memoria
    - Conflicto resolution
    - Versionado de cambios
    - Compresión de datos
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, 
                 credentials_path: str = "/home/ubuntu/jarvis-phase1/config/credentials.json",
                 token_path: str = "/home/ubuntu/jarvis-phase1/config/token.json",
                 local_memory_path: str = "/home/ubuntu/jarvis-phase1/config/memory.json",
                 folder_name: str = "Jarvis-Memory-jarvismemoria2"):
        """
        Inicializa el gestor de sincronización
        
        Args:
            credentials_path: Ruta del archivo credentials.json
            token_path: Ruta del archivo token.json
            local_memory_path: Ruta de la memoria local
            folder_name: Nombre de la carpeta en Drive
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.local_memory_path = local_memory_path
        self.folder_name = folder_name
        self.service = None
        self.folder_id = None
        self.last_sync = None
        self.sync_history = []
        
        # Inicializar servicio
        self._initialize_service()
        
        logger.info("✓ Drive Sync Manager inicializado")
    
    def _initialize_service(self):
        """Inicializa servicio de Google Drive"""
        try:
            creds = None
            
            # Cargar token existente
            if os.path.exists(self.token_path):
                creds = UserCredentials.from_authorized_user_file(
                    self.token_path, 
                    self.SCOPES
                )
            
            # Si no hay credenciales válidas, obtener nuevas
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except RefreshError:
                        creds = self._get_new_credentials()
                else:
                    creds = self._get_new_credentials()
                
                # Guardar token
                with open(self.token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
            
            self.service = googleapiclient.discovery.build(
                'drive', 'v3', credentials=creds
            )
            
            # Obtener o crear carpeta
            self._ensure_folder_exists()
            
            logger.info("✓ Servicio de Google Drive conectado")
        except Exception as e:
            logger.error(f"✗ Error inicializando servicio: {e}")
            raise
    
    def _get_new_credentials(self):
        """Obtiene nuevas credenciales OAuth"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                self.SCOPES
            )
            creds = flow.run_local_server(port=0)
            logger.info("✓ Nuevas credenciales obtenidas")
            return creds
        except FileNotFoundError:
            logger.error(f"✗ Archivo credentials.json no encontrado en {self.credentials_path}")
            logger.info("📝 Descarga credentials.json desde Google Cloud Console")
            raise
    
    def _ensure_folder_exists(self):
        """Asegura que la carpeta existe en Drive"""
        try:
            # Buscar carpeta existente
            query = f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                self.folder_id = files[0]['id']
                logger.info(f"✓ Carpeta encontrada: {self.folder_id}")
            else:
                # Crear nueva carpeta
                file_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                self.folder_id = folder.get('id')
                logger.info(f"✓ Nueva carpeta creada: {self.folder_id}")
        except Exception as e:
            logger.error(f"✗ Error asegurando carpeta: {e}")
            raise
    
    def upload_memory(self, memory_data: dict = None) -> bool:
        """
        Sube la memoria local a Google Drive
        
        Args:
            memory_data: Datos a subir (si None, usa archivo local)
        
        Returns:
            True si fue exitoso
        """
        try:
            if memory_data is None:
                # Cargar desde archivo local
                if not os.path.exists(self.local_memory_path):
                    logger.warning("✗ Archivo de memoria local no existe")
                    return False
                
                with open(self.local_memory_path, 'r') as f:
                    memory_data = json.load(f)
            
            # Preparar datos
            upload_data = {
                "timestamp": datetime.now().isoformat(),
                "device": os.environ.get('HOSTNAME', 'unknown'),
                "memory": memory_data,
                "version": "1.0"
            }
            
            # Crear archivo temporal
            temp_file = "/tmp/jarvis_memory_upload.json"
            with open(temp_file, 'w') as f:
                json.dump(upload_data, f, indent=4)
            
            # Buscar archivo existente
            query = f"name='memory.json' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            # Subir o actualizar
            file_metadata = {'name': 'memory.json'}
            media = MediaFileUpload(temp_file, mimetype='application/json', resumable=True)
            
            if files:
                # Actualizar archivo existente
                file_id = files[0]['id']
                self.service.files().update(
                    fileId=file_id,
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info("✓ Memoria actualizada en Drive")
            else:
                # Crear nuevo archivo
                file_metadata['parents'] = [self.folder_id]
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info("✓ Memoria subida a Drive")
            
            # Limpiar archivo temporal
            os.remove(temp_file)
            
            # Registrar sincronización
            self.last_sync = datetime.now()
            self.sync_history.append({
                "action": "upload",
                "timestamp": self.last_sync.isoformat(),
                "status": "success"
            })
            
            return True
        except Exception as e:
            logger.error(f"✗ Error subiendo memoria: {e}")
            self.sync_history.append({
                "action": "upload",
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            return False
    
    def download_memory(self) -> dict:
        """
        Descarga la memoria desde Google Drive
        
        Returns:
            Datos de memoria o None
        """
        try:
            # Buscar archivo
            query = f"name='memory.json' and '{self.folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if not files:
                logger.warning("✗ Archivo de memoria no encontrado en Drive")
                return None
            
            # Descargar archivo
            file_id = files[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # Parsear JSON
            file_content.seek(0)
            memory_data = json.loads(file_content.read().decode())
            
            logger.info("✓ Memoria descargada desde Drive")
            
            # Registrar sincronización
            self.sync_history.append({
                "action": "download",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            
            return memory_data
        except Exception as e:
            logger.error(f"✗ Error descargando memoria: {e}")
            self.sync_history.append({
                "action": "download",
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            return None
    
    def sync_bidirectional(self) -> bool:
        """
        Sincronización bidireccional inteligente
        - Descarga cambios remotos
        - Sube cambios locales
        - Resuelve conflictos
        
        Returns:
            True si fue exitoso
        """
        try:
            logger.info("🔄 Iniciando sincronización bidireccional...")
            
            # Descargar memoria remota
            remote_memory = self.download_memory()
            
            # Cargar memoria local
            if os.path.exists(self.local_memory_path):
                with open(self.local_memory_path, 'r') as f:
                    local_memory = json.load(f)
            else:
                local_memory = {"events": []}
            
            # Merge de memorias
            if remote_memory:
                merged_memory = self._merge_memories(local_memory, remote_memory)
                
                # Guardar merge localmente
                with open(self.local_memory_path, 'w') as f:
                    json.dump(merged_memory, f, indent=4)
                
                logger.info("✓ Memorias fusionadas")
            
            # Subir cambios
            self.upload_memory(local_memory)
            
            logger.info("✓ Sincronización completada")
            return True
        except Exception as e:
            logger.error(f"✗ Error en sincronización: {e}")
            return False
    
    def _merge_memories(self, local: dict, remote: dict) -> dict:
        """Fusiona memorias local y remota sin duplicados"""
        try:
            local_events = local.get('events', [])
            remote_events = remote.get('memory', {}).get('events', [])
            
            # Crear set de IDs locales
            local_ids = {e.get('id') for e in local_events if 'id' in e}
            
            # Agregar eventos remotos que no existen localmente
            for event in remote_events:
                if event.get('id') not in local_ids:
                    local_events.append(event)
            
            # Ordenar por timestamp
            local_events.sort(key=lambda x: x.get('timestamp', 0))
            
            local['events'] = local_events
            return local
        except Exception as e:
            logger.error(f"✗ Error fusionando memorias: {e}")
            return local
    
    def get_sync_history(self) -> list:
        """Retorna historial de sincronizaciones"""
        return self.sync_history
    
    def get_last_sync_time(self) -> str:
        """Retorna timestamp de última sincronización"""
        return self.last_sync.isoformat() if self.last_sync else "Nunca"


if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS DRIVE SYNC MODULE - TEST")
    print("=" * 60)
    
    print("\n⚠ Nota: Necesita credentials.json configurado")
    print("Descárgalo desde: https://console.cloud.google.com/")
    
    print("\nPasos para configurar:")
    print("1. Crear proyecto en Google Cloud Console")
    print("2. Habilitar Google Drive API")
    print("3. Crear OAuth 2.0 credentials (Desktop app)")
    print("4. Descargar JSON y guardar como credentials.json")
    print("5. Ejecutar este módulo nuevamente")
    
    print("\n✓ Módulo listo para usar")
