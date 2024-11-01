import PIL.Image
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.getenv("API_KEY"))



img = PIL.Image.open("images/vegeta.jpg")
model = genai.GenerativeModel(
  model_name='gemini-1.5-pro'
)
response=model.generate_content(["describe this in one scentence", img])
print(response.text)
