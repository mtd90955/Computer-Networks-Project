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

        # Create invitations box
#         tk.Label(self.root, text='Invite a friend:').pack()
#         self.invite_entry = tk.Entry(self.root)
#         self.invite_entry.pack()
#         tk.Button(self.root, text='Invite', command=self.create_invitation).pack()
        invite_button = tk.Button(self.root, text='Invite', command=self.show_invite_dialog).pack()

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
    def show_invite_dialog(self):
        # Show a dialog box where the user can enter the IP address and port number of the client they want to invite
        invite_dialog = tk.Toplevel()
        invite_dialog.title('Invite a Friend')

        ip_label = tk.Label(invite_dialog, text='IP Address:')
        ip_label.grid(row=0, column=0)
        self.ip_entry = tk.Entry(invite_dialog)
        self.ip_entry.grid(row=0, column=1)

        port_label = tk.Label(invite_dialog, text='Port Number:')
        port_label.grid(row=1, column=0)
        self.port_entry = tk.Entry(invite_dialog)
        self.port_entry.grid(row=1, column=1)

        send_button = tk.Button(invite_dialog, text='Send Invitation', command=self.send_invitation_dialog)
        send_button.grid(row=2, column=0, columnspan=2)
        
    def send_invitation_dialog(self):
        # Get the IP address and port number from the invitation dialog and send an invitation to the client at that address
        ip_address = self.ip_entry.get()
        port_number = int(self.port_entry.get())
        peer_address = (ip_address, port_number)
        self.send_invitation(peer_address)
    
    def run(self):
        # Start GUI event loop
        
        self.root.mainloop()

if __name__ == '__main__':
    client = Client()
    client.run()
