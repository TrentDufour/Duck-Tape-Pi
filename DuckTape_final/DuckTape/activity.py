###__LIBRARYS__#####
# pillow is used from opening different image file formats
#import PIL.Image
#allows python to interact with the operating system
import os
# this library "shutil"(shell utility) makes it to were i can maipulate the file system
#import shutil
#AI
import google.generativeai as genai
#this library readskey-values pairs from a (.env) file and sets them as enviroment values
from dotenv import load_dotenv
load_dotenv()
import time

from file_orginize import read, write, clock, read_file

#this line configures the gemini and sets the API key from the .env file in local storage
genai.configure(api_key=os.getenv("API_KEY"))
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 69,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

#this looks in the ftp file folder and filepath variable stores filepath
file_path = "/home/logan/files"
local_path = "/home/logan/DuckTape/images"

while True:
    if clock == 0:
        read()
        time.sleep(1)
    if clock == 1:
        write(read_file)
        time.sleep(30)

