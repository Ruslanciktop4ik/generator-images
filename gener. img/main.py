import telebot
import json
import time
import requests

import uuid
import base64
from PIL import Image
from io import BytesIO

TELEGRAM_TOKEN = '7699404341:AAF4l4_QaMtD96AtFmYhxEDVFcD3rD2JHJA'
API_KEY = 'DA87918DE3924480B523D26FE6D5FFF8'
SECRET_KEY = 'CA4ECD6DE808BC88EA24DEAE6FA1F3F9'

bot = telebot.TeleBot(TELEGRAM_TOKEN)

class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f"{prompt}"
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)
def save_images_from_base64(images_base64):
    filename = 'exmp.png'
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(images_base64[0]))
    print(f"Изображение сохранено как {filename}")
    return filename

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, "Привет отправь описание картинки, и я сгенерирую ее")

@bot.message_handler(func = lambda m: True)
def handle_prompt(message):
    prompt = message.text
    bot.send_message(message.chat.id, "Генерирую изображение подожди несколько минуток...")

    try:
        pipeline_id = api.get_pipeline()
        uuid = api.generate(prompt, pipeline_id)
        files = api.check_generation(uuid)
        filename = save_images_from_base64(files)
        with open(filename, 'rb') as f:
            bot.send_photo(message.chat.id, f, caption="Вот что получилось!")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")
    
if __name__ == '__main__':
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', API_KEY, SECRET_KEY)
    print("FusionBrainAPI запущен.")
    bot.polling(none_stop=True)