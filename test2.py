import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from mcstatus import JavaServer
def players(msg):
    server = JavaServer.lookup("94.26.229.202", 25565)
    status = server.status()
    return f"Игроков онлайн: {status.players.online}"

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
            if msg == "/онлайн" or True:
                response = players(msg)
                vk.messages.send(user_id=event.user_id, message=response, random_id=0)