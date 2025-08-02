import google.generativeai as genai
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from mcstatus import JavaServer

with open("ai_text.txt", "r", encoding="utf-8") as file:
    text_data = file.read()

# Настройка API-ключа
genai.configure(api_key="AIzaSyBgI_yz6s4sXS6ImytSJ0Q7OPoKnE_afto")

def online(msg):
    server = JavaServer.lookup("94.26.229.202", 25565)
    status = server.status()
    return f"Игроков онлайн: {status.players.online}"

def ping_s(msg):
    server = JavaServer.lookup("94.26.229.202", 25565)
    latency = server.ping()
    return f"Время ответа сервера (пинг) {latency} мс"


# Функция для генерации ответа
def ask_gemini(question):
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

        return response.text.strip()

    except Exception as e:
        return f"Произошла ошибка при обработке запроса: {str(e)}"

vk_session = vk_api.VkApi(token="vk1.a.4eymWFDs0O9VykPbaXeTfNXGEv4fPrIjqsg-rvmKs67yuu3QEIqOR30CmwxWQe-XO97q49vpt24hl5FvxCZuMEH-QNkMsJLfPrM-5YX1h4z_qjk5n5XzTOTdNkJePo4QKOVX-LfuVPLBPhQsjx4ypHTYakGO7-0Ev6Wv8Rltmxs7-7fkL0FamlLKllw0KHB9FgGmySum49VEAhNr7shftw")
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

keyboard = VkKeyboard(one_time=True)
keyboard.add_button("Привет", color=VkKeyboardColor.SECONDARY)
keyboard.add_button("Клавиатура", color=VkKeyboardColor.POSITIVE)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            if msg == "/онлайн":
                response = online(msg)
                vk.messages.send(user_id=event.user_id, message=response, random_id=0)
            elif msg == "/сервер":
                response = ping_s(msg)
                vk.messages.send(user_id=event.user_id, message=response, random_id=0)
            elif msg.startswith("/вопрос"):
                response = ask_gemini(msg)
                vk.messages.send(user_id=event.user_id, message=response, random_id=0)