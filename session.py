import socket, threading, typing
from util import convert, deconvert

CHUNK = 1024 # sending and receiving size

          
class Prompt:
   """
   Data class for the prompt, music, and votes.
   """
   promptStart: str
   promptEnd: str
   prompt_lock: threading.Lock = threading.Lock()
   promptMusic: str
   prompt_music_lock: threading.Lock = threading.Lock()
   votes_up: int = 0
   votes_down: int = 0
   vote_lock: threading.Lock = threading.Lock()

   def __init__(self, promptStart: str, promptEnd: str, promptMusic: str):
        """
        Initializes `Prompt` object.

        Parameters:
         promptStart (str): the starting prompt.
         promptEnd (str): the ending propt.
         promptMusic (str): The string version of the bytes array of music
        """
        self.promptStart = promptStart
        self.promptEnd = promptEnd
        self.promptMusic = promptMusic
    
   def vote(self, voting: bool):
       """
       Adds a vote to the prompt.
       
       Parameters:
         voting (bool): whether they liked it or not.
       """
       with self.vote_lock: # for thread safety
           if voting: # if liked
               self.votes_up += 1
           else: # else disliked
               self.votes_down += 1
   
   def getVotesUp(self) -> int:
       """
       Gets the number of votes in favor of the prompt.

       Returns:
         str: The number of votes in favor of the prompt.
       """
       temp: int = 0
       with self.vote_lock: # for thread safety
           temp = self.votes_up
       return temp
   
   def getVotesDown(self) -> int:
       """
       Gets the number of votes not in favor of the prompt.

       Returns:
         str: The number of votes not in favor of the prompt.
       """
       temp: int = 0
       with self.vote_lock: # for thread safety
           temp = self.votes_down
       return temp
   
   def getNetVotes(self) -> int:
       """
       Gets the net votes (liked - disliked) of the prompt.

       Returns:
         str: The net votes (liked - disliked) of the prompt.
       """
       temp: int = 0
       with self.vote_lock: # for thread safety
           temp = self.votes_up - self.votes_down
       return temp
   
   def getPrompt(self) -> str:
      """
       Gets the starting prompt of the prompt.

       Returns:
         str: The starting prompt of the prompt.
       """
      temp: str = ""
      with self.prompt_lock: # for thread safety
         temp = self.promptStart
      return temp

   def getPromptMusic(self) -> str:
      """
      Gets the music string of the prompt.

      Returns:
         str: The music string of the prompt.
      """
      temp: str = ""
      with self.prompt_music_lock: # for thread safety
         temp = self.promptMusic
      return temp

class Session:
    """
    The session for each particular game.
    Holds the music socket and prompts.
    Thread safe operations.
    """
    music_socket: typing.Union[socket.socket, None] = None
    music_socket_lock: threading.Lock = threading.Lock()
    prompters: int = 0
    prompters_lock: threading.Lock = threading.Lock()
    prompts: list[Prompt] = []
    prompts_lock: threading.Lock = threading.Lock()
    

    def promptMusic(self, promptStart: str, promptEnd: str) -> typing.Union[str, None]:
       """
       Tries to get music from the riffusion client (music_socket).

       Parameters:
         promptStart (str): the starting prompt.
         promptEnd (str): the ending prompt.

       Returns:
         str | None: a string of music data (encoded from bytes) or None if unsuccessful.
       """
       buffer: str = "" # string buffer
       prompt: dict[str, str] = {
          "promptStart": promptStart,
          "promptEnd": promptEnd,
        } # prompt dictionary
       with self.music_socket_lock: # for thread safety
          if self.music_socket is not None: # if music socket is set
             self.music_socket.send(convert(prompt)) # send prompt
             stop: bool = False
             while not stop: # while end has not been reached
                message = self.music_socket.recv(4 * CHUNK) # receive data
                data = deconvert(message) # convert data to dict
                if type(data) == str: # if something went wrong
                   print("ValueError in promptMusic")
                   return buffer # return incomplete buffer
                if data["data"] == "end": # if it is the end
                   stop = True # discontinue the loop
                   continue
                buffer += data["data"] # concatinate received data
          else: # if not set
             return None # return None
       return buffer # return complete buffer

    def vote(self, voting: bool, promptNum: int) -> bool:
       """
       Adds a vote to the selected prompt.
       
       Parameters:
         voting (bool): whether they liked it or not.
         promptNum (int): which prompt to vote.

       Returns:
         bool: whether the promptNum is in bounds of the prompts array.
       """
       with self.prompts_lock: # for thread safety
          if promptNum < len(self.prompts): # if in bounds
             self.prompts[promptNum].vote(voting=voting) # vote
          else: # else, return false
             return False
       return True
    
    def setSocket(self, conn: socket.socket):
        """
        Sets the music socket with a connection if not already set.

        Parameters:
         conn (socket.socket): a socket for the riffusion client.
        """
        with self.music_socket_lock: # for thread safety
          if self.music_socket == None: # if music socket not already set
              self.music_socket = conn # set it
          else: # else, close given conection
             conn.close()
             return
        
    def addPrompter(self) -> bool:
       """
       Adds a prompter to the session.

       Returns:
         bool: whether the prompter was added (limit 2).
       """
       with self.prompters_lock: # for thread safety
          if self.prompters < 2: # if not over 1
             self.prompters += 1 # add
          else: # else, return false
             return False
       return True
    
    def addPrompt(self, prompt: Prompt) -> bool:
       """
       Adds a prompt (limit 2).

       Parameters:
         prompt (Prompt): The prompt to add.
       
       Returns:
         bool: Whether it was added or not.
       """
       with self.prompts_lock: # for thread safety
          if len(self.prompts) < 2: # if not above 1
             self.prompts.append(prompt) # add
          else: # else, return false
             return False
       return True
    
    def getPrompts(self) -> list[Prompt]:
       """
       Gets a list of deep cloned prompts.
       For thread safety.

       Returns:
         list[Prompt]: a deep cloned list of prompts.
       """
       temp: list[Prompt] = [] # new list
       with self.prompts_lock: # for thread safety
          for prompt in self.prompts: # for every prompt in prompts
             tempPrompt: Prompt = Prompt(
                promptStart=prompt.promptStart,
                promptEnd=prompt.promptEnd,
                promptMusic=prompt.promptMusic,
             ) # make a deep cloned Prompt object
             temp.append(tempPrompt) # append it
       return temp
    
    def disactivateMusic(self) -> None:
       """
       Disactivates the riffusion client.
       Sends a message telling it to stop.
       """
       close: dict[str, str] = {"promptStart": "endstart", "promptEnd": "endend",}
       with self.music_socket_lock: # for thread safety
          if self.music_socket is not None: # if set
             self.music_socket.send(convert(close)) # send closing prompt
             self.music_socket.close() # close connection
             self.music_socket = None # reset it to None