import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Constants
SERVER_ADDRESS = 'localhost'
SERVER_TCP_PORT = 2351
SERVER_UDP_PORT = 2352
MAX_CONNECTIONS = 50
AUDIO_BUFFER_SIZE = 1024

def __init__(self):
        # Initialize TCP socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((SERVER_ADDRESS, SERVER_TCP_PORT))

        # Initialize UDP socket for audio
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.connect((SERVER_ADDRESS, SERVER_UDP_PORT))

        # Start audio receiver thread
        self.audio_thread = threading.Thread(target=self.receive_audio)
        self.audio_thread.start()

        # Initialize GUI
        self.root = tk.Tk()
        self.root.title('Riffusion Client')
        self.create_widgets()

def create_widgets(self):
        # Create prompt entry box
        tk.Label(self.root, text='Enter prompt to play music:').pack()
        self.prompt_entry = tk.Entry(self.root)
        self.prompt_entry.pack()

        # Create buttons for sending prompt and guessing prompt
        tk.Button(self.root, text='Send Prompt', command=self.send_prompt).pack()
        tk.Button(self.root, text='Guess Prompt', command=self.guess_prompt).pack()

        # Create invitations box
        tk.Label(self.root, text='Invitations:').pack()
        self.invitations_listbox = tk.Listbox(self.root)
        self.invitations_listbox.pack()
        tk.Button(self.root, text='Invite', command=self.send_invitation).pack()

        # Create voting box
        tk.Label(self.root, text='Vote for best prompt/music:').pack()
        self.votes_listbox = tk.Listbox(self.root)
        self.votes_listbox.pack()
        tk.Button(self.root, text='Vote', command=self.send_vote).pack()

def send_prompt(self):
        # Send prompt to server over TCP
        prompt = self.prompt_entry.get()
        self.tcp_socket.send(prompt.encode())

def guess_prompt(self):
        # Send guess prompt request to server over TCP
        self.tcp_socket.send('guess'.encode())

def send_invitation(self):
        # Send invitation to server over TCP
        invitation = self.invitations_listbox.get(tk.ACTIVE)
        self.tcp_socket.send(f'invite {invitation}'.encode())

def send_vote(self):
        # Send vote to server over TCP
        vote = self.votes_listbox.get(tk.ACTIVE)
        self.tcp_socket.send(f'vote {vote}'.encode())

def receive_audio(self):
        # Receive audio data from server over UDP and play it using a media player
        while True:
            data = self.udp_socket.recv(AUDIO_BUFFER_SIZE)
            if not data:
                break

