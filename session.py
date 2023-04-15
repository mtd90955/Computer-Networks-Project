import socket, threading, ast, typing
from util import convert, deconvert

CHUNK = 1024

          
class Prompt:
   promptStart: str
   promptEnd: str
   prompt_lock: threading.Lock = threading.Lock()
   promptMusic: str
   prompt_music_lock: threading.Lock = threading.Lock()
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
   
   def getVotesUp(self) -> int:
       temp: int = 0
       with self.vote_lock:
           temp = self.votes_up
       return temp
   
   def getVotesDown(self) -> int:
       temp: int = 0
       with self.vote_lock:
           temp = self.votes_down
       return temp
   
   def getNetVotes(self) -> int:
       temp: int = 0
       with self.vote_lock:
           temp = self.votes_up - self.votes_down
       return temp
   
   def getPrompt(self) -> str:
      temp: str = ""
      with self.prompt_lock:
         temp = self.promptStart
      return temp

   def getPromptMusic(self) -> str:
      temp: str = ""
      with self.prompt_music_lock:
         temp = self.promptMusic
      return temp

class Session:
    music_socket: typing.Union[socket.socket, None] = None
    music_socket_lock: threading.Lock = threading.Lock()
    prompters: int = 0
    prompters_lock: threading.Lock = threading.Lock()
    prompts: list[Prompt] = []
    prompts_lock: threading.Lock = threading.Lock()
    

    def promptMusic(self, promptStart: str, promptEnd: str) -> typing.Union[str, None]:
       buffer: str = ""
       prompt: dict[str, str] = {
          "promptStart": promptStart,
          "promptEnd": promptEnd,
        }
       with self.music_socket_lock:
          if self.music_socket is not None:
             self.music_socket.send(convert(prompt))
             stop: bool = False
             while not stop:
                message = self.music_socket.recv(4 * CHUNK)
                data = deconvert(message)
                if type(data) == str:
                   print("ValueError in promptMusic")
                   return buffer
                if data["data"] == "end":
                   stop = True
                   continue
                buffer += data["data"]
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
    
    def disactivateMusic(self) -> None:
       close: dict[str, str] = {"promptStart": "endstart", "promptEnd": "endend",}
       with self.music_socket_lock:
          if self.music_socket is not None:
             self.music_socket.send(convert(close))