import google.generativeai as genai
import vk_api
import os
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from mcstatus import JavaServer
from requests.exceptions import ReadTimeout
from abc import ABC, abstractmethod

vk = None
form_filling_cache = {}
form_checking_cache = {}

with open("ai_text.txt", "r", encoding="utf-8") as file:
    text_data = file.read()

# Настройка API-ключа
genai.configure(api_key="AIzaSyBgI_yz6s4sXS6ImytSJ0Q7OPoKnE_afto")

def write_msg(id, message):
    vk.method('messages.send', {
        'user_id': id,
        'message': message,
        "random_id": vk_api.utils.get_random_id()
    })

def players(user_id, argument):
    server = JavaServer.lookup("94.26.229.202", 25565)
    status = server.status()
    write_msg(user_id, f"Игроков онлайн: {status.players.online}")

# Функция для генерации ответа
def ask_gemini(user_id, question):
    question = question[:500]
    prompt = (f"Ответь на вопрос на основе следующего текста:\n{text_data}\n\nВопрос: {question}\nОтвет: . Ты "
              f"помощник, который помогает пользователям разобраться с вопросами по серверу майнкрафта CMCraft и найти ответы на их "
              f"вопросы. Ответы должны быть не очень длинными и лаконичными с самой важной информацией по вопросу "
              f"пользователя, без кучи лишней информации. Отвечай в дружелюбной форме. Если не знаешь ответ на "
              f"вопрос/не можешь найти ответ в тексте, то отвечай скриптами, которые позволяют пользователям найти "
              f"информацию самостоятельно (по сайту https://cmcraft.su/). Пиши сайт только если не знаешь ответ. "
              f"Умеешь отвечать на закрытые вопросы (да/нет). Например: «Сервер является ванильным?» (Да.) "
              f"Способен анализировать открытые источники из интернета в случае, если вопросы пользователей не относятся к проекту CMCraft. "
              f"Выдаёшь предупреждающие сообщения о неприличном стиле общения, если в тексте вопросов содержится нецензурная брань или некорректные высказывания.")
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    try:
        response = model.generate_content(
            contents=[prompt],
            generation_config={
                "max_output_tokens": 200,
                "temperature": 0.7,
            }
        )
        write_msg(user_id, response.text.strip())
    except Exception as e:
        return f"Произошла ошибка при обработке запроса: {str(e)}"

class messages:
    def __init__(self):
        os.chdir('messages')
        for message_filename in os.listdir():
            with open(message_filename, 'r', encoding='utf-8') as f:
                setattr(self, message_filename[:-4], f.read())
        os.chdir('..')

messages = messages()


class Command(ABC):

    def __init__(self, name: str, process_function, admin: bool):
        self.name = name
        self.process_function = process_function
        self.admin = admin

    @abstractmethod
    def process(self, user_id: int, argument: str):
        pass

class NonServerCommand(Command):

    def __init__(self, name: str, process_function, admin: bool):
        super().__init__(name, process_function, admin)

    def process(self, user_id: int, argument: str):
        if self.admin:
            if user_id in ['kiriabr1', True]:
                self.process_function(user_id, argument)
            else:
                write_msg(user_id, "Отказано в доступе")
        else:
            self.process_function(user_id, argument)

commands_set = {
    NonServerCommand("/онлайн", players, False),
    NonServerCommand("/вопрос", ask_gemini, False),
}

def run():
    global vk
    vk = vk_api.VkApi(token='vk1.a.4eymWFDs0O9VykPbaXeTfNXGEv4fPrIjqsg-rvmKs67yuu3QEIqOR30CmwxWQe-XO97q49vpt24hl5FvxCZuMEH-QNkMsJLfPrM-5YX1h4z_qjk5n5XzTOTdNkJePo4QKOVX-LfuVPLBPhQsjx4ypHTYakGO7-0Ev6Wv8Rltmxs7-7fkL0FamlLKllw0KHB9FgGmySum49VEAhNr7shftw')
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and not event.from_chat:
            if event.to_me:
                user_id = event.user_id
                request = event.text
                if request.startswith('/'):
                    try:
                        space = request.index(' ')
                        command_name, argument = request[0:space], request[space+1:]
                    except:
                        command_name, argument = request, None
                    found = False
                    for command in commands_set:
                        if command.name == command_name:
                            command.process(user_id, argument)
                            found = True
                            break
                    if not found: write_msg(user_id, "Команда не найдена")
                else:
                    if user_id in form_filling_cache:
                        form_filling_cache[user_id].append(request)
                    else:
                        write_msg(user_id, messages.problem)

while True:
    try:
        run()
    except ReadTimeout:
        pass