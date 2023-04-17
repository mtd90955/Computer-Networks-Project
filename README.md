# Computer-Networks-Project
The server will contain the Riffusion library. The client will connect to the server and can communicate with the server. The client app will connect to the server and retrieve a text box to request music. Music and audio will be done in UDP, and everything else (text prompt, voting system,..) is via TCP. The followings are the client's features: 

    The clients can send the server a text prompt to play music.
    
    The clients could guess the prompt from Riffusion music.
    
    The clients could team up by making invitations. 
    
    The clients can vote for the best prompt/music. 
    
    The client could observe the background’s change depending on the vote that goes into the server.
    
The server will be listening on port 2351 and will allow at most 50 connections at a time and 1 game instance at a time for the TCP communications. The client will disconnect when either the game concludes or the rate at which the audio gets to it is deemed too slow. 

## Instructions:
- pip install -r requirements.txt
    - Note: if on ubuntu
- python server.py
    - This will initialize the server and create an ngrok tunnel
        - Note: The ngrok tunnel's ip address and port will be printed
- upload music.ipynb to google colab:
    - set the runtime to gpu
    - run the first 2 cells (until and including pip commands)
    - reset runtime (versioning reasons)
    - run rest of the cells
- python client2.py [host-ip-addr] [host-ip-port] [sessionNum] [role]
    - Session number default is -1 (wanting to connect)
    - Role default is viewer