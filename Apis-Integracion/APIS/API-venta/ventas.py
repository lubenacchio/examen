from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurar la conexión a la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ecommerce_user:admin123@localhost/ecommerce'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definir los modelos
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    razonSocial = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(255), nullable=False)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

    cliente = db.relationship('Cliente', backref=db.backref('ventas', lazy=True))

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/generar_boleta/', methods=['POST'])
def generate_receipt():
    data = request.get_json()
    if not data or not data.get('items'):
        logger.error("La compra debe poseer al menos 1 articulo")
        return jsonify({"error": "La compra debe poseer al menos 1 articulo"}), 400

    customer_id = data.get('customer_id')
    if not customer_id:
        logger.error("El customer_id es obligatorio")
        return jsonify({"error": "El customer_id es obligatorio"}), 400

    try:
        total = sum(item['precio'] * item['cantidad'] for item in data['items'])
    except KeyError:
        logger.error("Cada artículo debe tener 'precio' y 'cantidad'")
        return jsonify({"error": "Cada artículo debe tener 'precio' y 'cantidad'"}), 400
    except TypeError:
        logger.error("El 'precio' y 'cantidad' deben ser números")
        return jsonify({"error": "El 'precio' y 'cantidad' deben ser números"}), 400

    receipt = {
        "customer_id": customer_id,
        "items": data['items'],
        "total": total
    }

    # Comunicación con API de Clientes
    try:
        client_response = requests.get(f"http://localhost:8002/api/cliente/{customer_id}")
        client_response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error al comunicarse con el API de clientes: {str(e)}")
        return jsonify({"error": f"Error al comunicarse con el API de clientes: {str(e)}"}), 500

    order_id = data.get('order_id')
    if not order_id:
        logger.error("El order_id es obligatorio")
        return jsonify({"error": "El order_id es obligatorio"}), 400

    # Comunicación con API de Despacho
    try:
        shipment_response = requests.post("http://localhost:8001/estado_envio/", json={"order_id": order_id, "status": "En proceso", "customer_id": customer_id})
        shipment_response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error al comunicarse con el API de logística: {str(e)}")
        return jsonify({"error": f"Error al comunicarse con el API de logística: {str(e)}"}), 500

    return jsonify(receipt), 200

@app.route('/estado', methods=['GET'])
def status():
    logger.info("Solicitud recibida para verificar el estado de la API")
    return jsonify({"estado": "API de ventas está funcionando"}), 200

@app.route('/crear_cliente', methods=['POST'])
def create_client():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos inválidos"}), 400

    try:
        nuevo_cliente = Cliente(
            razonSocial=data['razonSocial'],
            rut=data['rut'],
            direccion=data['direccion']
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        return jsonify({"message": "Cliente creado con éxito", "cliente": {
            "id": nuevo_cliente.id,
            "razonSocial": nuevo_cliente.razonSocial,
            "rut": nuevo_cliente.rut,
            "direccion": nuevo_cliente.direccion
        }}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
