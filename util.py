from typing import Union
import ast

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