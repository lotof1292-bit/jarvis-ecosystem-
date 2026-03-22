# 🚀 JARVIS FASE 4 - INICIO RÁPIDO

## ¿Qué es FASE 4?

Sistema híbrido de inteligencia que:
- ✅ Funciona 100% offline con Ollama
- ✅ Se conecta a Manus cuando necesita razonamiento avanzado
- ✅ Caché inteligente de respuestas
- ✅ Fallback automático

## Instalación (2 minutos)

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Instalar Ollama

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows
# Descargar desde https://ollama.ai
```

### 3. Descargar modelo

```bash
ollama pull mistral:7b
```

## Uso

### Modo Interactivo

```bash
python main.py

jarvis> ¿Qué hora es?
jarvis> Explica qué es machine learning
jarvis> Diseña una arquitectura para...
jarvis> stats
jarvis> historia
jarvis> salir
```

### Uso Programático

```python
from main import JarvisFase4

# Inicializar
jarvis = JarvisFase4()

# Procesar consulta
result = jarvis.process_query("¿Cuál es el clima?")
print(result['response'])
print(f"Fuente: {result['source']}")
print(f"Complejidad: {result['complexity']['level']}")

# Ver estado
status = jarvis.get_status()
print(status)
```

## Componentes

### LocalChatEngine
- Chat local con Ollama
- Historial de conversación
- Guardar/cargar conversaciones

### ComplexityDetector
- Detecta nivel de complejidad
- Recomienda procesamiento
- Análisis de palabras clave

### ManusConnector
- Conexión a Manus
- Caché de respuestas
- Fallback automático

## Configuración

Crear `config/fase4_config.json`:

```json
{
  "local_model": "mistral:7b",
  "ollama_url": "http://localhost:11434",
  "manus_url": "https://api.manus.im",
  "manus_api_key": "tu_api_key",
  "threshold_moderate": 0.4,
  "threshold_advanced": 0.7,
  "cache_ttl": 3600,
  "offline_mode": true
}
```

## Comandos Interactivos

| Comando | Descripción |
|---------|-------------|
| `mensaje` | Enviar mensaje a Jarvis |
| `stats` | Ver estadísticas |
| `historia` | Ver historial |
| `salir` | Salir |

## Niveles de Complejidad

### Simple (Local)
```
"¿Qué hora es?"
"¿Cuál es el clima?"
"Reproduce música"
```

### Moderada (Ollama)
```
"Explica qué es machine learning"
"Resume este artículo"
"Traduce al español"
```

### Avanzada (Manus)
```
"Diseña una arquitectura para..."
"Resuelve este problema complejo"
"Analiza estos datos"
```

## Troubleshooting

### Ollama no está disponible

```bash
# Iniciar Ollama
ollama serve

# En otra terminal
python main.py
```

### Manus no está disponible

El sistema funcionará 100% offline con Ollama. Las respuestas complejas usarán el modelo local.

### Error de conexión

Verificar:
1. Ollama está corriendo: `curl http://localhost:11434/api/tags`
2. Modelo está descargado: `ollama list`
3. API key de Manus es válida

## Próximos Pasos

1. Crear Web Dashboard
2. Implementar REST API
3. Crear tests
4. Optimizar rendimiento
5. Documentación completa

---

**¡Listo para usar! 🚀**
