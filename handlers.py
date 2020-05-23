# -*- coding: utf-8 -*-
"""
handler - функция, которая принимает text (текст входящего сообщения) и context (dict)
и возвращает bool: True если шаг пройден и False если данные введены не правильно
"""
import re

re_name = re.compile(r'^[\w\-\s]{3,40}$')
re_email = re.compile(r'\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b')


def handle_name(text, context):
    match = re.match(re_name, text)
    if match:
        context['name'] = text
        return True
    else:
        return False


def handle_email(text, context):
    matchs = re.findall(re_email, text)
    if len(matchs) >= 1:
        context['email'] = matchs[0]
        return True
    else:
        return False
