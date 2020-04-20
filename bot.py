from _token import token
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
import logging

group_id = 194389939

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log', encoding='UTF-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

    log.setLevel(logging.DEBUG)


class Bot:
    def __init__(self, group_id, token):
        self.token = token
        self.group_id = group_id
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                log.exception('Ошибка в обработке события', err)

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.info("Отправка сообщания")
            mes = event.object.message['text']
            peer_id = event.object.message['peer_id']
            log.info(f'Получено сообщение: "{mes}"')
            mes = f'Ваш запрос: "{mes}"'
            self.api.messages.send(
                message=mes,
                random_id=random.randint(0, 2 ** 5),
                peer_id=peer_id
            )
        else:
            log.info('пока не обрабатываются события %s', event.type)


if __name__ == "__main__":
    configure_logging()
    bot = Bot(group_id, token)
    bot.run()
