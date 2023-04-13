import riffusion
import socket
import threading
import time

# Constants
SERVER_ADDRESS = 'localhost'
SERVER_TCP_PORT = 2351
SERVER_UDP_PORT = 2352
MAX_CONNECTIONS = 50
AUDIO_BUFFER_SIZE = 1024

# Global variables
clients = []
prompt1 = ''
prompt2 = ''
votes = {'good': 0, 'bad': 0, 'prompt1': 0, 'prompt2': 0}

# Riffusion library initialization
riffusion.init()

# TCP server thread
def tcp_server_thread():
    # Initialize TCP socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((SERVER_ADDRESS, SERVER_TCP_PORT))
    tcp_socket.listen(MAX_CONNECTIONS)
    print(f'TCP server listening on {SERVER_ADDRESS}:{SERVER_TCP_PORT}...')

    # Accept new connections
    while True:
        client_socket, client_address = tcp_socket.accept()
        print(f'New client connected: {client_address}')
        clients.append(client_socket)
        threading.Thread(target=handle_tcp_client, args=(client_socket,)).start()

# Handle TCP client requests
def handle_tcp_client(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        if data.startswith('prompt'):
            prompt = data.split()[1]
            if not prompt1:
                prompt1 = prompt
            else:
                prompt2 = prompt
            print(f'Received prompt: {prompt}')
        elif data == 'guess':
            if riffusion.is_playing():
                prompt = riffusion.get_prompt()
                for client in clients:
                    client.send(prompt.encode())
        elif data.startswith('invite'):
            invitation = data.split()[1]
            print(f'Received invitation: {invitation}')
        elif data.startswith('vote'):
            vote = data.split()[1]
            if vote == 'good':
                votes['good'] += 1
            elif vote == 'bad':
                votes['bad'] += 1
            elif vote == 'prompt1':
                votes['prompt1'] += 1
            elif vote == 'prompt2':
                votes['prompt2'] += 1
            print(f'Received vote: {vote}')

# UDP audio server thread
def udp_server_thread():
    # Initialize UDP socket
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((SERVER_ADDRESS, SERVER_UDP_PORT))
    print(f'UDP server listening on {SERVER_ADDRESS}:{SERVER_UDP_PORT}...')

    # Continuously send audio data to all connected clients
    while True:
        data = riffusion.get_audio_buffer(AUDIO_BUFFER_SIZE)
        for client in clients:
            try:
                client.sendall(data)
            except socket.error:
                clients.remove(client)

# Background graphics thread
def background_graphics_thread():
    while True:
        time.sleep(5)
        print(f'Votes: good={votes["good"]}, bad={votes["bad"]}, prompt1={votes["prompt1"]}, prompt2={votes["prompt2"]}')

# Start server threads
threading.Thread(target=tcp_server_thread).start()
threading.Thread(target=udp_server_thread).start()
threading.Thread(target=background_graphics_thread).start()
