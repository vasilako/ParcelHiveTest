from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import cv2
import base64
import sqlite3
import time
import serial

