import socket
import threading
import tkinter as tk
from tkinter import messagebox
from util import convert, deconvert # Message conveersion
import sys # command line args

# Constants
SERVER_ADDRESS = '3.13.191.225' if len(sys.argv) < 2 else sys.argv[1]
SERVER_TCP_PORT = 18567 if len(sys.argv) < 3 else int(sys.argv[2])
SERVER_UDP_PORT = 2352
MAX_CONNECTIONS = 50
AUDIO_BUFFER_SIZE = 1024
SESSION_NUM = 0 if len(sys.argv) < 4 else int(sys.argv[3])
ROLE = "viewer" if len(sys.argv) < 5 else sys.argv[4]

class Client2:
        def __init__(self):
                # Initialize TCP socket
                self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_socket.connect((SERVER_ADDRESS, SERVER_TCP_PORT))
        
                # Initialize UDP socket for audio
                self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,AUDIO_BUFFER_SIZE)
        
                # Start audio receiver thread
                #self.audio_thread = threading.Thread(target=self.receive_audio)
                #self.audio_thread.start()
        
                # Initialize GUI
                self.root = tk.Tk()
                self.root.title('Riffusion Client')
                self.create_widgets()
                self.initConnection(ROLE.lower() == "prompter", SESSION_NUM)
                self.root.mainloop()
        
        def create_widgets(self):
                # Create prompt entry box
                tk.Label(self.root, text='Enter prompt to play music:').pack()
                self.prompt_entry = tk.Entry(self.root)
                self.prompt_entry.pack()
        
                # Create buttons for sending prompt and guessing prompt
                self.send_prompt_button = tk.Button(self.root, text='Send Prompt', command=self.send_prompt)
                self.send_prompt_button.pack()
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
                msg: dict = {"task": "prompt", "promptStart": prompt, "promptEnd": prompt, "alpha": "0.0"}
                self.tcp_socket.send(convert(msg))
                self.send_prompt_button["state"] = "disabled"
        
        def guess_prompt(self):
                # Send guess prompt request to server over TCP                
                prompt = self.prompt_entry.get()
                msg = {"task": "guess", "prompt": prompt, "promptNum": 0}
                self.tcp_socket.send(convert(msg))
                mess = self.tcp_socket.recv(1024)
                truth = deconvert(mess)
                if type(truth) == str:
                       print("Error: truth")
                else:
                       self.guess = truth["truth"] == "True"

        def send_invitation(self):
                # Send invitation to server over TCP
                invitation = self.invitations_listbox.get(tk.ACTIVE)
                self.tcp_socket.send(f'invite {invitation}'.encode())
        
        def send_vote(self):
                # Send vote to server over TCP
                vote = self.votes_listbox.get(tk.ACTIVE)
                self.tcp_socket.send(f'vote {vote}'.encode())
        
        def initConnection(self, prompter: bool, sessionNum: int):
                msg: dict = {"client": "prompter" if prompter else "viewer", "sessionNum": str(sessionNum)}
                self.tcp_socket.sendall(convert(msg))
        
        def receive_audio(self):
                # Receive audio data from server over UDP and play it using a media player
                self.udp_socket.sendto("Hello".encode(), (SERVER_ADDRESS, SERVER_UDP_PORT))
                while True:
                    data, addr = self.udp_socket.recvfrom(AUDIO_BUFFER_SIZE)
                    if not data:
                        break


client2 = Client2()