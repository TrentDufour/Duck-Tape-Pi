

import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 69,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
  system_instruction="explain things i a helpful way in 10 words or less",
)

history = []

while True:
    user_input = input("You: ")

    chat_session = model.start_chat(
        history=history
        
    )

    response = chat_session.send_message(user_input)
    model_response = response.text
    print(f"bot: {model_response}")
    print()
    history.append({"role": "user", "parts": [user_input]})
    history.append({"role": "model", "parts": [model_response]})