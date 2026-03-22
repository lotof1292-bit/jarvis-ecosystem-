# 📚 JARVIS FASE 4 - API REST DOCUMENTATION

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Health Check

**GET** `/health`

Verificar salud del servicio.

**Response:**
```json
{
  "status": "ok",
  "local_available": true,
  "manus_available": true,
  "timestamp": "2026-03-22 16:30:00"
}
```

---

### 2. Chat

**POST** `/chat`

Procesar un mensaje de chat.

**Request:**
```json
{
  "message": "¿Qué es machine learning?",
  "context": "Conversación anterior"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Machine learning es...",
  "complexity": {
    "level": "MODERATE",
    "score": 0.45,
    "details": {...}
  },
  "source": "local",
  "recommendation": {...},
  "timestamp": "2026-03-22 16:30:00"
}
```

---

### 3. Batch Chat

**POST** `/chat/batch`

Procesar múltiples mensajes.

**Request:**
```json
{
  "messages": [
    "¿Qué hora es?",
    "Explica qué es IA",
    "Diseña una arquitectura"
  ],
  "context": "Contexto general"
}
```

**Response:**
```json
{
  "results": [
    {...},
    {...},
    {...}
  ]
}
```

---

### 4. Analyze Complexity

**POST** `/complexity`

Analizar complejidad de un mensaje sin procesarlo.

**Request:**
```json
{
  "message": "Diseña una arquitectura para...",
  "context": "Contexto"
}
```

**Response:**
```json
{
  "level": "ADVANCED",
  "score": 0.85,
  "details": {
    "level": "ADVANCED",
    "score": 0.85,
    "message_length": 25,
    "requires_manus": true,
    "can_use_local": false,
    "estimated_time_ms": 3000,
    "reasoning": "Contiene palabras clave avanzadas | Requiere conexión a Manus"
  },
  "recommendation": {
    "primary": "manus",
    "fallback": "local",
    "use_manus": true,
    "priority": "quality"
  }
}
```

---

### 5. Statistics

**GET** `/stats`

Obtener estadísticas del sistema.

**Response:**
```json
{
  "local_chat_available": true,
  "manus_available": true,
  "stats": {
    "total_queries": 42,
    "local_queries": 35,
    "manus_queries": 5,
    "cache_hits": 2,
    "start_time": "2026-03-22 16:00:00"
  },
  "local_stats": {...},
  "manus_stats": {...}
}
```

---

### 6. History

**GET** `/history?limit=10`

Obtener historial de conversación.

**Query Parameters:**
- `limit` (int, default=10): Número de mensajes

**Response:**
```json
{
  "count": 10,
  "messages": [
    {
      "role": "user",
      "content": "¿Qué hora es?",
      "timestamp": "2026-03-22 16:30:00"
    },
    {
      "role": "assistant",
      "content": "Son las 16:30",
      "timestamp": "2026-03-22 16:30:01"
    }
  ]
}
```

---

### 7. Clear History

**POST** `/history/clear`

Limpiar historial de conversación.

**Response:**
```json
{
  "message": "Historial limpiado"
}
```

---

### 8. Cache Statistics

**GET** `/cache/stats`

Obtener estadísticas del caché.

**Response:**
```json
{
  "cache_size": 15,
  "cache_ttl": 3600,
  "total_items": 15,
  "expired_items": 0
}
```

---

### 9. Clear Cache

**POST** `/cache/clear`

Limpiar caché de respuestas.

**Response:**
```json
{
  "message": "Caché limpiado"
}
```

---

### 10. Get Configuration

**GET** `/config`

Obtener configuración actual.

**Response:**
```json
{
  "local_model": "mistral:7b",
  "ollama_url": "http://localhost:11434",
  "manus_url": "https://api.manus.im",
  "threshold_moderate": 0.4,
  "threshold_advanced": 0.7,
  "cache_ttl": 3600,
  "offline_mode": true
}
```

---

### 11. Update Configuration

**PUT** `/config`

Actualizar configuración.

**Request:**
```json
{
  "threshold_advanced": 0.8,
  "cache_ttl": 7200
}
```

**Response:**
```json
{
  "message": "Configuración actualizada",
  "config": {...}
}
```

---

### 12. Test Manus Connection

**GET** `/manus/test`

Probar conexión a Manus.

**Response:**
```json
{
  "success": true,
  "available": true,
  "response_time": "2026-03-22 16:30:00",
  "message": "Conexión exitosa"
}
```

---

### 13. Test Local Chat

**GET** `/local/test`

Probar chat local.

**Response:**
```json
{
  "success": true,
  "response": "Hola, estoy disponible",
  "complexity": "simple",
  "timestamp": "2026-03-22 16:30:00",
  "model": "mistral:7b"
}
```

---

### 14. System Status

**GET** `/status`

Obtener estado completo del sistema.

**Response:**
```json
{
  "status": "running",
  "system": {...},
  "timestamp": "2026-03-22 16:30:00"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Mensaje vacío"
}
```

### 404 Not Found
```json
{
  "error": "Endpoint no encontrado"
}
```

### 500 Internal Server Error
```json
{
  "error": "Error interno del servidor"
}
```

---

## Ejemplos de Uso

### Python

```python
import requests

# Chat simple
response = requests.post('http://localhost:5000/chat', json={
    'message': '¿Qué hora es?'
})
print(response.json())

# Analizar complejidad
response = requests.post('http://localhost:5000/complexity', json={
    'message': 'Diseña una arquitectura'
})
print(response.json())

# Obtener estadísticas
response = requests.get('http://localhost:5000/stats')
print(response.json())
```

### cURL

```bash
# Chat
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué hora es?"}'

# Estadísticas
curl http://localhost:5000/stats

# Historial
curl http://localhost:5000/history?limit=5
```

### JavaScript

```javascript
// Chat
fetch('http://localhost:5000/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({message: '¿Qué hora es?'})
})
.then(r => r.json())
.then(data => console.log(data))

// Estadísticas
fetch('http://localhost:5000/stats')
.then(r => r.json())
.then(data => console.log(data))
```

---

## Autenticación

Actualmente sin autenticación. Para producción, agregar:

```python
from flask_httpauth import HTTPBearerAuth
auth = HTTPBearerAuth()

@app.before_request
@auth.login_required
def verify_token():
    pass
```

---

## Rate Limiting

Actualmente sin límite. Para producción, agregar:

```python
from flask_limiter import Limiter
limiter = Limiter(app)

@app.route('/chat', methods=['POST'])
@limiter.limit("10 per minute")
def chat():
    pass
```

---

## Documentación Interactiva

Acceder a Swagger UI:

```
http://localhost:5000/api/docs
```

(Requiere instalar `flask-swagger-ui`)

---

**Última actualización**: Marzo 22, 2026
