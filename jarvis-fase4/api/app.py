"""
JARVIS FASE 4 - REST API
Endpoints para chat, estadísticas y configuración
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sys

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import JarvisFase4
from chat.complexity_detector import ComplexityLevel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)
CORS(app)

# Inicializar Jarvis
jarvis = JarvisFase4()

# ==================== ENDPOINTS ====================

@app.route('/health', methods=['GET'])
def health():
    """Verificar salud del servicio"""
    status = jarvis.get_status()
    return jsonify({
        'status': 'ok',
        'local_available': status['local_chat_available'],
        'manus_available': status['manus_available'],
        'timestamp': str(os.popen('date').read().strip())
    }), 200


@app.route('/chat', methods=['POST'])
def chat():
    """Procesar mensaje de chat"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        context = data.get('context', '')
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Procesar consulta
        result = jarvis.process_query(message, context)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error en /chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/chat/batch', methods=['POST'])
def chat_batch():
    """Procesar múltiples mensajes"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        context = data.get('context', '')
        
        if not messages:
            return jsonify({'error': 'Sin mensajes'}), 400
        
        results = []
        for msg in messages:
            result = jarvis.process_query(msg, context)
            results.append(result)
        
        return jsonify({'results': results}), 200
    
    except Exception as e:
        logger.error(f"Error en /chat/batch: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/complexity', methods=['POST'])
def analyze_complexity():
    """Analizar complejidad de un mensaje"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        context = data.get('context', '')
        
        if not message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        level, score, details = jarvis.complexity_detector.detect(message, context)
        recommendation = jarvis.complexity_detector.get_recommendation(level)
        
        return jsonify({
            'level': level.name,
            'score': score,
            'details': details,
            'recommendation': recommendation
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /complexity: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    """Obtener estadísticas del sistema"""
    try:
        status = jarvis.get_status()
        return jsonify(status), 200
    
    except Exception as e:
        logger.error(f"Error en /stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/history', methods=['GET'])
def history():
    """Obtener historial de conversación"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = jarvis.local_chat.get_history(limit=limit)
        
        return jsonify({
            'count': len(history),
            'messages': history
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /history: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/history/clear', methods=['POST'])
def clear_history():
    """Limpiar historial"""
    try:
        jarvis.local_chat.clear_history()
        return jsonify({'message': 'Historial limpiado'}), 200
    
    except Exception as e:
        logger.error(f"Error en /history/clear: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Obtener estadísticas del caché"""
    try:
        stats = jarvis.manus_connector.get_cache_stats()
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error en /cache/stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Limpiar caché"""
    try:
        jarvis.manus_connector.clear_cache()
        return jsonify({'message': 'Caché limpiado'}), 200
    
    except Exception as e:
        logger.error(f"Error en /cache/clear: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/config', methods=['GET'])
def get_config():
    """Obtener configuración actual"""
    try:
        return jsonify(jarvis.config), 200
    
    except Exception as e:
        logger.error(f"Error en /config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/config', methods=['PUT'])
def update_config():
    """Actualizar configuración"""
    try:
        data = request.get_json()
        
        # Actualizar configuración
        jarvis.config.update(data)
        
        # Guardar a archivo
        import json
        os.makedirs('config', exist_ok=True)
        with open('config/fase4_config.json', 'w') as f:
            json.dump(jarvis.config, f, indent=2)
        
        return jsonify({
            'message': 'Configuración actualizada',
            'config': jarvis.config
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /config PUT: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/manus/test', methods=['GET'])
def test_manus():
    """Probar conexión a Manus"""
    try:
        result = jarvis.manus_connector.test_connection()
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error en /manus/test: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/local/test', methods=['GET'])
def test_local():
    """Probar chat local"""
    try:
        result = jarvis.local_chat.chat("Hola, ¿estás disponible?")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error en /local/test: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/status', methods=['GET'])
def status():
    """Obtener estado completo del sistema"""
    try:
        status = jarvis.get_status()
        return jsonify({
            'status': 'running',
            'system': status,
            'timestamp': str(os.popen('date').read().strip())
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /status: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Endpoint no encontrado"""
    return jsonify({'error': 'Endpoint no encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Error interno del servidor"""
    return jsonify({'error': 'Error interno del servidor'}), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    logger.info("🚀 Iniciando API REST de JARVIS FASE 4...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
