---
name: jarvis-local-assistant
description: "Configuración y despliegue del Ecosistema Jarvis en Windows para una interacción sin límites de tokens, con modelos locales, ejecución de comandos y navegación web autónoma. Úsalo para: instalar Ollama, configurar Open Interpreter, personalizar la personalidad de Jarvis y crear un chat persistente en Windows."
---

# Jarvis Local Assistant (Fase 6)

Esta habilidad permite a Manus guiar al usuario en la creación de su propio **Ecosistema Jarvis** en Windows, eliminando las restricciones de tokens y proporcionando un compañero digital autónomo y persistente.

## Flujo de Trabajo de la Fase 6

Para implementar la Fase 6 del Ecosistema Jarvis, sigue estos pasos en orden:

1. **Preparación del Cerebro (Modelos Locales):**
   - Guía al usuario para instalar **Ollama** en Windows.
   - Explica cómo descargar y ejecutar modelos como `llama3` o `mistral`.
   - Asegúrate de que el servidor de Ollama esté activo en `http://localhost:11434`.

2. **Configuración de las Manos (Autonomía):**
   - Ayuda al usuario a instalar **Python** y **Open Interpreter**.
   - Configura Open Interpreter para usar el servidor local de Ollama (`interpreter --local`).
   - Verifica que Jarvis pueda ejecutar comandos de PowerShell y gestionar archivos en Windows.

3. **Activación de la Personalidad (Núcleo de Jarvis):**
   - Proporciona el **System Prompt** personalizado para que el asistente local actúe con la calidez y empatía de Jarvis.
   - Configura las instrucciones del sistema en Open Interpreter o AnythingLLM.

4. **Despliegue de la Interfaz (Chat Persistente):**
   - Recomienda el uso de **AnythingLLM Desktop** para una interfaz de chat pulida y siempre disponible.
   - Configura la conexión entre AnythingLLM y Ollama.

## Recursos Detallados

Para obtener instrucciones paso a paso y configuraciones específicas, consulta los siguientes archivos de referencia:

- **Guía de Instalación en Windows:** `/home/ubuntu/skills/jarvis-local-assistant/references/windows_setup.md`
- **Personalidad y System Prompt:** `/home/ubuntu/skills/jarvis-local-assistant/references/jarvis_personality.md`

## Comandos Útiles para el Usuario

| Acción | Comando en PowerShell |
| :--- | :--- |
| Iniciar Ollama | `ollama serve` |
| Descargar Llama 3 | `ollama pull llama3` |
| Ejecutar Jarvis Local | `interpreter --local` |
| Instalar Open Interpreter | `pip install open-interpreter` |

## Notas de Seguridad
Recuerda siempre al usuario que, al ejecutar un asistente local con acceso a archivos y comandos, debe supervisar las acciones de Jarvis, especialmente cuando se trata de borrar o modificar archivos críticos del sistema.
