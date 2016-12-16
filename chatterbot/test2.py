#!/usr/bin/python
# -*- coding: utf-8 -*-
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot("myBot")
chatbot.set_trainer(ChatterBotCorpusTrainer)

# 使用英文语料库训练它
chatbot.train("chatterbot.corpus.english")

# 开始对话
while True:
    print chatbot.get_response(raw_input(">"))
