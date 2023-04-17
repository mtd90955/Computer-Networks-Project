import socket
import threading
import tkinter as tk
from tkinter import messagebox
from util import convert, deconvert # Message conveersion
import sys # command line args
import random, math
import pyaudio

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

                self.net = 0
        
                # Initialize GUI
                self.root = tk.Tk()
                self.current_color = '#FFFFFF'
                self.target_color = self.generate_random_color()
                self.root.configure(bg=self.current_color)
                self.root.geometry("500x500+200+200") 
                self.root.title('Riffusion Client')
                self.create_widgets()
                self.initConnection(ROLE.lower() == "prompter", SESSION_NUM)
                t1: threading.Thread = threading.Thread(target=self.handle_things)
                t1.start()
                self.root.mainloop()
        
        def create_widgets(self):
                self.root.after(0, self.transition_color)

                # Create invitation system
                invitation_frame = tk.Frame(self.root)
                invitation_frame.pack()
                tk.Label(invitation_frame, text="Want to join:").grid(row=0, column=0)
                self.want_to_join_label = tk.Label(invitation_frame, text="")
                self.want_to_join_label.grid(row=0, column=1)
                self.invite_button = tk.Button(invitation_frame, text="Invite", command=self.invite_person, state="disabled")
                self.invite_button.grid(row=0, column=2)
                tk.Label(invitation_frame, text="Invite code:").grid(row=1, column=0)
                self.invite_code_entry = tk.Entry(invitation_frame)
                self.invite_code_entry.grid(row=1, column=1)
                self.invite_code_button = tk.Button(invitation_frame, text="Join", command=self.join_session)
                self.invite_code_button.grid(row=1, column=2)

                # Create prompt entry box
                tk.Label(self.root, text='Enter prompt to play music:').pack()
                self.prompt_entry = tk.Entry(self.root)
                self.prompt_entry.pack()
        
                # Create buttons for sending prompt and guessing prompt
                self.send_prompt_button = tk.Button(self.root, text='Send Prompt', command=self.send_prompt)
                self.send_prompt_button.pack()
                tk.Button(self.root, text='Guess Prompt', command=self.guess_prompt).pack()

                # Create option menu
                varList = tk.StringVar(self.root)
                varList.set("1")
                self.sel = 1
                self.om = tk.OptionMenu(self.root, varList, "1", "2", command=self.setSel)
                self.om.pack()
        
                # Create voting box
                vote_frame = tk.Frame(self.root)
                vote_frame.pack()
                # Create good vote button and count label
                self.good_votes = 0
                tk.Button(vote_frame, text='Good', command=self.cast_good_vote).grid(row=0, column=0)
                tk.Label(vote_frame, text='Good Votes:').grid(row=0, column=1)
                self.good_count_label = tk.Label(vote_frame, text="Vote now to see vote count")
                self.good_count_label.grid(row=0, column=2)
                # Create bad vote button and count label
                self.bad_votes = 0
                tk.Button(vote_frame, text='Bad', command=self.cast_bad_vote).grid(row=1, column=0)
                tk.Label(vote_frame, text='Bad Votes:').grid(row=1, column=1)
                self.bad_count_label = tk.Label(vote_frame, text="Vote now to see vote count")
                self.bad_count_label.grid(row=1, column=2)
        
        def send_prompt(self):
                # Send prompt to server over TCP
                prompt = self.prompt_entry.get()
                msg: dict = {"task": "prompt", "promptStart": prompt, "promptEnd": prompt, "alpha": "0.0"}
                self.tcp_socket.send(convert(msg))
                self.send_prompt_button["state"] = "disabled"
        
        def guess_prompt(self):
                # Send guess prompt request to server over TCP                
                prompt = self.prompt_entry.get()
                msg = {"task": "guess", "prompt": prompt, "promptNum": self.sel}
                self.tcp_socket.send(convert(msg))
        
        def send_vote(self, vote: bool):
                # Send vote to server over TCP
                num = self.sel
                self.tcp_socket.send(convert({"vote": vote, "task": "vote", "promptNum": num}))

        def cast_good_vote(self):
            # Send current vote counts over TCP to server
            self.send_vote(True)
            self.show_votes()
    
        def cast_bad_vote(self):
            # Send current vote counts over TCP to server
            self.send_vote(False)
            self.show_votes()
    
        def show_votes(self, resp: dict):
            # Split the vote data into good and bad vote counts
            good = resp["up"]
            bad = resp["down"]
            self.bad_count_label.config(text=str(bad))
            self.good_count_label.config(text=str(good))

        def setSel(self, sel):
                self.sel = int(sel)
        
        def initConnection(self, prompter: bool, sessionNum: int):
                msg: dict = {"client": "prompter" if prompter else "viewer", "sessionNum": str(sessionNum)}
                self.tcp_socket.sendall(convert(msg))
        
        def receive_audio(self):
                # Receive audio data from server over UDP and play it using a media player
                self.udp_socket.sendto("Hello".encode(), (SERVER_ADDRESS, SERVER_UDP_PORT))
                while True:
                    data, addr = self.udp_socket.recvfrom(AUDIO_BUFFER_SIZE)
                    p = pyaudio.PyAudio()
                    # Open the audio file (replace 'audio_bytes' with your bytes object)
                    stream = p.open(format=p.get_format_from_width(2),
					channels=1,
					rate=44100,
					output=True,
					frames_per_buffer=1024)
                    stream.write(data)
                    if not data:
                        break

        def generate_random_color(self):
            # Generate a random hexadecimal color code
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)

        def transition_color(self):
            ask: dict = {"task": "ask"} # task
            self.tcp_socket.sendall(convert(ask)) # send it
            # Update the target color if the current color has reached it
            if self.current_color == self.target_color:
                self.target_color = self.generate_random_color()

            # Calculate the distance between the current color and target color
            r1, g1, b1 = tuple(int(self.current_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            r2, g2, b2 = tuple(int(self.target_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            distance = math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)

            # Adjust the speed of the transition based on the distance
            speed = 0.1 * distance * self.net / 255

            # Update the current color to smoothly transition to the target color
            r = int(r1 + (r2 - r1) * speed)
            g = int(g1 + (g2 - g1) * speed)
            b = int(b1 + (b2 - b1) * speed)
            self.current_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
            self.root.configure(bg=self.current_color)

            # Schedule the next color transition after a delay of 100 ms
            self.root.after(3000, self.transition_color)

        def send_invitation(self, peer_address):
            # Send an invitation to another client at the given address
            message = {"INVITE": self.username, "task": "INVITE"}
            self.tcp_socket.sendto(convert(message), peer_address)

        def invite_person(self):
            # Prompt user to select a person to invite
            person = messagebox.askquestion("Invite", "Who do you want to invite?")
            if person == "yes":
                # Send invitation over TCP to server
                self.tcp_socket.send(convert({"invite": person, "task": "invite"}))

        def join_session(self):
            # Send join request over TCP to server
            invite_code = self.invite_code_entry.get()
            self.tcp_socket.send(convert({"join": invite_code, "task": "join"}))

        def handle_invite(self, person: str, sessNum: str):
            # Prompt user to confirm invitation
            confirmed = messagebox.askyesno("Invitation", f"{person} has invited you to join their session. Do you want to join?")
            if confirmed:
                # Send confirmation message over TCP to server
                self.tcp_socket.send({"invite_confirmed": person, "task": "invite_confirmed", "sessNum": sessNum})
                # Disable invite button until next invitation is received
                self.invite_button.config(state="disabled")

        def handle_join(self, invite_code):
            # Disable join button and clear invite code entry
            self.invite_code_button.config(state="disabled")
            self.invite_code_entry.delete(0, tk.END)

        def handle_leave(self, person):
            # Remove person from want to join list and update label
            self.want_to_join.discard(person)
            self.want_to_join_label.config(text=", ".join(self.want_to_join))
            if not self.want_to_join:
                self.invite_button.config(state="disabled")

        def handle_things(self):
              while True:
                    message = self.tcp_socket.recv(1024)
                    data = deconvert(message) # get dict
                    if type(data) == str: # if failed
                          break
                    if data["task"] == "error": # if error
                          print(data["error"])
                    if data["task"] == "want_to_join":
                          self.handle_invite(data["want_to_join"], data["sessNum"])
                    if data["task"] == "show": # if showing votes
                          self.show_votes(data)
                    if data["task"] == "guess": # if showing guess
                          self.guess = data["truth"] == "True"
                    if data["task"] == "answer": # if have answer
                          self.net = data["net"]

client2 = Client2()