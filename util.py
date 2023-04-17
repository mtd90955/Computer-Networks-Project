from typing import Union
import ast
import socket
from pyngrok.ngrok import NgrokTunnel

def convert(d: dict) -> bytes:
   return (bytes(str(d), "utf-8"))

def deconvert(message: bytes) -> Union[str, dict]:
   strMessage: str = message.decode("utf-8")
   if strMessage == "":
      return strMessage
   try:
      dictMessage: dict = ast.literal_eval(strMessage)
      return dictMessage
   except ValueError:
      return strMessage
   except SyntaxError:
      return strMessage
   return strMessage

def get_ngrok_public_ip_address(tunnel: NgrokTunnel)-> str:
   split: list[str] = tunnel.public_url.replace("tcp://", "").split(":")
   url: str = split[0]
   return f"Host ip address: {socket.gethostbyname(url)}, port: {split[1]}"