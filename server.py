from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import cv2
import base64
import sqlite3
import time
import serial
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
socketio = SocketIO(app)

# Ahora configuraremos la conexion serial
ser = serial.Serial('COM3', 9600)

# Después deberiamos configurar la conexion de la base de datos
conn = sqlite3.connect("my_sqlite.sqlite", check_same_thread=False)

c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS mouse_data
             (x INTEGER, y INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
c.execute('''CREATE TABLE IF NOT EXISTS images
             (image BLOB, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
c.commit()


# Esta funcción leerá los datos del pueto serial
def serial_reader():
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            x, y = map(int, line.split(','))
            socketio.emit('mouse_position', {'x': x, 'y': y})
            c.execute("INSERT INTO mouse_data (x, y) VALUES (?, ?)", (x, y))
            conn.commit()

threading.Thread(target=serial_reader).start()