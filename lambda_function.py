import json
import requests
import openai

TELEGRAM_TOKEN = "вашият_telegram_token"
OPENAI_API_KEY = "вашият_openai_key"

openai.api_key = OPENAI_API_KEY

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        chat_id = body['message']['chat']['id']
        user_message = body['message']['text']

        # Генериране на отговор с OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply = response.choices[0].message['content']

        # Изпращане на отговор обратно в Telegram
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": bot_reply}
        )

        return {"statusCode": 200}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}