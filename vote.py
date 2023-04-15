# client
def create_widgets(self):
        # Create voting box
        vote_frame = tk.Frame(self.root)
        vote_frame.pack()
        # Create good vote button and count label
        self.good_votes = 0
        tk.Button(vote_frame, text='Good', command=self.cast_good_vote).grid(row=0, column=0)
        tk.Label(vote_frame, text='Good Votes:').grid(row=0, column=1)
        self.good_count_label = tk.Label(vote_frame, text=str(self.good_votes))
        self.good_count_label.grid(row=0, column=2)
        # Create bad vote button and count label
        self.bad_votes = 0
        tk.Button(vote_frame, text='Bad', command=self.cast_bad_vote).grid(row=1, column=0)
        tk.Label(vote_frame, text='Bad Votes:').grid(row=1, column=1)
        self.bad_count_label = tk.Label(vote_frame, text=str(self.bad_votes))
        self.bad_count_label.grid(row=1, column=2)
def cast_good_vote(self):
        # Increment good vote count and update label
        self.good_votes += 1
        self.tcp_socket.send("good".encode())

def cast_bad_vote(self):
        # Increment bad vote count and update label
        self.bad_votes += 1
        self.tcp_socket.send("bad".encode())

# server
def handle_client(client_socket, client_address):
    # Loop to handle client requests
    while True:
        # Receive data from the client
        data = client_socket.recv(1024).decode()
        if not data:
            break
        elif data == "good":
            global votes_good
            votes_good += 1
        elif data == "bad":
            global votes_bad
            votes_bad += 1
        print(f"Received data from {client_address}: {data}")
        print(f"Votes - Good: {votes_good}, Bad: {votes_bad}")
        client_socket.sendall("Received".encode())
    
    # Close the client socket
    client_socket.close()
