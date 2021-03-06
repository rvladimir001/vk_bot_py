# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent
import random
import logging
import handlers

try:
    import settings
except ImportError:
    exit("Do cp settings.py.default settings.py and set token")

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


class UserState:
    """Состояние пользователя внтури сценария"""

    def __init__(self, scenario_name, step_name, context=None):
        self.scenario_name = scenario_name
        self.step_name = step_name
        self.context = context or {}


class Bot:
    """
    Echo bot for vk

    Use python 3.8.2
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id из группы вк
        :param token: секретный токен для доступа
        """
        self.token = token
        self.group_id = group_id
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()
        self.user_states = dict()  # user_id -> UserState

    def run(self):
        """запуск бота"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as err:
                log.exception('Ошибка в обработке события', err)

    def on_event(self, event):
        """
        Обработка сообщения бота - отправляет сообщение назад
        :param event:VkBotEventMessage object
        :return None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info("Мы пока не умеем обрабатывать события такого типа %s", event.type)
            return
        user_id = event.object.peer_id
        text = event.object.text
        if user_id in self.user_states:
            text_to_send = self.continue_scenario(user_id, text)
        else:
            # search intent
            for intent in settings.INTENTS:
                log.debug(f'User gets intent {intent}')
                if any(token in text for token in intent['tokens']):
                    # run intent
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 5),
            peer_id=user_id
        )

    def continue_scenario(self, user_id, text):
        # continue scenario
        state = self.user_states[user_id]
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        if handler(text=text, context=state.context):
            # next step
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                log.info('Зарегистрирован {name}{email}'.format(**state.context))
                self.user_states.pop(user_id)
        else:
            text_to_send = step['failure_text'].format(**state.context)
        return text_to_send

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        self.user_states[user_id] = UserState(scenario_name=scenario_name, step_name=first_step)
        return text_to_send


if __name__ == "__main__":
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()
