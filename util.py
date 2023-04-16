from typing import Union
import ast
import socket
from pyngrok.ngrok import NgrokTunnel

def convert(d: dict) -> bytes:
   """
   Converts the dictionary into bytes using utf-8 encoding.

   Parameters:
      d (dict): the dict to convert.

   Returns:
      bytes: The converted dictionary.
   """
   return (bytes(str(d), "utf-8"))

def deconvert(message: bytes) -> Union[str, dict]:
   """
   Converts the bytes into a str or dict using utf-8 encoding.

   Parameters:
      message (bytes): the bytes to convert.

   Returns:
      str | dict: The converted dictionary or string if failed.
   """
   strMessage: str = message.decode("utf-8") # decoded string
   if strMessage == "": # if empty, return string
      return strMessage
   try: # try to convert it to dict, return string if fails
      dictMessage: dict = ast.literal_eval(strMessage)
      return dictMessage
   except ValueError:
      return strMessage
   except SyntaxError:
      return strMessage
   return strMessage

def get_ngrok_public_ip_address(tunnel: NgrokTunnel)-> str:
   """
   Gets the IP address of the ngrok tcp tunnel.

   Parameters:
      tunnel (NgrokTunnel): the grok tunnel.
   
   Returns:
      str: A mix of the IP address and the port number.
   """
   split: list[str] = tunnel.public_url.replace("tcp://", "").split(":")
   url: str = split[0] # the domain of the url (without port Number)
   return f"Host ip address: {socket.gethostbyname(url)}, port: {split[1]}"