# 🕵️ JARVIS FASE 5 - MITM (Man in the Middle) GUIDE

## ¿Qué es MITM?

**Man in the Middle** es una técnica que permite interceptar, monitorear y modificar comunicaciones entre dispositivos en tiempo real.

---

## 🎯 Características

✅ **Interceptación Pasiva** - Solo monitorear tráfico  
✅ **Interceptación Activa** - Modificar comandos  
✅ **Bloqueo de Comandos** - Prevenir acciones específicas  
✅ **Inyección de Comandos** - Insertar comandos adicionales  
✅ **Detección de Anomalías** - Identificar comportamientos sospechosos  
✅ **Análisis de Patrones** - Entender flujos de comunicación  
✅ **Blacklist/Whitelist** - Control de dispositivos  
✅ **Servidor Proxy** - Interceptar tráfico HTTP  

---

## 📋 Modos de Operación

### 1. PASSIVE (Pasivo)
Solo monitorea el tráfico sin modificarlo.

```python
mitm = MITMInterceptor(mode=InterceptionMode.PASSIVE)
```

**Casos de uso:**
- Auditoría de seguridad
- Análisis de patrones
- Debugging

### 2. ACTIVE (Activo)
Modifica comandos según reglas.

```python
mitm = MITMInterceptor(mode=InterceptionMode.ACTIVE)
```

**Casos de uso:**
- Aplicar políticas de seguridad
- Proteger dispositivos
- Optimizar comandos

### 3. BLOCKING (Bloqueo)
Bloquea comandos específicos.

```python
mitm = MITMInterceptor(mode=InterceptionMode.BLOCKING)
```

**Casos de uso:**
- Prevenir acciones peligrosas
- Control parental
- Protección de dispositivos

### 4. INJECTION (Inyección)
Inyecta comandos adicionales.

```python
mitm = MITMInterceptor(mode=InterceptionMode.INJECTION)
```

**Casos de uso:**
- Automatización
- Testing
- Análisis de seguridad

---

## 🔧 Uso Básico

### Crear Interceptor

```python
from mitm.mitm_interceptor import MITMInterceptor, InterceptionMode

# Crear en modo activo
mitm = MITMInterceptor(mode=InterceptionMode.ACTIVE)
```

### Agregar Reglas

```python
# Regla 1: Modificar brillo
mitm.add_rule('rule_brightness', {
    'source': '*',                    # Cualquier origen
    'target': '192.168.1.50',         # Dispositivo específico
    'command': 'set_brightness',      # Comando específico
    'action': 'modify',               # Acción
    'modification': {                 # Modificación
        'brightness': 100             # Siempre al máximo
    },
    'enabled': True
})

# Regla 2: Bloquear apagado
mitm.add_rule('rule_block_off', {
    'source': '*',
    'target': '192.168.1.50',
    'command': 'turn_off',
    'action': 'block',
    'enabled': True
})

# Regla 3: Inyectar comando
mitm.add_rule('rule_inject_log', {
    'source': '*',
    'target': '*',
    'command': '*',
    'action': 'inject',
    'enabled': True
})
```

### Interceptar Comandos

```python
# Interceptar comando
allow, modified = mitm.intercept_command(
    source='192.168.1.100',           # Origen
    target='192.168.1.50',            # Destino
    command='set_brightness',         # Comando
    params={'brightness': 50}         # Parámetros
)

if allow:
    print(f"✅ Permitido")
    print(f"Modificado: {modified}")
else:
    print(f"🚫 Bloqueado")
```

### Usar Blacklist/Whitelist

```python
# Agregar a blacklist (bloquear dispositivo)
mitm.add_to_blacklist('192.168.1.100')

# Agregar a whitelist (permitir solo estos)
mitm.add_to_whitelist('192.168.1.50')
mitm.add_to_whitelist('192.168.1.51')
```

---

## 🌐 Servidor Proxy

### Iniciar Proxy

```python
from mitm.mitm_proxy import MITMProxyServer

# Crear servidor
proxy = MITMProxyServer(host='0.0.0.0', port=8888)

# Agregar reglas
proxy.add_rule('rule_brightness', {...})

# Iniciar
proxy.start()
```

### Usar Proxy

```bash
# Configurar dispositivo para usar proxy
# En M5Stack o Kode Dot:
# - IP: 192.168.1.100 (PC con Jarvis)
# - Puerto: 8888

# Todos los comandos pasarán por el proxy
```

---

## 📊 Análisis de Tráfico

### Obtener Log de Tráfico

```python
# Últimos 100 comandos
log = mitm.get_traffic_log(limit=100)

# Tráfico de dispositivo específico
device_traffic = mitm.get_traffic_by_device('192.168.1.50')

# Tráfico de comando específico
command_traffic = mitm.get_traffic_by_command('set_brightness')
```

### Analizar Patrones

```python
analysis = mitm.analyze_traffic_patterns()

print(f"Total de comandos: {analysis['total_commands']}")
print(f"Dispositivos únicos: {analysis['unique_sources']}")
print(f"Comandos únicos: {analysis['unique_commands']}")
print(f"Frecuencia: {analysis['command_frequency']}")
```

### Exportar Log

```python
# Exportar a archivo JSON
mitm.export_traffic_log('traffic_log.json')
```

---

## 🚨 Detección de Anomalías

El sistema detecta automáticamente:

1. **Comandos Repetidos** - Mismo comando muchas veces
2. **Nuevos Dispositivos** - Dispositivos desconocidos
3. **Patrones Sospechosos** - Comportamiento anómalo

```python
# Registrar callback para anomalías
def on_anomaly(data):
    print(f"⚠️ Anomalía detectada: {data}")

mitm.register_callback('anomaly_detected', on_anomaly)
```

---

## 🔒 Casos de Uso de Seguridad

### Caso 1: Proteger Dispositivo

```python
# Bloquear apagado accidental
mitm.add_rule('protect_device', {
    'source': '*',
    'target': '192.168.1.50',
    'command': 'turn_off',
    'action': 'block',
    'enabled': True
})
```

### Caso 2: Control Parental

```python
# Permitir solo ciertos dispositivos
mitm.add_to_whitelist('192.168.1.50')  # Solo TV
mitm.add_to_whitelist('192.168.1.51')  # Solo Luces

# Bloquear todo lo demás
```

### Caso 3: Auditoría

```python
# Modo pasivo para auditar
mitm = MITMInterceptor(mode=InterceptionMode.PASSIVE)

# Monitorear todo
allow, modified = mitm.intercept_command(...)

# Exportar para análisis
mitm.export_traffic_log('audit.json')
```

### Caso 4: Testing

```python
# Inyectar comandos de prueba
mitm.add_rule('test_injection', {
    'source': 'test_suite',
    'target': '*',
    'command': '*',
    'action': 'inject',
    'enabled': True
})
```

---

## 📈 Estadísticas

```python
stats = mitm.get_stats()

print(f"Total interceptado: {stats['total_intercepted']}")
print(f"Modificados: {stats['commands_modified']}")
print(f"Bloqueados: {stats['commands_blocked']}")
print(f"Inyectados: {stats['commands_injected']}")
print(f"Anomalías: {stats['anomalies_detected']}")
```

---

## 🔄 Integración con Jarvis

```python
from mitm.mitm_integration import MITMController

# Crear controlador MITM
mitm_controller = MITMController(executor)

# Ejecutar con MITM
result = mitm_controller.execute_with_mitm(
    'set_brightness',
    {'brightness': 50},
    '192.168.1.50'
)

# Habilitar/Deshabilitar
mitm_controller.enable_mitm()
mitm_controller.disable_mitm()
```

---

## ⚠️ Consideraciones de Seguridad

1. **Encriptación**: MITM puede ser detectado si hay encriptación
2. **Autenticación**: Implementar autenticación para comandos críticos
3. **Logging**: Registrar todas las acciones
4. **Auditoría**: Revisar logs regularmente
5. **Permisos**: Usar whitelist en lugar de blacklist cuando sea posible

---

## 🎯 Ejemplos Completos

### Ejemplo 1: Proteger Dispositivo

```python
from mitm.mitm_interceptor import MITMInterceptor, InterceptionMode

mitm = MITMInterceptor(mode=InterceptionMode.ACTIVE)

# Bloquear apagado
mitm.add_rule('block_off', {
    'source': '*',
    'target': '192.168.1.50',
    'command': 'turn_off',
    'action': 'block',
    'enabled': True
})

# Limitar brillo
mitm.add_rule('limit_brightness', {
    'source': '*',
    'target': '192.168.1.50',
    'command': 'set_brightness',
    'action': 'modify',
    'modification': {'brightness': 80},
    'enabled': True
})

# Probar
allow, _ = mitm.intercept_command('user', '192.168.1.50', 'turn_off')
print(f"Apagado permitido: {allow}")  # False

allow, modified = mitm.intercept_command('user', '192.168.1.50', 'set_brightness', {'brightness': 100})
print(f"Brillo modificado a: {modified['params']['brightness']}")  # 80
```

### Ejemplo 2: Auditoría

```python
mitm = MITMInterceptor(mode=InterceptionMode.PASSIVE)

# Monitorear todo
commands = [
    ('192.168.1.100', '192.168.1.50', 'turn_on', {}),
    ('192.168.1.100', '192.168.1.50', 'set_brightness', {'brightness': 75}),
    ('192.168.1.101', '192.168.1.51', 'turn_on', {}),
]

for source, target, cmd, params in commands:
    mitm.intercept_command(source, target, cmd, params)

# Analizar
analysis = mitm.analyze_traffic_patterns()
print(f"Dispositivos únicos: {analysis['unique_sources']}")

# Exportar
mitm.export_traffic_log('audit.json')
```

---

**¡MITM está listo para usar! 🕵️**
