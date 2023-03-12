# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 14:49:26 2023

@author: kpk16
"""

import socket
import threading

# Maximum number of connections allowed
MAX_CONNECTIONS = 50

# Maximum number of game instances allowed
MAX_GAME_INSTANCES = 1

# List of active game instances
active_game_instances = []

# Function to handle client connections
def handle_client_connection(conn, addr):
    print(f"New client connected: {addr}")
    # TODO: Implement game logic and audio transmission
    conn.close()
    print(f"Client disconnected: {addr}")

# Function to start the server
def start_server():
    # Create a TCP socket and bind it to a specific port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 2351))
    server_socket.listen()

    print("Server listening on port 2351")

    # Keep accepting new connections until the maximum number of connections is reached
    while len(active_game_instances) < MAX_GAME_INSTANCES:
        try:
            conn, addr = server_socket.accept()
            # Check if the maximum number of connections has been reached
            if len(active_game_instances) >= MAX_GAME_INSTANCES:
                conn.send(b"Server is busy. Please try again later.")
                conn.close()
                print(f"Rejected client connection: {addr}")
                continue
            # Start a new thread to handle the client connection
            client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
            client_thread.start()
        except KeyboardInterrupt:
            # Stop the server if the user presses Ctrl-C
            break

    # Close the server socket when the maximum number of game instances has been reached
    server_socket.close()

# Start the server
start_server()