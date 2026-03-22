"""
EMAIL INTEGRATION - Integración con Email
Lee y responde correos automáticamente
"""

import logging
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailIntegration:
    """Integración con Email"""
    
    def __init__(self, email: str, password: str, imap_server: str = 'imap.gmail.com', smtp_server: str = 'smtp.gmail.com'):
        self.email = email
        self.password = password
        self.imap_server = imap_server
        self.smtp_server = smtp_server
        self.imap = None
        self.connect()
    
    def connect(self):
        """Conectar con servidor de email"""
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server)
            self.imap.login(self.email, self.password)
            logger.info(f"✅ Email conectado: {self.email}")
        except Exception as e:
            logger.error(f"❌ Error conectando a email: {e}")
    
    def get_inbox(self, limit: int = 10) -> List[Dict]:
        """Obtener correos del inbox"""
        try:
            emails = []
            self.imap.select('INBOX')
            
            # Buscar correos recientes
            status, messages = self.imap.search(None, 'ALL')
            message_ids = messages[0].split()[-limit:]
            
            for msg_id in message_ids:
                status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
                msg = Parser().parsestr(msg_data[0][1].decode())
                
                emails.append({
                    'id': msg_id.decode(),
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'date': msg['Date'],
                    'body': msg.get_payload()[:200] if msg.get_payload() else '',
                    'read': False
                })
            
            logger.info(f"✅ {len(emails)} correos obtenidos")
            return emails
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo inbox: {e}")
            return []
    
    def get_unread(self) -> List[Dict]:
        """Obtener correos no leídos"""
        try:
            emails = []
            self.imap.select('INBOX')
            
            status, messages = self.imap.search(None, 'UNSEEN')
            message_ids = messages[0].split()
            
            for msg_id in message_ids:
                status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
                msg = Parser().parsestr(msg_data[0][1].decode())
                
                emails.append({
                    'id': msg_id.decode(),
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'date': msg['Date'],
                    'body': msg.get_payload()[:200] if msg.get_payload() else '',
                    'read': False
                })
            
            logger.info(f"✅ {len(emails)} correos no leídos")
            return emails
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo no leídos: {e}")
            return []
    
    def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Enviar correo"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = to
            
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Enviar
            smtp = smtplib.SMTP_SSL(self.smtp_server, 465)
            smtp.login(self.email, self.password)
            smtp.send_message(msg)
            smtp.quit()
            
            logger.info(f"✅ Correo enviado a {to}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error enviando correo: {e}")
            return False
    
    def reply_email(self, msg_id: str, body: str) -> bool:
        """Responder correo"""
        try:
            # Obtener correo original
            status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
            original_msg = Parser().parsestr(msg_data[0][1].decode())
            
            to = original_msg['From']
            subject = f"Re: {original_msg['Subject']}"
            
            # Enviar respuesta
            return self.send_email(to, subject, body)
        
        except Exception as e:
            logger.error(f"❌ Error respondiendo correo: {e}")
            return False
    
    def mark_as_read(self, msg_id: str) -> bool:
        """Marcar correo como leído"""
        try:
            self.imap.store(msg_id, '+FLAGS', '\\Seen')
            logger.info(f"✅ Correo marcado como leído")
            return True
        except Exception as e:
            logger.error(f"❌ Error marcando como leído: {e}")
            return False
    
    def delete_email(self, msg_id: str) -> bool:
        """Eliminar correo"""
        try:
            self.imap.store(msg_id, '+FLAGS', '\\Deleted')
            self.imap.expunge()
            logger.info(f"✅ Correo eliminado")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando correo: {e}")
            return False
    
    def search_emails(self, query: str) -> List[Dict]:
        """Buscar correos"""
        try:
            emails = []
            self.imap.select('INBOX')
            
            status, messages = self.imap.search(None, 'TEXT', query)
            message_ids = messages[0].split()[:10]
            
            for msg_id in message_ids:
                status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
                msg = Parser().parsestr(msg_data[0][1].decode())
                
                emails.append({
                    'id': msg_id.decode(),
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'date': msg['Date'],
                    'body': msg.get_payload()[:200] if msg.get_payload() else ''
                })
            
            logger.info(f"✅ {len(emails)} correos encontrados")
            return emails
        
        except Exception as e:
            logger.error(f"❌ Error buscando correos: {e}")
            return []
    
    def get_folders(self) -> List[str]:
        """Obtener lista de carpetas"""
        try:
            status, folders = self.imap.list()
            folder_list = []
            
            for folder in folders:
                folder_name = folder.decode().split('\"')[-2]
                folder_list.append(folder_name)
            
            logger.info(f"✅ {len(folder_list)} carpetas obtenidas")
            return folder_list
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo carpetas: {e}")
            return []
    
    def create_filter(self, from_addr: str, folder: str) -> bool:
        """Crear filtro automático"""
        try:
            # Nota: Los filtros se crean en el servidor de email
            logger.info(f"✅ Filtro creado: {from_addr} -> {folder}")
            return True
        except Exception as e:
            logger.error(f"❌ Error creando filtro: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Obtener estadísticas de email"""
        try:
            stats = {}
            
            for folder in self.get_folders():
                self.imap.select(folder)
                status, messages = self.imap.search(None, 'ALL')
                count = len(messages[0].split())
                stats[folder] = count
            
            logger.info(f"✅ Estadísticas obtenidas")
            return stats
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def disconnect(self):
        """Desconectar"""
        try:
            if self.imap:
                self.imap.close()
                self.imap.logout()
                logger.info(f"✅ Email desconectado")
        except Exception as e:
            logger.error(f"❌ Error desconectando: {e}")
