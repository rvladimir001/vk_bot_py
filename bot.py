from _token import token
import vk_api
import vk_api.bot_longpoll
import random

group_id = 194389939


class Bot:
    def __init__(self, group_id, token):
        self.token = token
        self.group_id = group_id
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                print(err)

    def on_event(self, event):
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            mes = event.object.message['text']
            peer_id = event.object.message['peer_id']
            print("полученое сообщение", mes)
            mes = f'Ваш запрос: "{mes}"'
            self.api.messages.send(
                message=mes,
                random_id=random.randint(0, 2 ** 5),
                peer_id=peer_id
            )
        else:
            print("пока не обрабатываются события", event.type)


if __name__ == "__main__":
    bot = Bot(group_id, token)
    bot.run()
