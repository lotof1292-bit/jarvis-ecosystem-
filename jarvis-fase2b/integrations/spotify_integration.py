"""
SPOTIFY INTEGRATION - Integración con Spotify
Control de música y reproducción
"""

import logging
from typing import Dict, List, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth

logger = logging.getLogger(__name__)


class SpotifyIntegration:
    """Integración con Spotify"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = 'http://localhost:8888/callback'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.sp = None
        self.connect()
    
    def connect(self):
        """Conectar con Spotify"""
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope='user-read-playback-state user-modify-playback-state user-read-currently-playing'
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            logger.info(f"✅ Spotify conectado")
        except Exception as e:
            logger.error(f"❌ Error conectando a Spotify: {e}")
    
    def get_current_track(self) -> Optional[Dict]:
        """Obtener canción actual"""
        try:
            current = self.sp.current_playback()
            
            if current and current['item']:
                track = current['item']
                return {
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'duration': track['duration_ms'],
                    'progress': current['progress_ms'],
                    'is_playing': current['is_playing'],
                    'url': track['external_urls']['spotify']
                }
            
            logger.info(f"✅ Canción actual obtenida")
            return None
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo canción actual: {e}")
            return None
    
    def play(self, context_uri: Optional[str] = None, track_uris: Optional[List[str]] = None) -> bool:
        """Reproducir música"""
        try:
            if context_uri:
                self.sp.start_playback(context_uri=context_uri)
            elif track_uris:
                self.sp.start_playback(uris=track_uris)
            else:
                self.sp.start_playback()
            
            logger.info(f"✅ Reproducción iniciada")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error iniciando reproducción: {e}")
            return False
    
    def pause(self) -> bool:
        """Pausar música"""
        try:
            self.sp.pause_playback()
            logger.info(f"✅ Reproducción pausada")
            return True
        except Exception as e:
            logger.error(f"❌ Error pausando: {e}")
            return False
    
    def next_track(self) -> bool:
        """Siguiente canción"""
        try:
            self.sp.next_track()
            logger.info(f"✅ Siguiente canción")
            return True
        except Exception as e:
            logger.error(f"❌ Error en siguiente: {e}")
            return False
    
    def previous_track(self) -> bool:
        """Canción anterior"""
        try:
            self.sp.previous_track()
            logger.info(f"✅ Canción anterior")
            return True
        except Exception as e:
            logger.error(f"❌ Error en anterior: {e}")
            return False
    
    def set_volume(self, volume: int) -> bool:
        """Establecer volumen (0-100)"""
        try:
            self.sp.volume(volume)
            logger.info(f"✅ Volumen establecido a {volume}%")
            return True
        except Exception as e:
            logger.error(f"❌ Error estableciendo volumen: {e}")
            return False
    
    def search(self, query: str, search_type: str = 'track', limit: int = 10) -> List[Dict]:
        """Buscar en Spotify"""
        try:
            results = []
            search_results = self.sp.search(q=query, type=search_type, limit=limit)
            
            items = search_results[f'{search_type}s']['items']
            
            for item in items:
                if search_type == 'track':
                    results.append({
                        'name': item['name'],
                        'artist': item['artists'][0]['name'],
                        'album': item['album']['name'],
                        'uri': item['uri'],
                        'url': item['external_urls']['spotify']
                    })
                elif search_type == 'artist':
                    results.append({
                        'name': item['name'],
                        'uri': item['uri'],
                        'url': item['external_urls']['spotify']
                    })
                elif search_type == 'playlist':
                    results.append({
                        'name': item['name'],
                        'owner': item['owner']['display_name'],
                        'uri': item['uri'],
                        'url': item['external_urls']['spotify']
                    })
            
            logger.info(f"✅ {len(results)} resultados encontrados")
            return results
        
        except Exception as e:
            logger.error(f"❌ Error buscando: {e}")
            return []
    
    def get_playlists(self) -> List[Dict]:
        """Obtener playlists del usuario"""
        try:
            playlists = []
            results = self.sp.current_user_playlists()
            
            for playlist in results['items']:
                playlists.append({
                    'name': playlist['name'],
                    'uri': playlist['uri'],
                    'tracks': playlist['tracks']['total'],
                    'url': playlist['external_urls']['spotify']
                })
            
            logger.info(f"✅ {len(playlists)} playlists obtenidos")
            return playlists
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo playlists: {e}")
            return []
    
    def get_top_tracks(self, limit: int = 10) -> List[Dict]:
        """Obtener canciones top del usuario"""
        try:
            tracks = []
            results = self.sp.current_user_top_tracks(limit=limit)
            
            for track in results['items']:
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'uri': track['uri'],
                    'url': track['external_urls']['spotify']
                })
            
            logger.info(f"✅ {len(tracks)} canciones top obtenidas")
            return tracks
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo top tracks: {e}")
            return []
    
    def get_recommendations(self, seed_artists: List[str], limit: int = 10) -> List[Dict]:
        """Obtener recomendaciones"""
        try:
            recommendations = []
            results = self.sp.recommendations(seed_artists=seed_artists, limit=limit)
            
            for track in results['tracks']:
                recommendations.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'album': track['album']['name'],
                    'uri': track['uri'],
                    'url': track['external_urls']['spotify']
                })
            
            logger.info(f"✅ {len(recommendations)} recomendaciones obtenidas")
            return recommendations
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo recomendaciones: {e}")
            return []
    
    def add_to_playlist(self, playlist_id: str, track_uris: List[str]) -> bool:
        """Agregar canciones a playlist"""
        try:
            self.sp.playlist_add_items(playlist_id, track_uris)
            logger.info(f"✅ Canciones agregadas a playlist")
            return True
        except Exception as e:
            logger.error(f"❌ Error agregando a playlist: {e}")
            return False
    
    def create_playlist(self, name: str, description: str = '') -> Optional[Dict]:
        """Crear nueva playlist"""
        try:
            playlist = self.sp.user_playlist_create(
                self.sp.current_user()['id'],
                name,
                public=False,
                description=description
            )
            
            logger.info(f"✅ Playlist creada: {name}")
            return {
                'id': playlist['id'],
                'name': playlist['name'],
                'uri': playlist['uri'],
                'url': playlist['external_urls']['spotify']
            }
        
        except Exception as e:
            logger.error(f"❌ Error creando playlist: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """Obtener información del usuario"""
        try:
            user = self.sp.current_user()
            
            return {
                'id': user['id'],
                'display_name': user['display_name'],
                'email': user.get('email'),
                'followers': user['followers']['total'],
                'url': user['external_urls']['spotify']
            }
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo info: {e}")
            return None
