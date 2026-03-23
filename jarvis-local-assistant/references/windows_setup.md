# Guía de Instalación de Jarvis Local en Windows (Fase 6)

Esta guía detalla los pasos para configurar el "Cerebro" y las "Manos" de Jarvis en un entorno Windows, permitiendo una interacción sin límites de tokens y con capacidades de automatización.

## 1. El Cerebro: Modelos Locales (Sin Tokens)

Para que Jarvis hable sin límites, utilizaremos **Ollama**, que es la herramienta más rápida y estable en 2026 para Windows.

### Pasos:
1. Descarga e instala **Ollama** desde [ollama.com](https://ollama.com).
2. Abre una terminal (PowerShell o CMD) y ejecuta:
   ```powershell
   ollama run llama3
   ```
   *Esto descargará y ejecutará el modelo Llama 3 en tu PC.*
3. Mantén Ollama ejecutándose en segundo plano. Servirá una API en `http://localhost:11434`.

## 2. Las Manos: Open Interpreter (Autonomía)

Open Interpreter permite que Jarvis ejecute código, navegue por la web y gestione archivos en tu Windows.

### Pasos:
1. Instala **Python 3.11+** desde [python.org](https://www.python.org/). Asegúrate de marcar "Add Python to PATH".
2. Instala Open Interpreter usando pip:
   ```powershell
   pip install open-interpreter
   ```
3. Para conectar las "Manos" con el "Cerebro" local, ejecuta:
   ```powershell
   interpreter --local
   ```
   *Selecciona 'Ollama' como proveedor y 'llama3' como modelo.*

## 3. Navegación Web Autónoma

Para que Jarvis pueda navegar como yo, asegúrate de tener instalado Google Chrome o Microsoft Edge. Open Interpreter utilizará estos navegadores para realizar búsquedas y extraer información.

## 4. Interfaz de Chat Persistente

Para tener a Jarvis siempre a mano, puedes usar **AnythingLLM**, que ofrece una interfaz de escritorio muy pulida:
1. Descarga **AnythingLLM Desktop** para Windows.
2. En la configuración, selecciona "Ollama" como tu motor de IA.
3. ¡Listo! Ya tienes una ventana de chat persistente en tu escritorio.
