import socket, threading, ast, typing

CHUNK = 1024

          
class Prompt:
   promptStart: str
   promptEnd: str
   promptMusic: str
   votes_up: int = 0
   votes_down: int = 0
   vote_lock: threading.Lock = threading.Lock()

   def __init__(self, promptStart: str, promptEnd: str, promptMusic: str):
        self.promptStart = promptStart
        self.promptEnd = promptEnd
        self.promptMusic = promptMusic
    
   def vote(self, voting: bool):
       with self.vote_lock:
           if voting:
               self.votes_up += 1
           else:
               self.votes_down += 1
   
   def getVotesUp(self):
       temp: int = 0
       with self.vote_lock:
           temp = self.votes_up
       return temp
   
   def getVotesDown(self):
       temp: int = 0
       with self.vote_lock:
           temp = self.votes_down
       return temp
   
   def getNetVotes(self):
       temp: int = 0
       with self.vote_lock:
           temp = self.votes_up - self.votes_down
       return temp

class Session:
    music_socket: typing.Union[socket.socket, None] = None
    music_socket_lock: threading.Lock = threading.Lock()
    prompters: int = 0
    prompters_lock: threading.Lock = threading.Lock()
    prompts: list[Prompt] = []
    prompts_lock: threading.Lock = threading.Lock()
    

    def promptMusic(self, promptStart: str, promptEnd: str,
                    alpha: float) -> typing.Union[str, None]:
       buffer: str = ""
       prompt: dict[str, str] = {
          "promptStart": promptStart,
          "promptEnd": promptEnd,
          "alpha": alpha,
        }
       with self.music_socket_lock:
          if self.music_socket is not None:
             self.music_socket.send(prompt)
             stop: bool = False
             while not stop:
                message = self.music_socket.recv(4 * CHUNK)
                try:
                    data = ast.literal_eval(message)
                    if data["data"] == "end":
                       stop = True
                       continue
                    buffer += data["data"]
                except ValueError:
                   print("ValueError in promptMusic")
                   return buffer
          else:
             return None
       return buffer

    def vote(self, voting: bool, promptNum: int) -> bool:
       with self.prompts_lock:
          if promptNum < len(self.prompts):
             self.prompts[promptNum].vote(voting=voting)
          else:
             return False
       return True
    
    def setSocket(self, conn: socket.socket):
        with self.music_socket_lock:
          if self.music_socket == None:
              self.music_socket = conn
          else:
             conn.close()
             return
        
    def addPrompter(self) -> bool:
       with self.prompters_lock:
          if self.prompters < 2:
             self.prompters += 1
          else:
             return False
       return True
    
    def addPrompt(self, prompt: Prompt) -> bool:
       with self.prompts_lock:
          if len(self.prompts) < 2:
             self.prompts.append(prompt)
          else:
             return False
       return True
    
    def getPrompts(self) -> list[Prompt]:
       temp: list[Prompt] = []
       with self.prompts_lock:
          for prompt in self.prompts:
             tempPrompt: Prompt = Prompt(
                promptStart=prompt.promptStart,
                promptEnd=prompt.promptEnd,
                promptMusic=prompt.promptMusic,
             )
             temp.append(tempPrompt)
       return temp