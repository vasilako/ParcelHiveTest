from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import cv2
import base64
import sqlite3
import time
import serial
import os

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Configurar la conexión serial
serial_port = '/dev/tty.Bluetooth-Incoming-Port'
baud_rate = 9600
try:
    ser = serial.Serial(serial_port, baud_rate)
    print(f"Serial port {serial_port} opened successfully.")
except serial.SerialException as e:
    print(f"Error opening serial port {serial_port}: {e}")
    ser = None

# Configurar la conexión de la base de datos
conn = sqlite3.connect("my_sqlite.sqlite", check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS mouse_data
             (x INTEGER, y INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
c.execute('''CREATE TABLE IF NOT EXISTS images
             (image BLOB, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Función para leer datos del puerto serial
def serial_reader():
    while True:
        if ser and ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            x, y = map(int, line.split(','))
            socketio.emit('mouse_position', {'x': x, 'y': y})
            # c.execute("INSERT INTO mouse_data (x, y) VALUES (?, ?)", (x, y))
            # conn.commit()

threading.Thread(target=serial_reader).start()

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on('take_picture')
def take_picture(data):  # Cambié el nombre de la función a 'take_picture' para que coincida con el evento
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        c.execute("INSERT INTO images (image) VALUES (?)", (buffer.tobytes(),))
        conn.commit()
        emit('picture', {'image': image_base64})

@socketio.on('click')
def handle_mouse_click(data):
    x = data['x']
    y = data['y']
    print("Coordenadas del clic del ratón:", x, y)
    socketio.emit('mouse_position', {'x': x, 'y': y})
    c.execute("INSERT INTO mouse_data (x, y) VALUES (?, ?)", (x, y))
    conn.commit()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
