import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import TOKEN
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

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
            if msg == "photo":
                send_photo(id, "photo-227582531_457239019")
