"""
JARVIS VOICE & TONE ANALYSIS MODULE - FASE 1
Reconocimiento de voz y análisis de tono emocional
Módulo Independiente - No depende de otros
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
import speech_recognition as sr
import librosa
import soundfile as sf
from scipy import signal

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [VOICE] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/jarvis-phase1/logs/voice.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class JarvisVoiceManager:
    """
    Gestor de Voz y Análisis de Tono
    - Reconocimiento de voz (Speech-to-Text)
    - Análisis de tono emocional
    - Síntesis de voz (Text-to-Speech)
    - Detección de intenciones por tono
    """
    
    def __init__(self, 
                 language: str = "es-ES",
                 audio_path: str = "/home/ubuntu/jarvis-phase1/config/audio",
                 tone_model_path: str = "/home/ubuntu/jarvis-phase1/ai/tone_model.json"):
        """
        Inicializa el gestor de voz
        
        Args:
            language: Idioma para reconocimiento (es-ES, en-US, etc)
            audio_path: Ruta para almacenar archivos de audio
            tone_model_path: Ruta del modelo de análisis de tono
        """
        self.language = language
        self.audio_path = audio_path
        self.tone_model_path = tone_model_path
        self.recognizer = sr.Recognizer()
        self.voice_profile = {}
        self.tone_history = []
        
        # Crear directorio de audio si no existe
        os.makedirs(audio_path, exist_ok=True)
        
        # Cargar o crear modelo de tono
        self._load_tone_model()
        
        logger.info("✓ Voice Manager inicializado")
    
    def _load_tone_model(self):
        """Carga o crea modelo de análisis de tono"""
        if os.path.exists(self.tone_model_path):
            try:
                with open(self.tone_model_path, 'r') as f:
                    self.tone_model = json.load(f)
                logger.info("✓ Modelo de tono cargado")
            except Exception as e:
                logger.warning(f"⚠ Error cargando modelo: {e}")
                self._create_default_tone_model()
        else:
            self._create_default_tone_model()
    
    def _create_default_tone_model(self):
        """Crea modelo de tono por defecto"""
        self.tone_model = {
            "emotions": {
                "alegria": {
                    "pitch_range": (150, 250),
                    "energy": (0.6, 1.0),
                    "speed": (1.1, 1.5),
                    "confidence": 0.8
                },
                "tristeza": {
                    "pitch_range": (80, 150),
                    "energy": (0.2, 0.5),
                    "speed": (0.7, 0.9),
                    "confidence": 0.8
                },
                "enojo": {
                    "pitch_range": (180, 300),
                    "energy": (0.8, 1.0),
                    "speed": (1.2, 1.6),
                    "confidence": 0.85
                },
                "miedo": {
                    "pitch_range": (120, 200),
                    "energy": (0.5, 0.8),
                    "speed": (1.3, 1.7),
                    "confidence": 0.75
                },
                "calma": {
                    "pitch_range": (100, 150),
                    "energy": (0.3, 0.6),
                    "speed": (0.8, 1.0),
                    "confidence": 0.8
                }
            }
        }
        
        # Guardar modelo
        os.makedirs(os.path.dirname(self.tone_model_path), exist_ok=True)
        with open(self.tone_model_path, 'w') as f:
            json.dump(self.tone_model, f, indent=4)
        
        logger.info("✓ Modelo de tono creado")
    
    def recognize_speech(self, audio_source=None, timeout: int = 10) -> str:
        """
        Reconoce voz del micrófono o archivo
        
        Args:
            audio_source: Archivo de audio (si None, usa micrófono)
            timeout: Timeout en segundos
        
        Returns:
            Texto reconocido
        """
        try:
            if audio_source is None:
                # Usar micrófono
                with sr.Microphone() as source:
                    logger.info("🎤 Escuchando...")
                    audio = self.recognizer.listen(source, timeout=timeout)
            else:
                # Usar archivo
                with sr.AudioFile(audio_source) as source:
                    audio = self.recognizer.record(source)
            
            # Reconocer con Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=self.language)
            logger.info(f"✓ Texto reconocido: {text}")
            
            return text
        except sr.UnknownValueError:
            logger.warning("✗ No se pudo entender el audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"✗ Error en servicio de reconocimiento: {e}")
            return ""
        except Exception as e:
            logger.error(f"✗ Error reconociendo voz: {e}")
            return ""
    
    def analyze_tone(self, audio_source: str) -> dict:
        """
        Analiza el tono emocional del audio
        
        Args:
            audio_source: Ruta del archivo de audio
        
        Returns:
            Dict con análisis de tono
        """
        try:
            # Cargar audio
            y, sr_rate = librosa.load(audio_source, sr=None)
            
            # Extraer características
            features = self._extract_audio_features(y, sr_rate)
            
            # Clasificar emoción
            emotion = self._classify_emotion(features)
            
            # Crear registro
            tone_record = {
                "timestamp": datetime.now().isoformat(),
                "audio_file": audio_source,
                "emotion": emotion,
                "features": features,
                "confidence": emotion.get("confidence", 0)
            }
            
            self.tone_history.append(tone_record)
            
            logger.info(f"✓ Tono analizado: {emotion['emotion']} ({emotion['confidence']:.2%})")
            
            return tone_record
        except Exception as e:
            logger.error(f"✗ Error analizando tono: {e}")
            return {}
    
    def _extract_audio_features(self, y: np.ndarray, sr_rate: int) -> dict:
        """Extrae características de audio"""
        try:
            # Pitch (fundamental frequency)
            S = librosa.feature.melspectrogram(y=y, sr=sr_rate)
            S_db = librosa.power_to_db(S, ref=np.max)
            
            # Centroide espectral (pitch promedio)
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr_rate)[0]
            pitch = np.mean(spectral_centroid)
            
            # Energía
            energy = np.sqrt(np.mean(y**2))
            
            # Velocidad (tasa de cambio de energía)
            energy_envelope = np.abs(signal.hilbert(y))
            speed = np.std(np.diff(energy_envelope))
            
            # MFCC (Mel-frequency cepstral coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            
            return {
                "pitch": float(pitch),
                "energy": float(energy),
                "speed": float(speed),
                "mfcc": mfcc_mean.tolist()
            }
        except Exception as e:
            logger.error(f"✗ Error extrayendo características: {e}")
            return {}
    
    def _classify_emotion(self, features: dict) -> dict:
        """Clasifica emoción basada en características"""
        try:
            best_emotion = None
            best_score = 0
            
            for emotion_name, emotion_params in self.tone_model["emotions"].items():
                # Calcular score
                score = 0
                
                # Pitch score
                pitch_range = emotion_params["pitch_range"]
                if pitch_range[0] <= features["pitch"] <= pitch_range[1]:
                    score += 0.3
                
                # Energy score
                energy_range = emotion_params["energy"]
                if energy_range[0] <= features["energy"] <= energy_range[1]:
                    score += 0.3
                
                # Speed score
                speed_range = emotion_params["speed"]
                if speed_range[0] <= features["speed"] <= speed_range[1]:
                    score += 0.4
                
                if score > best_score:
                    best_score = score
                    best_emotion = emotion_name
            
            confidence = min(best_score / 1.0, 1.0)
            
            return {
                "emotion": best_emotion or "neutral",
                "confidence": confidence,
                "score": best_score
            }
        except Exception as e:
            logger.error(f"✗ Error clasificando emoción: {e}")
            return {"emotion": "neutral", "confidence": 0, "score": 0}
    
    def record_audio(self, duration: int = 5, filename: str = None) -> str:
        """
        Graba audio del micrófono
        
        Args:
            duration: Duración en segundos
            filename: Nombre del archivo (si None, genera automático)
        
        Returns:
            Ruta del archivo grabado
        """
        try:
            if filename is None:
                filename = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            filepath = os.path.join(self.audio_path, filename)
            
            logger.info(f"🎤 Grabando por {duration} segundos...")
            
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=duration)
            
            with open(filepath, "wb") as f:
                f.write(audio.get_wav_data())
            
            logger.info(f"✓ Audio grabado: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"✗ Error grabando audio: {e}")
            return ""
    
    def get_tone_history(self) -> list:
        """Retorna historial de análisis de tono"""
        return self.tone_history
    
    def get_emotional_profile(self) -> dict:
        """Retorna perfil emocional basado en historial"""
        if not self.tone_history:
            return {}
        
        emotions = {}
        for record in self.tone_history:
            emotion = record["emotion"]["emotion"]
            if emotion not in emotions:
                emotions[emotion] = 0
            emotions[emotion] += 1
        
        total = sum(emotions.values())
        return {
            emotion: count / total 
            for emotion, count in emotions.items()
        }


if __name__ == "__main__":
    print("=" * 60)
    print("JARVIS VOICE & TONE MODULE - TEST")
    print("=" * 60)
    
    # Inicializar
    voice = JarvisVoiceManager()
    
    print("\nOpciones de test:")
    print("1. Grabar audio")
    print("2. Reconocer voz (micrófono)")
    print("3. Analizar tono")
    
    choice = input("\nElige opción (1-3): ").strip()
    
    if choice == "1":
        filepath = voice.record_audio(duration=3)
        print(f"✓ Audio grabado: {filepath}")
    elif choice == "2":
        text = voice.recognize_speech(timeout=5)
        print(f"✓ Texto: {text}")
    elif choice == "3":
        print("⚠ Necesita archivo de audio para analizar")
    
    print("\n✓ Módulo de voz listo")
