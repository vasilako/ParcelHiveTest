# ParcelHiveTest
This repository is to present the test solution for Parcel Hive.

This application that uses parallel processes / multiprocessing via python using a browser environment to visualize the current reading of serial data from the movement of the mouse and when the left mouse’s button is pressed take a picture of a connected webcam. As a final result, to save the current coordinates of the mouse cursor and data-source of the image in sqllite database.

# Explanation of the code
**Multithreading:** We use a thread to continuously read data from the serial port and output the mouse coordinates via websockets.

**Webserver:** We use Flask to create a webserver to serve the HTML page and handle requests.

**Websockets:** Flask-SocketIO is used to send and receive messages in real time between the server and the client.

**Pyserial:** We read mouse data from the serial port.

**OpenCV:** Capture an image of the webcam when the left mouse button is pressed.

**SQLite:** Save the mouse coordinates and captured images in a SQLite database.