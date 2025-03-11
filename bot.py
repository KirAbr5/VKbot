import json
import vk_api
import openai
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

#Парсер
from bs4 import BeautifulSoup
from urllib.request import urlopen

urls = [
    "https://education.vk.company/"
    "https://education.vk.company/students",
    "https://education.vk.company/news?target_audience=students&page=1",
    "https://internship.vk.company/internship",
    "https://internship.vk.company/vacancy",
    "https://cups.online/ru/",
    "https://education.vk.company/products_for_education",
    "https://education.vk.company/education_projects",
]

with open('text.txt', 'w', encoding='utf-8') as file:
    for url in urls:
        try:
            response = urlopen(url)
            html_code = response.read().decode('utf-8')

            soup = BeautifulSoup(html_code, 'html.parser')

            title = soup.find('title').text.strip() if soup.find('title') else 'No Title'
            file.write(title + '\n\n')
            print(title)

            paragraphs = soup.find_all('p')
            for paragraph in paragraphs:
                text = paragraph.get_text(strip=True)
                print(text)
                file.write(text + '\n')

        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

#GPT
openai.api_base = "https://openai.loe.gg/v1"
openai.api_key = "your token"

with open("text.txt", "r", encoding="utf-8") as file:
    text_data = file.read()

def ask_gpt(question):
    """Отправляет запрос в ChatGPT и получает ответ."""
    prompt = (f"Ответь на вопрос на основе следующего текста:\n{text_data}\n\nВопрос: {question}\nОтвет: . Ты "
              f"помощник, который помогает пользователям разобраться на платформе VK Education и найти ответы на их "
              f"вопросы. Ответы должны быть не очень длинными и лаконичнми с самйо важной информацией по вопросу "
              f"пользователя, без кучи лишней информации. Отвечай в дружелюбной форме. Если не знаешь ответ на "
              f"вопрос/не можешь найти ответ в тексте, то отвечает скриптами, которые позволяют пользователям найти "
              f"информацию самостоятельно ( по сайту https://education.vk.company/). Пиши сайт только если не знаешь ответ"
              f"Дополнительные требования к боту:Умеет отвечать на закрытые вопросы (да/нет). Например: «Возможно ли взять несколько проектов?» (Да.)Способен анализировать открытые источники из интернета в случае, если вопросы пользователей не относятся к сайту VK Education Projects.Выдаёт предупреждающие сообщения о неприличном стиле общения, если в тексте вопросов содержится нецензурная брань или некорректные высказывания. Способен анализировать открытые источники из интернета в случае, если вопросы пользователей не относятся к сайту VK Education Projects.")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ты помощник, отвечающий на вопросы по тексту."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    return response["choices"][0]["message"]["content"].strip()


vk_session = vk_api.VkApi(token="your token")
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

keyboard = VkKeyboard(one_time=True)
keyboard.add_button("Привет", color=VkKeyboardColor.SECONDARY)
keyboard.add_button("Клавиатура", color=VkKeyboardColor.POSITIVE)


def sender(id, text):
    vk_session.method("messages.send", {"user_id":id, "message":text, "random_id":0})

def send_stick(id, number):
    vk.messages.send(user_id=id, sticker_id=number, random_id=0)

def send_photo(id, url):
    vk.messages.send(user_id=id, attachment=url, random_id=0)


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            if msg == "start":
                sender(id, "Привет! Я чат-бот ВК, разработанный на python для проекта VK Education Projects.")
                send_stick(id, 107462)
            elif msg == "photo":
                send_photo(id, "photo-227582531_457239019")
            else:
                response = ask_gpt(msg)
                vk.messages.send(user_id=event.user_id, message=response, random_id=0)
