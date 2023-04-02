import socket
import threading

SERVER_ADDRESS = 'localhost'
SERVER_PORT = 2351

def send_message(sock):
    # send answer to server
    while True:
        message = input('Enter your answer: ')
        sock.sendall(message.encode())

def receive_messages(sock):
    # receive data from server
    while True:
        data = sock.recv(1024)
        if not data:
            break
        print(data.decode())

# create socket object
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connect to server
    client_socket.connect((SERVER_ADDRESS, SERVER_PORT))

    # create thread to send messages to server
    send_thread = threading.Thread(target=send_message, args=(client_socket,))
    send_thread.start()

    # create thread to receive messages from server
    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    recv_thread.start()

    # wait for threads to finish
    send_thread.join()
    recv_thread.join()
    
# start client    
start_client()
