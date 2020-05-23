from unittest import TestCase
from unittest.mock import patch, Mock, ANY
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType, VkBotMessageEvent, VkBotEvent
from bot import Bot
from copy import deepcopy
import settings


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'date': 1587575002, 'from_id': 4363990, 'id': 68, 'out': 1, 'peer_id': 298989633,
                   'text': 'Привет bot', 'conversation_message_id': 69, 'fwd_messages': [], 'important': False,
                   'random_id': 0, 'attachments': [], 'admin_author_id': 4363990, 'is_hidden': False},
        'group_id': 194389939, 'event_id': '4d85a0f18b27fb607e83306310bf950f7834bf96'
    }

    def test_run(self):
        count = 5
        obj = {'a': 1}
        events = [obj] * count
        long_poller_mock = Mock(return_value=events)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock
        with patch('bot.vk_api.VkApi'):
            with patch('bot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                assert bot.on_event.call_count == count

    INPUTS = [
        'ghbdtn',
        'Привет',
        'А когда?',
        'Где будет?',
        'Зарегистрируй меня',
        'Вениамин',
        'email@gmail.',
        'email@gmail.com'
    ]
    EXPECTED_OUTPUTS = [
        settings.DEFAULT_ANSWER,
        settings.INTENTS[0]['answer'],
        settings.INTENTS[1]['answer'],
        settings.INTENTS[2]['answer'],
        settings.SCENARIOS['registration']['steps']['step1']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['text'],
        settings.SCENARIOS['registration']['steps']['step2']['failure_text'],
        settings.SCENARIOS['registration']['steps']['step3']['text'].format(name='Вениамин', email='email@gmail.com'),
    ]

    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_poller_mock = Mock()
        long_poller_mock.listen = Mock(return_value=events)

        with patch('bot.VkBotLongPoll', return_value=long_poller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []

        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])

        assert real_outputs == self.EXPECTED_OUTPUTS
