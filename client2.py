import socket
import threading
import tkinter as tk
from tkinter import messagebox
import random
import math 

# Constants
SERVER_ADDRESS = 'localhost'
SERVER_TCP_PORT = 2351
SERVER_UDP_PORT = 2352
MAX_CONNECTIONS = 50
AUDIO_BUFFER_SIZE = 1024

class Client:
    def __init__(self):
        # Initialize TCP socket
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((SERVER_ADDRESS, SERVER_TCP_PORT))
        # Initialize GUI
        self.root = tk.Tk()
        self.current_color = '#FFFFFF'
        self.target_color = self.generate_random_color()
        self.root.configure(bg=self.current_color)
        self.root.geometry("500x500+200+200")        
        self.root.title('Riffusion Client')
        self.create_widgets()

    def generate_random_color(self):
        # Generate a random hexadecimal color code
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    def transition_color(self):
        # Update the target color if the current color has reached it
        if self.current_color == self.target_color:
            self.target_color = self.generate_random_color()

        # Calculate the distance between the current color and target color
        r1, g1, b1 = tuple(int(self.current_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        r2, g2, b2 = tuple(int(self.target_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        distance = math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)

        # Adjust the speed of the transition based on the distance
        speed = 0.1 * distance / 255

        # Update the current color to smoothly transition to the target color
        r = int(r1 + (r2 - r1) * speed)
        g = int(g1 + (g2 - g1) * speed)
        b = int(b1 + (b2 - b1) * speed)
        self.current_color = '#{:02x}{:02x}{:02x}'.format(r, g, b)
        self.root.configure(bg=self.current_color)

        # Schedule the next color transition after a delay of 100 ms
        self.root.after(200, self.transition_color)

    def create_widgets(self):
        # Background change
        self.root.after(0, self.transition_color)

#         invite_button = tk.Button(self.root, text='Invite', command=self.show_invite_dialog).pack(side="left")

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

    def cast_good_vote(self):
        # Send current vote counts over TCP to server
        self.tcp_socket.send("good".encode())
        self.show_votes()

    def cast_bad_vote(self):
        # Send current vote counts over TCP to server
        self.tcp_socket.send("bad".encode())
        self.show_votes()

    def show_votes(self):
        data = self.tcp_socket.recv(1024).decode()
        # Split the vote data into good and bad vote counts
        _, good, bad = data.split(',')                                  
        self.bad_count_label.config(text=str(bad))
        self.good_count_label.config(text=str(good))
        
    def send_invitation(self, peer_address):
        # Send an invitation to another client at the given address
        message = f"INVITE {self.username}"
        self.tcp_socket.sendto(message.encode(), peer_address)
    def invite_person(self):
        # Prompt user to select a person to invite
        person = messagebox.askquestion("Invite", "Who do you want to invite?")
        if person == "yes":
            # Send invitation over TCP to server
            self.tcp_socket.send(f"invite:{person}".encode())

    def join_session(self):
        # Send join request over TCP to server
        invite_code = self.invite_code_entry.get()
        self.tcp_socket.send(f"join:{invite_code}".encode())

    def handle_invite(self, person):
        # Add person to want to join list and update label
        self.want_to_join.add(person)
        self.want_to_join_label.config(text=", ".join(self.want_to_join))
        self.invite_button.config(state="normal")

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
    
    def run(self):
        # Start GUI event loop
        
        self.root.mainloop()

if __name__ == '__main__':
    client = Client()
    client.run()
