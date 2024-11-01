#file handling
#from notifications import picture, pic_disc
import os
# this library "shutil"(shell utility) makes it to were i can maipulate the file syem
import PIL.Image
import time
import mysql.connector as mariadb
import shutil
import google.generativeai as genai
#this library readskey-values pairs from a (.env) file and sets them as enviroment values
#from dotenv import load_dotenv
#load_dotenv()
#configures the gemini API key from a dotenv file where the key is stored along with a variable
genai.configure(api_key=os.getenv("API_KEY"))


mariadb_connection = mariadb.connect(user= 'sqluser', password = '123',database="DuckTape", host = 'localhost')
create_cusor = mariadb_connection.cursor()

#set a location were the files from the camera are stored
file_path = "/home/logan/files"
#set a location where the files from the ftp are transferd to
local_path = "/home/logan/DuckTape/images"

#creating a function for a reading phase that checks the file #path for picture(.jpg extension) specific files and see if it #is in the local path, if not, it will copy that file to the #local path and then returns a new file that can be used for #the write phase
clock = 0
read_file = ""
def read():
    global clock, read_file
    # iterate throuh the files in filepath
    for file in os.listdir(file_path):
        #checks for correct file type
        if ".jpg" in file:
            #checks to see if it is already stored localy
            if file not in os.listdir(local_path):
                shutil.copy(f"{file_path}/{file}", f"{local_path}/{file}")
                new_file = f"{local_path}/{file}"
                clock = 1
                read_file= new_file
                break
                #turns the clock o one to start writing
            
# The write fonction only executes when the clock is set to 1 #and takes a file that it collected during the read phase and #processes the image with gemini
def write(file: str):
    global clock
    #set an image variable for gemini to process(uses the file from the read function)
    img=PIL.Image.open(file)
    model =genai.GenerativeModel(
    model_name="gemini-1.5-pro"
    )
    # this confgures the response it passes a prompt as an arguement and the image as another that the prompts follows to process the image
    response=model.generate_content(["describe this in a scentence", img])
    # setting mariadb variables to update to database table (pics)
    filename = file
    description = response.text
    #this command is what is being ran in the mariadb and inserts are variable sort of like a (f"string")
    sql_statement = 'INSERT INTO pics (filename, response) VALUES (%s, %s);'
    create_cusor.execute(sql_statement, (filename, description))
    mariadb_connection.commit()
    #description.lower()
    #if "vegeta" in description:
        #picture = filename
        #pic_disc = description

    # updates terminal to track changes
    print (response.text)
    # sets the clock back to zero to read again
    clock = 0

####### MAIN ############
while True:
    if clock == 0:
        read()
        time.sleep(1)
    if clock == 1:
        write(read_file)
        time.sleep(30)
