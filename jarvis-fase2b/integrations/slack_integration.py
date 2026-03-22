"""
SLACK INTEGRATION - Integración con Slack
Envía y recibe mensajes
"""

import logging
from typing import Dict, List, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


class SlackIntegration:
    """Integración con Slack"""
    
    def __init__(self, token: str):
        self.token = token
        self.client = WebClient(token=token)
        self.user_info = None
        self.connect()
    
    def connect(self):
        """Conectar con Slack"""
        try:
            self.user_info = self.client.auth_test()
            logger.info(f"✅ Slack conectado: {self.user_info['user_id']}")
        except SlackApiError as e:
            logger.error(f"❌ Error conectando a Slack: {e}")
    
    def get_channels(self) -> List[Dict]:
        """Obtener lista de canales"""
        try:
            channels = []
            result = self.client.conversations_list()
            
            for channel in result['channels']:
                channels.append({
                    'id': channel['id'],
                    'name': channel['name'],
                    'is_private': channel['is_private'],
                    'topic': channel.get('topic', {}).get('value', ''),
                    'purpose': channel.get('purpose', {}).get('value', ''),
                    'members': channel.get('num_members', 0)
                })
            
            logger.info(f"✅ {len(channels)} canales obtenidos")
            return channels
        
        except SlackApiError as e:
            logger.error(f"❌ Error obteniendo canales: {e}")
            return []
    
    def send_message(self, channel: str, text: str, thread_ts: Optional[str] = None) -> Optional[Dict]:
        """Enviar mensaje a canal"""
        try:
            result = self.client.chat_postMessage(
                channel=channel,
                text=text,
                thread_ts=thread_ts
            )
            
            logger.info(f"✅ Mensaje enviado a {channel}")
            return {
                'channel': result['channel'],
                'ts': result['ts'],
                'message': text
            }
        
        except SlackApiError as e:
            logger.error(f"❌ Error enviando mensaje: {e}")
            return None
    
    def get_messages(self, channel: str, limit: int = 10) -> List[Dict]:
        """Obtener mensajes de un canal"""
        try:
            messages = []
            result = self.client.conversations_history(channel=channel, limit=limit)
            
            for msg in result['messages']:
                messages.append({
                    'user': msg.get('user', 'bot'),
                    'text': msg.get('text', ''),
                    'ts': msg['ts'],
                    'thread_ts': msg.get('thread_ts'),
                    'reactions': msg.get('reactions', [])
                })
            
            logger.info(f"✅ {len(messages)} mensajes obtenidos de {channel}")
            return messages
        
        except SlackApiError as e:
            logger.error(f"❌ Error obteniendo mensajes: {e}")
            return []
    
    def get_direct_messages(self) -> List[Dict]:
        """Obtener conversaciones directas"""
        try:
            dms = []
            result = self.client.conversations_list(types='im')
            
            for dm in result['channels']:
                user_id = dm['user']
                user_info = self.client.users_info(user=user_id)
                
                dms.append({
                    'id': dm['id'],
                    'user': user_info['user']['real_name'],
                    'user_id': user_id,
                    'is_open': dm['is_open']
                })
            
            logger.info(f"✅ {len(dms)} DMs obtenidos")
            return dms
        
        except SlackApiError as e:
            logger.error(f"❌ Error obteniendo DMs: {e}")
            return []
    
    def send_direct_message(self, user_id: str, text: str) -> Optional[Dict]:
        """Enviar mensaje directo"""
        try:
            # Abrir DM
            dm = self.client.conversations_open(users=user_id)
            channel_id = dm['channel']['id']
            
            # Enviar mensaje
            result = self.client.chat_postMessage(
                channel=channel_id,
                text=text
            )
            
            logger.info(f"✅ DM enviado a {user_id}")
            return {
                'channel': channel_id,
                'ts': result['ts'],
                'message': text
            }
        
        except SlackApiError as e:
            logger.error(f"❌ Error enviando DM: {e}")
            return None
    
    def get_user_info(self, user_id: str) -> Optional[Dict]:
        """Obtener información de usuario"""
        try:
            result = self.client.users_info(user=user_id)
            user = result['user']
            
            return {
                'id': user['id'],
                'name': user['name'],
                'real_name': user['real_name'],
                'email': user.get('profile', {}).get('email'),
                'phone': user.get('profile', {}).get('phone'),
                'status': user.get('profile', {}).get('status_text'),
                'avatar': user.get('profile', {}).get('image_72')
            }
        
        except SlackApiError as e:
            logger.error(f"❌ Error obteniendo info de usuario: {e}")
            return None
    
    def create_channel(self, name: str, is_private: bool = False) -> Optional[Dict]:
        """Crear nuevo canal"""
        try:
            result = self.client.conversations_create(
                name=name,
                is_private=is_private
            )
            
            logger.info(f"✅ Canal creado: {name}")
            return {
                'id': result['channel']['id'],
                'name': result['channel']['name'],
                'is_private': result['channel']['is_private']
            }
        
        except SlackApiError as e:
            logger.error(f"❌ Error creando canal: {e}")
            return None
    
    def add_reaction(self, channel: str, ts: str, emoji: str) -> bool:
        """Agregar reacción a mensaje"""
        try:
            self.client.reactions_add(
                channel=channel,
                timestamp=ts,
                name=emoji
            )
            logger.info(f"✅ Reacción agregada: :{emoji}:")
            return True
        
        except SlackApiError as e:
            logger.error(f"❌ Error agregando reacción: {e}")
            return False
    
    def set_status(self, status_text: str, emoji: str = ':robot_face:') -> bool:
        """Establecer estado del usuario"""
        try:
            self.client.users_setPresence(presence='auto')
            self.client.users_profile_set(
                profile={
                    'status_text': status_text,
                    'status_emoji': emoji
                }
            )
            logger.info(f"✅ Estado actualizado: {status_text}")
            return True
        
        except SlackApiError as e:
            logger.error(f"❌ Error actualizando estado: {e}")
            return False
    
    def search_messages(self, query: str) -> List[Dict]:
        """Buscar mensajes"""
        try:
            results = []
            result = self.client.search_messages(query=query)
            
            for match in result['messages']['matches'][:10]:
                results.append({
                    'text': match['text'],
                    'channel': match['channel']['name'],
                    'user': match.get('user', 'bot'),
                    'ts': match['ts']
                })
            
            logger.info(f"✅ {len(results)} mensajes encontrados")
            return results
        
        except SlackApiError as e:
            logger.error(f"❌ Error buscando mensajes: {e}")
            return []
    
    def upload_file(self, channel: str, file_path: str, title: str = '') -> Optional[Dict]:
        """Subir archivo a canal"""
        try:
            with open(file_path, 'rb') as f:
                result = self.client.files_upload_v2(
                    channel=channel,
                    file=f,
                    title=title or file_path.split('/')[-1]
                )
            
            logger.info(f"✅ Archivo subido a {channel}")
            return {
                'id': result['file']['id'],
                'name': result['file']['name'],
                'url': result['file']['permalink']
            }
        
        except Exception as e:
            logger.error(f"❌ Error subiendo archivo: {e}")
            return None
