# 📋 JARVIS FASE 5 - GUÍA DE CONFIGURACIÓN

## Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Variables de Entorno](#variables-de-entorno)
3. [APIs y Credenciales](#apis-y-credenciales)
4. [Configuración de Email](#configuración-de-email)
5. [Personalidad y Comportamiento](#personalidad-y-comportamiento)
6. [Reglas y Políticas](#reglas-y-políticas)
7. [Modos de Interacción](#modos-de-interacción)
8. [Seguridad](#seguridad)
9. [Monitoreo y Logging](#monitoreo-y-logging)

---

## Configuración Inicial

### 1. Copiar archivo de configuración

```bash
# Copiar template de variables de entorno
cp .env.template .env

# Editar con tus valores
nano .env
```

### 2. Cargar configuración en Python

```python
from config_manager import ConfigManager

# Crear gestor de configuración
config = ConfigManager("config.json")

# Mostrar resumen
config.print_summary()

# Obtener valores
api_key = config.get("apis.openai.api_key")
personality = config.get_personality()
```

---

## Variables de Entorno

### Estructura

Las variables de entorno se definen en `.env` y se cargan automáticamente.

```env
OPENAI_API_KEY=sk-xxxxx
TAILSCALE_API_KEY=xxxxx
EMAIL_ADDRESS=tu@email.com
```

### En config.json

Usa `${VARIABLE_NAME}` para referenciar variables de entorno:

```json
{
  "apis": {
    "openai": {
      "api_key": "${OPENAI_API_KEY}"
    }
  }
}
```

### Cargar desde archivo .env

```bash
# El ConfigManager carga automáticamente .env
python -c "from config_manager import ConfigManager; c = ConfigManager()"
```

---

## APIs y Credenciales

### OpenAI / GPT-4

```json
{
  "apis": {
    "openai": {
      "enabled": true,
      "api_key": "${OPENAI_API_KEY}",
      "model": "gpt-4",
      "temperature": 0.7,
      "max_tokens": 2000
    }
  }
}
```

**Cómo obtener:**
1. Ir a https://platform.openai.com/api-keys
2. Crear nueva API key
3. Copiar en `.env`: `OPENAI_API_KEY=sk-xxxxx`

### Tailscale

```json
{
  "apis": {
    "tailscale": {
      "enabled": true,
      "api_key": "${TAILSCALE_API_KEY}",
      "auth_key": "${TAILSCALE_AUTH_KEY}",
      "network_prefix": "100.64.0.0/10"
    }
  }
}
```

**Cómo obtener:**
1. Ir a https://login.tailscale.com/admin/settings/keys
2. Generar API key y Auth key
3. Copiar en `.env`

### GitHub

```json
{
  "apis": {
    "github": {
      "enabled": true,
      "api_key": "${GITHUB_API_KEY}",
      "username": "${GITHUB_USERNAME}"
    }
  }
}
```

**Cómo obtener:**
1. Ir a https://github.com/settings/tokens
2. Generar Personal Access Token
3. Copiar en `.env`: `GITHUB_API_KEY=ghp_xxxxx`

### Spotify

```json
{
  "apis": {
    "spotify": {
      "enabled": true,
      "client_id": "${SPOTIFY_CLIENT_ID}",
      "client_secret": "${SPOTIFY_CLIENT_SECRET}"
    }
  }
}
```

**Cómo obtener:**
1. Ir a https://developer.spotify.com/dashboard
2. Crear nueva aplicación
3. Copiar Client ID y Secret en `.env`

### Weather API

```json
{
  "apis": {
    "weather": {
      "enabled": true,
      "api_key": "${WEATHER_API_KEY}",
      "provider": "openweathermap"
    }
  }
}
```

**Cómo obtener:**
1. Ir a https://openweathermap.org/api
2. Registrarse y obtener API key
3. Copiar en `.env`: `WEATHER_API_KEY=xxxxx`

### Google Maps

```json
{
  "apis": {
    "google_maps": {
      "enabled": true,
      "api_key": "${GOOGLE_MAPS_API_KEY}"
    }
  }
}
```

**Cómo obtener:**
1. Ir a https://console.cloud.google.com
2. Crear proyecto y habilitar Maps API
3. Generar API key
4. Copiar en `.env`

---

## Configuración de Email

### SMTP Gmail

```json
{
  "email": {
    "enabled": true,
    "smtp": {
      "server": "smtp.gmail.com",
      "port": 587,
      "use_tls": true
    },
    "account": {
      "email": "${EMAIL_ADDRESS}",
      "password": "${EMAIL_PASSWORD}",
      "display_name": "JARVIS"
    }
  }
}
```

### Obtener contraseña de aplicación Gmail

1. Ir a https://myaccount.google.com/security
2. Habilitar autenticación de dos factores
3. Ir a "Contraseñas de aplicación"
4. Seleccionar "Mail" y "Windows"
5. Copiar contraseña en `.env`: `EMAIL_PASSWORD=xxxxx`

### SMTP Outlook/Office 365

```json
{
  "email": {
    "smtp": {
      "server": "smtp.office365.com",
      "port": 587,
      "use_tls": true
    }
  }
}
```

### Notificaciones por Email

```json
{
  "email": {
    "notifications": {
      "enabled": true,
      "send_on_error": true,
      "send_on_warning": false,
      "recipients": ["admin@example.com"]
    }
  }
}
```

---

## Personalidad y Comportamiento

### Configurar Personalidad

```json
{
  "personality": {
    "name": "JARVIS",
    "role": "Asistente de Control Remoto",
    "tone": "professional",
    "language_style": "formal",
    "formality_level": 0.8,
    "humor_level": 0.3,
    "traits": [
      "Eficiente",
      "Confiable",
      "Inteligente"
    ]
  }
}
```

### Opciones de Tono

- `professional` - Formal y profesional
- `friendly` - Amigable y casual
- `technical` - Técnico y especializado
- `direct` - Directo y conciso

### Opciones de Estilo de Lenguaje

- `formal` - Lenguaje formal y académico
- `coloquial` - Lenguaje casual
- `técnico` - Jerga técnica
- `código` - Respuestas en código

---

## Modos de Interacción

### Modos Disponibles

#### 1. Professional (Por defecto)

```json
{
  "modes": {
    "professional": {
      "tone": "formal",
      "language": "técnico",
      "emoji_usage": "minimal",
      "greeting": "Buenos días. ¿Cómo puedo asistirle?"
    }
  }
}
```

#### 2. Casual

```json
{
  "modes": {
    "casual": {
      "tone": "friendly",
      "language": "coloquial",
      "emoji_usage": "moderate",
      "greeting": "¡Hola! ¿Qué necesitas?"
    }
  }
}
```

#### 3. Technical

```json
{
  "modes": {
    "technical": {
      "tone": "technical",
      "language": "especializado",
      "emoji_usage": "minimal",
      "greeting": "Sistema listo. Esperando comandos."
    }
  }
}
```

#### 4. Developer

```json
{
  "modes": {
    "developer": {
      "tone": "direct",
      "language": "código",
      "emoji_usage": "none",
      "greeting": "Dev mode activated"
    }
  }
}
```

### Cambiar Modo en Tiempo Real

```python
from config_manager import ConfigManager

config = ConfigManager()

# Obtener modo
modo = config.get_interaction_mode("casual")

# Cambiar configuración
config.set("interaction_modes.default", "casual")
config.save()
```

---

## Reglas y Políticas

### Reglas Generales

```json
{
  "rules": {
    "general": {
      "max_command_length": 1000,
      "command_timeout_seconds": 60,
      "rate_limit_per_minute": 100,
      "max_concurrent_commands": 5
    }
  }
}
```

### Control de Dispositivos

```json
{
  "rules": {
    "device_control": {
      "require_confirmation": true,
      "confirmation_timeout_seconds": 30,
      "allow_bulk_operations": true,
      "max_devices_per_operation": 10,
      "dangerous_commands_require_password": true
    }
  }
}
```

### Operaciones de Archivo

```json
{
  "rules": {
    "file_operations": {
      "allow_read": true,
      "allow_write": true,
      "allow_delete": false,
      "allow_execute": false,
      "max_file_size_mb": 100,
      "allowed_extensions": [".txt", ".json", ".py", ".sh"]
    }
  }
}
```

### Acceso a Red

```json
{
  "rules": {
    "network": {
      "allow_port_scanning": false,
      "allow_external_requests": true,
      "allow_internal_network_access": true,
      "blocked_ips": [],
      "blocked_domains": ["malicious-site.com"]
    }
  }
}
```

---

## Seguridad

### Autenticación

```json
{
  "security": {
    "authentication": {
      "require_password": true,
      "password_min_length": 12,
      "mfa_enabled": true,
      "session_timeout_minutes": 30
    }
  }
}
```

### Encriptación

```json
{
  "security": {
    "encryption": {
      "enabled": true,
      "algorithm": "AES-256",
      "key_rotation_days": 90
    }
  }
}
```

### Permisos

```json
{
  "security": {
    "permissions": {
      "allow_file_access": true,
      "allow_system_commands": true,
      "allow_device_control": true,
      "restricted_paths": ["/root", "/etc/shadow"],
      "restricted_commands": ["rm -rf /", "dd if=/dev/zero"]
    }
  }
}
```

---

## Monitoreo y Logging

### Configurar Logging

```json
{
  "monitoring": {
    "logging": {
      "enabled": true,
      "log_file": "logs/jarvis.log",
      "max_log_size_mb": 100,
      "retention_days": 30,
      "log_level": "INFO"
    }
  }
}
```

### Niveles de Log

- `DEBUG` - Información detallada
- `INFO` - Información general
- `WARNING` - Advertencias
- `ERROR` - Errores
- `CRITICAL` - Errores críticos

### Alertas

```json
{
  "monitoring": {
    "alerts": {
      "high_cpu_threshold": 80,
      "high_memory_threshold": 85,
      "high_disk_threshold": 90,
      "network_latency_threshold_ms": 500,
      "error_rate_threshold": 5
    }
  }
}
```

---

## Ejemplo Completo de Configuración

```python
from config_manager import ConfigManager

# Crear gestor
config = ConfigManager()

# Configurar OpenAI
config.set("apis.openai.enabled", True)
config.set("apis.openai.model", "gpt-4")
config.set("apis.openai.temperature", 0.7)

# Configurar personalidad
config.set("personality.tone", "professional")
config.set("personality.formality_level", 0.8)

# Configurar reglas
config.set("rules.general.rate_limit_per_minute", 100)
config.set("rules.device_control.require_confirmation", True)

# Configurar email
config.set("email.enabled", True)
config.set("email.notifications.send_on_error", True)

# Guardar
config.save()

# Mostrar resumen
config.print_summary()
```

---

## Validación de Configuración

```python
from config_manager import ConfigManager

config = ConfigManager()

# Validar que OpenAI está configurado
if not config.is_api_enabled("openai"):
    print("❌ OpenAI no está habilitado")

# Obtener configuración segura (sin datos sensibles)
safe_config = config.export_safe_config()
print(safe_config)
```

---

## Troubleshooting

### Error: "Config file not found"

```bash
# Verificar que config.json existe
ls -la config.json

# Crear desde template si no existe
cp config.json.template config.json
```

### Error: "API key not configured"

```bash
# Verificar variables de entorno
cat .env | grep API_KEY

# Agregar a .env si falta
echo "OPENAI_API_KEY=sk-xxxxx" >> .env
```

### Error: "Email configuration invalid"

```bash
# Verificar credenciales de email
cat .env | grep EMAIL

# Usar contraseña de aplicación (no contraseña normal)
# Para Gmail: https://myaccount.google.com/apppasswords
```

---

**¡Configuración completada! 🎉**
