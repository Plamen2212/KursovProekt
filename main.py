import json
import os
import requests
import time
from dotenv import load_dotenv
from openai import OpenAI

# to do more:
# raid limit from spamming 
# cache response
# integrate with aws lambda
# log for errors
# for now is this

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY env variable is not set")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN env variable is not set")

client = OpenAI(
    api_key=OPENAI_API_KEY,
)


def ask(question):
    try:
        response = client.chat.completions.create(
            model = "gpt-4o", #gpt-4o
            messages=[
                {"role": "user", "content": question}
            ],
            max_tokens=1000
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        return f"Error: {e}"

def send_to_telegram(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Oopsie! Nemoa go izprata tova suobshtenie: {e}")
        return False
    
def telegram_updates(offset=0):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {
        "offset": offset,
        "timeout": 10
    }

    try:
        response = requests.get(url, params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to update: {response.text}")
            return False
    except Exception as e:
        print(f"Oopsie! Nemoa go izprata tova suobshtenie: {e}")
        return False

def handle_message(message):
    try:
        chat_id = message.get("chat", {}).get('id')
        text = message.get("text", '')
        user_name = message.get("from", {}).get("first_name", "User")

        if chat_id and text:
            print(f"\n {user_name} asks: {text}")

            answer = ask(text)
            print(f"OpenAI says: ", answer)
            
            success = send_to_telegram(chat_id, answer)
            if success:
                print(f"Response sent to {user_name}")
            else:
                print(f"Failed to send response to {user_name}")

            return True
        return False            
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("Bot is starting......")  
    print("Press Ctrl+C to stop")

offset = 0

while True:
    try:
        updates = telegram_updates(offset)

        if updates and updates.get("ok"):
            for update in updates.get("result", []):
                if "message" in update:
                    handle_message(update["message"])   
                offset = update["update_id"] + 1
            
        time.sleep(1)        
    except KeyboardInterrupt: 
        print(f"Bot stopped by user") 
        break
    except Exception as e: 
        print(f"Error in loop: {e}") 
        time.sleep(5)        