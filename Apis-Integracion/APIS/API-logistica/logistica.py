from flask import Flask, request, jsonify
import sqlite3
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE = 'ecommerce.db'

def query_db(query, args=(), one=False):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    try:
        cur.execute(query, args)
        rv = cur.fetchall()
        con.close()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return None

statuses = []

@app.route('/estado_envio/', methods=['POST'])
def update_status():
    data = request.get_json()
    logger.info(f"Solicitud recibida para actualizar estado: {data}")

    if not data or not data.get('order_id') or not data.get('status'):
        logger.error("Faltan order_id o estado en la solicitud.")
        return jsonify({"error": "Order Id y estado son requeridos"}), 400

    if not isinstance(data['order_id'], int) or not isinstance(data['status'], str):
        logger.error("Tipos de datos inválidos para order_id o estado.")
        return jsonify({"error": "Order Id debe ser un entero y estado debe ser un string"}), 400

    # Verificar cliente en la base de datos
    customer_id = data.get('customer_id')
    client = query_db('SELECT * FROM Clientes WHERE id = ?', [customer_id], one=True)
    if not client:
        logger.error(f"Cliente no encontrado: {customer_id}")
        return jsonify({"error": "Cliente no encontrado"}), 404

    statuses.append(data)
    logger.info(f"Estado actualizado para order_id {data['order_id']}")
    return jsonify({"message": "Estado actualizado correctamente"}), 200

@app.route('/get_status/<int:order_id>', methods=['GET'])
def get_status(order_id):
    logger.info(f"Solicitud recibida para obtener estado de order_id {order_id}")

    for status in statuses:
        if status['order_id'] == order_id:
            logger.info(f"Estado encontrado para order_id {order_id}: {status}")
            return jsonify(status), 200

    logger.error(f"Orden no encontrada para order_id {order_id}")
    return jsonify({"error": "Orden no encontrada"}), 404

@app.route('/status', methods=['GET'])
def status():
    logger.info("Solicitud recibida para verificar el estado de la API")
    return jsonify({"status": "Api de logistica esta funcionando"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
