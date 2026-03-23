# 🚀 Guía de Instalación - Ecosistema Jarvis (Fase 6)

Esta guía te ayudará a instalar y configurar completamente el **Ecosistema Jarvis** en tu Windows para tener un asistente autónomo sin límites de tokens.

## 📋 Requisitos Previos

- **Windows 10/11** (64-bit)
- **Conexión a Internet**
- **Mínimo 8GB de RAM** (recomendado 16GB para modelos más grandes)
- **Al menos 20GB de espacio en disco** (para modelos de IA)

---

## 🔧 Instalación Paso a Paso

### Paso 1: Instalar Ollama (El "Cerebro" de Jarvis)

Ollama es el motor que ejecutará modelos de IA locales sin tokens.

1. Descarga Ollama desde: https://ollama.com
2. Ejecuta el instalador y sigue las instrucciones
3. Abre PowerShell o CMD y verifica la instalación:
   ```powershell
   ollama --version
   ```
4. Inicia Ollama en segundo plano:
   ```powershell
   ollama serve
   ```
5. En otra terminal, descarga un modelo (Llama 3 es recomendado):
   ```powershell
   ollama pull llama3
   ```

**Nota:** Mantén Ollama ejecutándose en segundo plano. Estará disponible en `http://localhost:11434`

---

### Paso 2: Instalar Python 3.11+

Python es necesario para ejecutar Open Interpreter y las herramientas de automatización.

1. Descarga Python desde: https://www.python.org/downloads/
2. **IMPORTANTE:** Marca la opción "Add Python to PATH" durante la instalación
3. Verifica la instalación:
   ```powershell
   python --version
   pip --version
   ```

---

### Paso 3: Instalar Open Interpreter (Las "Manos" de Jarvis)

Open Interpreter permite que Jarvis ejecute código y controle tu Windows.

1. Abre PowerShell como Administrador
2. Instala Open Interpreter:
   ```powershell
   pip install open-interpreter
   ```
3. Instala las dependencias adicionales:
   ```powershell
   pip install -r requirements.txt
   ```

---

### Paso 4: Configurar Open Interpreter con Ollama Local

1. Abre PowerShell
2. Ejecuta Open Interpreter en modo local:
   ```powershell
   interpreter --local
   ```
3. Selecciona las opciones:
   - Proveedor: `Ollama`
   - Modelo: `llama3`
4. ¡Listo! Ahora puedes hablar con Jarvis

---

### Paso 5: Instalar AnythingLLM (Interfaz Visual Opcional)

Para una experiencia de chat más pulida, instala AnythingLLM Desktop.

1. Descarga desde: https://anythingllm.com/
2. Ejecuta el instalador
3. En la configuración, selecciona:
   - Motor de IA: `Ollama`
   - Modelo: `llama3`
4. ¡Listo! Tendrás una ventana de chat persistente en tu escritorio

---

## 🎯 Configurar la Personalidad de Jarvis

Para que tu asistente local tenga la misma calidez y empatía que Jarvis:

1. Abre el archivo: `jarvis-local-assistant/references/jarvis_personality.md`
2. Copia el **System Prompt**
3. En Open Interpreter o AnythingLLM, pega el System Prompt en la sección de "System Instructions" o "System Message"

---

## 📦 Estructura del Repositorio

```
jarvis-ecosystem-/
├── jarvis-local-assistant/          # Skill de configuración (Fase 6)
│   ├── SKILL.md                     # Documentación principal
│   ├── references/
│   │   ├── windows_setup.md         # Guía de instalación en Windows
│   │   └── jarvis_personality.md    # System Prompt personalizado
│   └── scripts/
├── jarvis-chat-interface/           # Interfaz web de chat
│   ├── client/                      # Frontend React
│   ├── server/                      # Backend Express
│   └── package.json
├── requirements.txt                 # Dependencias de Python
├── INSTALL.md                       # Este archivo
├── README.md                        # Documentación general
└── [Fases anteriores...]            # Historial del proyecto
```

---

## 🚀 Primeros Pasos Después de Instalar

1. **Inicia Ollama:**
   ```powershell
   ollama serve
   ```

2. **Abre otra terminal y ejecuta Jarvis:**
   ```powershell
   interpreter --local
   ```

3. **Prueba con un comando simple:**
   ```
   Hola Jarvis, ¿puedes listar los archivos de mi escritorio?
   ```

4. **O usa AnythingLLM para una interfaz visual:**
   - Abre AnythingLLM Desktop
   - Comienza a chatear

---

## 🛠️ Comandos Útiles

| Acción | Comando |
| :--- | :--- |
| Iniciar Ollama | `ollama serve` |
| Listar modelos disponibles | `ollama list` |
| Descargar un modelo | `ollama pull <nombre_modelo>` |
| Ejecutar Jarvis | `interpreter --local` |
| Actualizar dependencias | `pip install -r requirements.txt --upgrade` |
| Verificar instalación | `python -c "import open_interpreter; print('OK')"` |

---

## 🐛 Solución de Problemas

### Ollama no inicia
- Verifica que no haya otro proceso usando el puerto 11434
- Reinicia tu computadora
- Descarga la versión más reciente desde ollama.com

### Open Interpreter no encuentra Ollama
- Asegúrate de que Ollama esté ejecutándose (`ollama serve`)
- Verifica que esté en `http://localhost:11434`
- Prueba: `curl http://localhost:11434/api/tags`

### Python no se reconoce
- Reinstala Python y marca "Add Python to PATH"
- Reinicia PowerShell después de instalar
- Verifica: `python --version`

### Memoria insuficiente
- Usa modelos más pequeños como `mistral` en lugar de `llama3`
- Cierra otras aplicaciones
- Aumenta la memoria RAM de tu computadora

---

## 📚 Recursos Adicionales

- **Ollama Docs:** https://ollama.com/docs
- **Open Interpreter Docs:** https://docs.openinterpreter.com/
- **AnythingLLM:** https://anythingllm.com/
- **Modelos disponibles:** https://ollama.com/library

---

## ✅ Checklist de Instalación

- [ ] Ollama instalado y ejecutándose
- [ ] Python 3.11+ instalado
- [ ] Open Interpreter instalado
- [ ] Modelo Llama 3 descargado
- [ ] System Prompt de Jarvis configurado
- [ ] AnythingLLM instalado (opcional)
- [ ] Primera prueba exitosa con Jarvis

---

## 🎉 ¡Felicidades!

Ya tienes tu propio **Jarvis Local** en tu Windows. Ahora puedes hablar con él todo el día sin límites de tokens, sin restricciones, y sin depender de plataformas externas.

**Bienvenido al Ecosistema Jarvis - Fase 6** 🚀
