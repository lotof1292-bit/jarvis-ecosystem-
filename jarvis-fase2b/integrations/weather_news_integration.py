"""
WEATHER & NEWS INTEGRATION - Integración con Clima y Noticias
Obtiene información de clima y noticias en tiempo real
"""

import logging
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class WeatherIntegration:
    """Integración con OpenWeatherMap"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.openweathermap.org/data/2.5'
    
    def get_current_weather(self, city: str, units: str = 'metric') -> Optional[Dict]:
        """Obtener clima actual"""
        try:
            url = f'{self.base_url}/weather'
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'lang': 'es'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                weather = {
                    'city': data['name'],
                    'country': data['sys']['country'],
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'wind_speed': data['wind']['speed'],
                    'clouds': data['clouds']['all'],
                    'sunrise': data['sys']['sunrise'],
                    'sunset': data['sys']['sunset']
                }
                logger.info(f"✅ Clima obtenido para {city}")
                return weather
            else:
                logger.error(f"❌ Error: {data.get('message')}")
                return None
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo clima: {e}")
            return None
    
    def get_forecast(self, city: str, days: int = 5, units: str = 'metric') -> List[Dict]:
        """Obtener pronóstico"""
        try:
            url = f'{self.base_url}/forecast'
            params = {
                'q': city,
                'appid': self.api_key,
                'units': units,
                'lang': 'es',
                'cnt': days * 8  # 8 predicciones por día
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                forecast = []
                for item in data['list']:
                    forecast.append({
                        'date': item['dt_txt'],
                        'temperature': item['main']['temp'],
                        'description': item['weather'][0]['description'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed'],
                        'rain': item.get('rain', {}).get('3h', 0)
                    })
                
                logger.info(f"✅ Pronóstico obtenido para {city}")
                return forecast
            else:
                logger.error(f"❌ Error: {data.get('message')}")
                return []
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo pronóstico: {e}")
            return []
    
    def get_weather_by_coordinates(self, lat: float, lon: float, units: str = 'metric') -> Optional[Dict]:
        """Obtener clima por coordenadas"""
        try:
            url = f'{self.base_url}/weather'
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': units,
                'lang': 'es'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code == 200:
                weather = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed']
                }
                logger.info(f"✅ Clima obtenido por coordenadas")
                return weather
            else:
                return None
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return None
    
    def get_alerts(self, city: str) -> List[Dict]:
        """Obtener alertas de clima"""
        try:
            url = f'{self.base_url}/weather'
            params = {
                'q': city,
                'appid': self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            alerts = []
            if 'alerts' in data:
                for alert in data['alerts']:
                    alerts.append({
                        'event': alert['event'],
                        'start': alert['start'],
                        'end': alert['end'],
                        'description': alert['description']
                    })
            
            logger.info(f"✅ Alertas obtenidas")
            return alerts
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo alertas: {e}")
            return []


class NewsIntegration:
    """Integración con NewsAPI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://newsapi.org/v2'
    
    def get_top_headlines(self, country: str = 'us', category: str = 'general', limit: int = 10) -> List[Dict]:
        """Obtener noticias principales"""
        try:
            url = f'{self.base_url}/top-headlines'
            params = {
                'country': country,
                'category': category,
                'apiKey': self.api_key,
                'pageSize': limit
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok':
                articles = []
                for article in data['articles']:
                    articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'source': article['source']['name'],
                        'author': article.get('author'),
                        'url': article['url'],
                        'image': article.get('urlToImage'),
                        'published_at': article['publishedAt']
                    })
                
                logger.info(f"✅ {len(articles)} noticias principales obtenidas")
                return articles
            else:
                logger.error(f"❌ Error: {data.get('message')}")
                return []
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo noticias: {e}")
            return []
    
    def search_news(self, query: str, sort_by: str = 'relevancy', limit: int = 10) -> List[Dict]:
        """Buscar noticias"""
        try:
            url = f'{self.base_url}/everything'
            params = {
                'q': query,
                'sortBy': sort_by,
                'apiKey': self.api_key,
                'pageSize': limit,
                'language': 'es'
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok':
                articles = []
                for article in data['articles']:
                    articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'source': article['source']['name'],
                        'author': article.get('author'),
                        'url': article['url'],
                        'image': article.get('urlToImage'),
                        'published_at': article['publishedAt']
                    })
                
                logger.info(f"✅ {len(articles)} noticias encontradas")
                return articles
            else:
                return []
        
        except Exception as e:
            logger.error(f"❌ Error buscando noticias: {e}")
            return []
    
    def get_news_by_source(self, source: str, limit: int = 10) -> List[Dict]:
        """Obtener noticias de una fuente específica"""
        try:
            url = f'{self.base_url}/top-headlines'
            params = {
                'sources': source,
                'apiKey': self.api_key,
                'pageSize': limit
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok':
                articles = []
                for article in data['articles']:
                    articles.append({
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'image': article.get('urlToImage'),
                        'published_at': article['publishedAt']
                    })
                
                logger.info(f"✅ {len(articles)} noticias de {source} obtenidas")
                return articles
            else:
                return []
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
    
    def get_available_sources(self) -> List[Dict]:
        """Obtener fuentes disponibles"""
        try:
            url = f'{self.base_url}/sources'
            params = {'apiKey': self.api_key}
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok':
                sources = []
                for source in data['sources']:
                    sources.append({
                        'id': source['id'],
                        'name': source['name'],
                        'description': source['description'],
                        'url': source['url'],
                        'category': source['category'],
                        'country': source['country']
                    })
                
                logger.info(f"✅ {len(sources)} fuentes obtenidas")
                return sources
            else:
                return []
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return []
