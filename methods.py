from time import sleep

from requests import get, post
from decouple import config
import json
import random


TOKEN = config('TOKEN')

URL_BASE = "https://api.telegram.org/bot{}".format(TOKEN)
URL_UPDATES = "{}/getUpdates".format(URL_BASE)
URL_SEND_MESSAGE = "{}/sendMessage?".format(URL_BASE)
URL_SEND_STICKER = "{}/sendSticker?".format(URL_BASE)
URL_SEND_PHOTO = "{}/sendPhoto?".format(URL_BASE)
# URL_WEBHOOK = "https://"
# URL_SET_WEBHOOK = "https://api.telegram.org/bot{}/setWebhook?url={}".format(TOKEN, URL_WEBHOOK)
# URL_GET_WEBHOOK_INFO = "{}/bot{}/getWebhookInfo".format(URL_WEBHOOK, TOKEN)
START = 'Começar Amigo Secreto'
CHOOSE = 'Sortear quem começa'


class BotFalar:
    def getme(self):
        self.resp_getme = get('{}/getMe'.format(URL_BASE)).json()
        self.bot_name = self.resp_getme['result']['first_name']
        return self.bot_name

    def get_updates(self, offset = 0, timeout = 0):
        self.last_update_id = 0
        self.resp = get('{}?offset={}&timeout={}'.format(URL_UPDATES, offset, timeout)).json()
        # print(self.resp, self.resp['result'])
        self.result = len(self.resp['result'])
        if self.result >= 1:
            self.last_index = self.resp['result'][self.result - 1]
            self.chat = self.last_index['message']['chat']
            self.last_update_id = self.last_index['update_id']
            self.chat_id = self.chat['id']
            self.first_name = self.chat['first_name']
            if self.last_index['message'].get('text'):
                self.message_text = True
                self.text = self.last_index['message']['text']
            elif self.last_index['message'].get('sticker'):
                self.message_sticker = True
                self.sticker_id = self.last_index['message']['sticker']['file_id']
            else:
                self.send_message("Só é permitido enviar texto e stickers.")
                self.get_updates(offset = self.last_update_id + 1, timeout = 30)
            if 'username' in self.chat:
                self.username = self.chat['username']
            else:
                self.username = self.first_name
            self.handle_updates()
        return self.last_update_id

    def send_message(self, text, reply_markup=None):
        self.message = "{}chat_id={}&text={}".format(URL_SEND_MESSAGE, self.chat_id, text)
        if reply_markup:
            self.message += "&reply_markup={}".format(reply_markup)
        return post(self.message)

    def friend_message(self, chat_id, message):
        if self.message_text:
            post("{}chat_id={}&text={}".format(URL_SEND_MESSAGE, chat_id, message))
        elif self.message_sticker:
            post("{}chat_id={}&sticker={}".format(URL_SEND_STICKER, chat_id, message))

    def resp_msg_to_friend(self, chat_id, message):
        if self.message_text:
            post("{}chat_id={}&text={}".format(URL_SEND_MESSAGE, chat_id, message))
        else:
            post("{}chat_id={}&sticker={}".format(URL_SEND_STICKER, chat_id, message))

    def message_to_all(self, text_all):
        for amigo in self.get_friends():
            self.friend_message(amigo[1], text_all)

    def start_secret_friend(self):
        photo = 'https://imgcdn.portalt5.com.br/6EsuDA5canHPt6OGXBDzdRlyBZE=/400x266/smart/filters:strip_icc()/' \
                's3.portalt5.com.br/imagens/amigo-secreto.png'

        self.send_message("Chegou a hora do ...")
        post("{}chat_id=200598266&photo={}".format(URL_SEND_PHOTO, photo))

    def choose_who_to_start(self):
        self.send_message("E quem começa a brincadeira é ...")
        names = self.get_names()
        sleep(5)
        self.send_message("{}".format(random.choice(names)))

    def sorteio(self):
        self.nomes = self.get_names()
        sorteio = self.nomes[:]
        self.combinados = {}

        for nome in self.nomes:
            if nome in sorteio:
                sorteio.remove(nome)
            sorteado = random.choice(sorteio)
            self.combinados[nome] = sorteado
            sorteio.remove(sorteado)
            if not nome in self.combinados.values():
                sorteio.append(nome)
            if sorteio == []:
                break

        if len(set(self.combinados.keys())) == len(set(self.combinados.values())) == len(set(self.combinados.items())):
            print(self.combinados)
            for name in self.nomes:
                self.name_friend(name, self.combinados[name])
            for each in self.get_friends():
                self.insert_id_friend(each[1], each[0])
            for id_amigo in self.friends():
                self.friend_message(id_amigo[0], "Sorteio realizado com sucesso!\n"
                                                 "Seu amigo secreto é {}".format(id_amigo[1]))


    def handle_updates(self):
        # self.names = self.get_names()
        if self.message_text:
            if self.text.startswith("/start"):
                self.send_message("Olá {}, sou o Bot do Amigo Secreto.".format(self.first_name))
                self.get_updates(offset=self.last_update_id + 1, timeout=30)
            if self.text.startswith("/entrar"):
                if self.first_name in self.get_names():
                    self.send_message("Você já está participando do grupo do amigo secreto {}".format(self.first_name))
                else:
                    self.add_name()
                    self.send_message("{}, seu nome foi adicionado ao grupo do amigo secreto.".format(self.first_name))
            elif self.text.startswith("/del"):
                del_name = self.text[5:]
                self.delete_name(del_name)
                self.send_message("{} foi deletado do grupo.".format(del_name))
            elif self.text.startswith("/list"):
                self.names_list = ["{}".format(i) for i in self.get_names()]
                self.message_list = "\n".join(self.names_list)
                self.send_message("Participantes do amigo secreto\n\n{}".format(self.message_list))
            elif self.text.startswith("/sorteio"):
                self.sorteio()
            elif self.text.startswith("/all"):
                self.message_to_all(self.text[5:])
            elif self.text.startswith("/r") or self.text.startswith("/R"):
                id_name = self.id_of_name(self.chat_id)
                self.resp_msg_to_friend(id_name[0], self.text[3:])
            elif self.text.startswith("/t") and self.chat_id == 200598266:
                self.keyboard = self.build_keyboard([START, CHOOSE])
                self.send_message("Escolha", self.keyboard)
            elif self.text.startswith(START):
                self.start_secret_friend()
            elif self.text.startswith(CHOOSE):
                self.choose_who_to_start()
            else:
                id_friend = self.id_friend()
                self.friend_message(id_friend[0], self.text)
        elif self.sticker_id:
            id_friend = self.id_friend()
            self.friend_message(id_friend[0], self.sticker_id)
        else:
            pass


    def build_keyboard(self, items):
        keyboard = [[item] for item in items]
        reply_markup = {'keyboard': keyboard, "one_time_keyboard": True}
        return json.dumps(reply_markup)


# def set_webhook(self):
#     self.url_setwebhook = post(URL_SET_WEBHOOK)
#     return self.url_setwebhook
#
# def get_webhookinfo(self):
#     self.url_get_webhookinfo = get(URL_GET_WEBHOOK_INFO)
#     return self.url_get_webhookinfo


