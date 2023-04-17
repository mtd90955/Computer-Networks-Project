# -*- coding: utf-8 -*-
"""
Created on Sun Mar 12 14:49:26 2023

@author: kpk16
"""

import socket # for sockets
import threading
from typing import Union # for multithreading
from session import Session, Prompt # Game Session info
from util import convert, deconvert, get_ngrok_public_ip_address # Message conversion
from pyngrok import ngrok # to avoid hosting server
ngrok.set_auth_token("2DaRNugWZw7jrHWLOUvKwrm88BY_816JczcVsUEVtfz4LXbWC")
ngrok.kill() # Ensures no starting connection
# Maximum number of connections allowed
MAX_CONNECTIONS = 50

# Maximum number of game instances allowed
MAX_GAME_INSTANCES = 1

# List of active game instances
active_game_instances: list[Session] = [Session() for _ in range(MAX_GAME_INSTANCES)] # list compression
agi_lock: threading.Lock = threading.Lock() # active instances lock

# List of client sockets
cSocks: list[socket.socket] = []
cs_lock: threading.Lock = threading.Lock()

# List of wanted clients
wClients: list[str] = []
wc_lock: threading.Lock = threading.Lock()

udp_socket: socket.socket
udp_lock: threading.Lock = threading.Lock()

def helper(conn: socket.socket, addr, sess: Session, client: dict) -> bool:
   if client["task"] == "vote" and sess != None: # if they want to vote, let them
      vote: bool = bool(client["vote"])
      num = int(client["promptNum"])
      if sess.vote(voting=vote, promptNum=num):
         prompt = sess.getPrompts()[num]
         d: dict[str, str] = {"up": prompt.getVotesUp(), "down": prompt.getVotesDown(), "task": "show"}
         conn.sendall(convert(d))
   if client["task"] == "guess" and sess != None: # if they want to guess, let them
      prompts: list[Prompt] = sess.getPrompts() # get prompts
      promptNum: int = int(client["promptNum"])
      if promptNum < len(prompts): # if promptNum is within bounds
         truth: bool = prompts[promptNum].getPrompt().lower() == client["prompt"].lower() # compare
         d: dict = {"truth": str(truth), "task": "guess"} # make the truth known
         conn.sendall(convert(d)) # send it to them
   if client["task"] == "end": # if they want it to end, let them
      conn.close() # close conection
      return False # stop while loop
   if client["task"] == "ask" and sess != None: # ask
      answer: dict = {"net": 0, "task": "answer"}
      prompts = sess.getPrompts()
      for prompt in prompts:
         answer["net"] += prompt.getNetVotes()
      conn.sendall(convert(answer))
   if client["task"] == "invite": # client wants to invite
      person = client["invite"]
      sessNum = 0
      with agi_lock:
         sessNum = active_game_instances.index(sess)
      with wc_lock:
         wClients.add(person)
      with cs_lock:
         for client in cSocks:
             client.sendall({"want_to_join": person, "task": "want_to_join", "sessNum": sessNum})
   if client["task"] == "join": # client wants to join
       invite_code = client["join"]
       with agi_lock:
         b: bool = False
         for session in active_game_instances:
            if invite_code == session.getInviteCode():
                viewer(conn, addr, session)
                b= True
         if not b:
             conn.send({"task": "error", "error": "Invalid invite code"})
   if client["task"] == "invite_confirmed": # client wants to join an invite sess
      sessNum: int = int(client["sessNum"])
      Sess = None
      with agi_lock:
         if sessNum < len(active_game_instances):
            Sess = active_game_instances[sessNum]
         else:
            return False
         viewer(conn, addr, Sess)
   return True

def prompter(conn: socket.socket, addr, sess: Session):
   """
   Handles the prompter connection.

   Parameters:
      conn (socket.socket): the socket to communicate with.
      addr (Any): Not used atm.
      sess (Session): The session the prompter is in.
   """
   stop: bool = False # do not stop
   while not stop: # while not stopping
      message = conn.recv(1024) # receive message
      client = deconvert(message) # deconvert message to dict
      if type(client) == str: # if something went wrong
        print("ValueError")
      if client["task"] == "prompt" and sess != None: # if they want to prompt, let them
          newChunk: Union[bytes, None] = sess.promptMusic(client["promptStart"], client["promptEnd"])
          if newChunk == None: # if the Music is nonexistant
            print("Riffusion is not setup yet")
          else: # else, add the prompt
            prompt: Prompt = Prompt(
               promptStart=client["promptStart"],
               promptEnd=client["promptEnd"],
               promptMusic=newChunk,
            ) # new prompt
            sess.addPrompt(prompt=prompt)
      stop = not helper(conn, addr, sess, client)


def viewer(conn: socket.socket, addr, sess: Session):
   """
   Handles the viewer connection.

   Parameters:
      conn (socket.socket): the socket to communicate with.
      addr (Any): Not used atm.
      sess (Session): The session the viewer is in.
   """
   stop: bool = False # do not stop
   while not stop: # while not stopping
      message = conn.recv(1024) # receive message
      client = deconvert(message) # deconvert message to dict
      if type(client) == str: # if something went wrong
        print("ValueError")
      stop = not helper(conn, addr, sess, client)

# Function to handle client connections
def handle_client_connection(conn: socket.socket, addr):
    """
    Handles the client connection.
    Differentiates between the music client,
    prompter and viewer.

    Parameters:
      conn (socket.socket): the client socket connection
      addr (Any): the address of the client.
    """
    print(f"New client connected: {addr}")
    # TODO: Implement game logic and audio transmission
    try: # kill thread, print Error for any socket or conversion error not explicitly addressed
      message = conn.recv(1024) # receive message
      client = deconvert(message) # try to deconvert it
      if type(client) == str: # if failed, report it and close connection
        print("ValueError")
        conn.send(bytes("Error: -1", "utf-8"))
        conn.close()
        return
      sessionNum: int = int(client["sessionNum"]) # get the session number
      if client["client"] == "music": # if role is to provide music, set it in session
          with agi_lock:
             if sessionNum < len(active_game_instances):
                active_game_instances[sessionNum].setSocket(conn=conn)
                return
             else:
                print("IDK") # IDK how it would get here
                return
      if client["client"] == "prompter": # if role is prompter, give it to prompter
         Sess: Session = None
         with agi_lock: # for thread safety
          if sessionNum < len(active_game_instances) and sessionNum >= 0:
           Sess = active_game_instances[sessionNum]
          elif sessionNum == -1:
           Sess = None
          else:
           Sess = active_game_instances[0] # fallback
         prompter(conn=conn, addr=addr, sess=Sess) #prompter method
      if client["client"] == "viewer": # if role is viewer, give it to viewer
         Sess: Session = None
         with agi_lock: # for thread safety
          if sessionNum < len(active_game_instances) and sessionNum >= 0:
           Sess = active_game_instances[sessionNum]
          elif sessionNum == -1:
           Sess = None
          else:
           Sess = active_game_instances[0] # fallback
         viewer(conn=conn, addr=addr, sess=Sess) #viewer code (send to other function)
    except Exception as err: # for any exception, print the error
       print(err)
    conn.close() # close connection when done
    print(f"Client disconnected: {addr}")

# Function to start the server
def start_server():
    """
    Entry point for the server.
    """
    # Create a TCP socket and bind it to a specific port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', 2351))
    server_socket.listen()
    print("Server listening on port 2351")

    # Setup UDP socket and bind it to port
    global udp_socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
    udp_socket.bind(('', (2352)))
    print("Server listening on port 2352")

    # set up ngrok tcp tunnel
    tunnel = ngrok.connect(2351, "tcp")

    # print the address and port number
    print(get_ngrok_public_ip_address(tunnel))
    
    # Keep accepting new connections until the maximum number of connections is reached
    while len(active_game_instances) <= MAX_GAME_INSTANCES:
        try:
            conn, addr = server_socket.accept()
            # Check if the maximum number of connections has been reached
            if len(active_game_instances) > MAX_GAME_INSTANCES:
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
    with agi_lock: # for thread safety
       for session in active_game_instances: # for all game instances
          session.disactivateMusic() # disconnect from music servers
    server_socket.close() # close connections
    udp_socket.close()
    ngrok.disconnect(tunnel.public_url) # disconnect tunnel
    ngrok.kill() # kill ngrok
# Start the server
start_server()