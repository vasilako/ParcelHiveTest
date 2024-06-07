from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, LargeBinary, TIMESTAMP, func, create_engine
from flask_socketio import SocketIO, emit
import os
import serial
import cv2
import threading
import time
import base64



app = Flask(__name__, template_folder='templates')

# Configurar la conexión de la base de datos


# Lee el valor de la variable de entorno DATABASE_URI
database_url = os.getenv("DATABASE_URL")
# Verifica si la variable de entorno está configurada
print(database_url)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://db_pictures_sockets_app_user:p8nWGyd0yVYosMDqWSudtNLGZTiDNrT7@dpg-cpeugqf109ks73fl2s3g-a.oregon-postgres.render.com/db_pictures_sockets_app"
# app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Optional, but recommended to suppress warnings
print(app.config['SQLALCHEMY_DATABASE_URI'])

db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins="*")


# Configurar la conexión serial
serial_port = '/dev/tty.Bluetooth-Incoming-Port'
baud_rate = 9600
try:
    ser = serial.Serial(serial_port, baud_rate)
    print(f"Serial port {serial_port} opened successfully.")
except serial.SerialException as e:
    print(f"Error opening serial port {serial_port}: {e}")
    ser = None



# Configurar los modelos
class MouseData(db.Model):
    __tablename__ = 'mouse_data'
    id = Column(Integer, primary_key=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False)


class Images(db.Model):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), nullable=False)

# Create the tables
with app.app_context():
    db.create_all()



# Función para leer datos del puerto serial
def serial_reader():
    while True:
        if ser and ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            x, y = map(int, line.split(','))
            socketio.emit('mouse_position', {'x': x, 'y': y})


threading.Thread(target=serial_reader).start()

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)


@socketio.on('take_picture')
def take_picture(data):
    cap = cv2.VideoCapture(0)
    time.sleep(1)
    ret, frame = cap.read()
    cap.release()

    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Insert image data into the database
        session = db.session()
        new_image = Images(image=buffer.tobytes())
        session.add(new_image)
        session.commit()
        session.close()

        print(image_base64)
        emit('picture', {'image': image_base64})


@socketio.on('click')
def handle_mouse_click(data):
    x = data['x']
    y = data['y']
    print("Coordenadas del clic del ratón:", x, y)
    socketio.emit('mouse_position', {'x': x, 'y': y})

    # Insert mouse data into the database
    session = db.session()
    new_mouse_data = MouseData(x=x, y=y)
    session.add(new_mouse_data)
    session.commit()
    session.close()


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000,  debug=False, allow_unsafe_werkzeug=True)
