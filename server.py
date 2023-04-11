# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 14:49:26 2023

@author: kpk16
"""

import socket # for sockets
import threading # for multithreading
import ast # for dict conversion
from session import Session, Prompt # Game Session info
# Maximum number of connections allowed
MAX_CONNECTIONS = 50

# Maximum number of game instances allowed
MAX_GAME_INSTANCES = 1

# List of active game instances
active_game_instances: list[Session] = []
agi_lock: threading.Lock = threading.Lock()

def prompter(conn: socket.socket, addr: socket._RetAddress, sess: Session):
   stop: bool = False
   while not stop:
      message = conn.recv(1024)
      try: # try to convert message into dictionary
        client = ast.literal_eval(message)
        if client["task"] == "prompt":
            music: str = ""
            for i in range(0, 5):
                music += sess.promptMusic(client["promptStart"], client["promptEnd"], i / 4)
            prompt: Prompt = Prompt(
               promptStart=client["promptStart"],
               promptEnd=client["promptEnd"],
               promptMusic=music,
            )
            sess.addPrompt(prompt=prompt)
        if client["task"] == "vote":
           vote: bool = bool(client["vote"])
           sess.vote(voting=vote, promptNum=client["promptNum"]) #prompter code (send to other function)
        if client["task"] == "end":
           stop = True
           conn.close()
           continue
      except ValueError:
        print("ValueError")

# Function to handle client connections
def handle_client_connection(conn: socket.socket, addr: socket._RetAddress):
    print(f"New client connected: {addr}")
    # TODO: Implement game logic and audio transmission
    message = conn.recv(1024)
    try: # try to convert message into dictionary
      client = ast.literal_eval(message)
      sessionNum: int = int(client["sessionNum"])
      if client["client"] == "music":
          with agi_lock:
             if sessionNum < len(active_game_instances):
                active_game_instances[sessionNum].setSocket(conn=conn)
             else:
                print("IDK")
                return
      if client["client"] == "prompter":
         prompter(conn=conn, addr=addr) #prompter method
      if client["client"] == "viewer":
         None #viewer code (send to other function)
    except ValueError:
      print("ValueError")
      conn.send("Error: -1")
      conn.close()
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