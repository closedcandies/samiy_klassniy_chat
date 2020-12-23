import socket
import select
import sqlite3
import csv

IP = '127.0.0.1'
PORT = 7777
QUEUE_LENGTH = 5
CODING = 'utf-8'
DATABASE_NAME = 'chat'
PATH = '/home/vovan/PycharmProjects/samiy_klassniy_chat'
LAST_MESSAGES = 5   # столько последних сообщений мы будем отправлять клиенту


class Server:
    def __init__(self):
        self.active_users = dict()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((IP, PORT))
        self.server_socket.listen(QUEUE_LENGTH)
        self.server_socket.setblocking(False)
        self.active_users[self.server_socket] = ''
        self.read_inputs()
        self.database = sqlite3.connect(DATABASE_NAME).cursor()

    def read_inputs(self):
        while True:
            sockets = self.active_users.keys()
            read_sockets, write_sockets, exception_sockets = select.select(sockets, sockets, sockets)

            for sock in read_sockets:
                if sock is self.server_socket:
                    client_socket, client_address = sock.accept()
                    client_id = int(client_socket.recv(1024).decode(CODING))
                    self.active_users[client_socket] = client_id
                    self.get_chats(client_socket)

                else:
                    request = str(sock.recv(1024).decode(CODING)).split(':')
                    request_modifyer = request[0]
                    arguments = request[1::]

                    if request_modifyer == 'gp':
                        self.get_profiles(sock, *arguments)

                    elif request_modifyer == 'nc':
                        self.create_chat(sock, *arguments)

                    elif request_modifyer == 'nm':
                        self.spread_message(sock, *arguments)

                    elif request_modifyer == 'gm':
                        self.get_chat_messages(sock, *arguments)

    def get_chats(self, client):
        client_id = self.active_users[client]
        chats = self.database.execute("""SELECT * FROM chats WHERE
         user1_id = ? or user2_id = ?""", (client_id, client_id)).fetchall()

        ''' Получаем номер клиента (чтобы отсылать информацию с именем собеседника) и собираем ответ'''
        response = list()
        for chat in chats:
            chat = list(chat)
            companion_name = 3 if client_id == chat[2] else 4  # здесь получаем индекс столбца с именем собеседника
            response.append('{}:{}'.format(chat[0], chat[companion_name]))

        try:
            client.send(str(response).encode(CODING))
        except Exception as e:
            self.handle_exception(client, e)

    # TODO: fix sql injection here
    def get_profiles(self, client, name):
        response = self.database.execute("""SELECT * FROM profiles WHERE name = '?'""", (name, )).fetchall()
        try:
            client.send(str(response).encode(CODING))
        except Exception as e:
            self.handle_exception(client, e)

    def create_chat(self, client, nickname, id2, anonymous):
        new_id = int(''.join(list(self.database.execute("""SELECT MAX(id) FROM chats""").fetchall())[0])) + 1

        if anonymous:
            user2_nickname = self.database.execute("""SELECT default_nickname FROM profiles WHERE id = ?""", (id2, ))
        else:
            user2_nickname = self.database.execute("""SELECT name FROM profiles WHERE id = ?""", (id2, ))

        ''' Создаем новый файл с копией чата '''
        file_path = '{}/chat{}.csv'.format(PATH, new_id)
        file = open(file_path, 'w')
        file.close()

        ''' Обновляем базу данных '''
        self.database.execute("""INSERT INTO chats(user1_id, user2_id, user1_nickname, user2_nickname, chat_copy) 
        VALUES(?, ?, ?, ?, ?)""", (self.active_users[client], id2, nickname, user2_nickname, file_path))

        for active in self.active_users:
            if self.active_users[active] == int(id2):
                try:
                    active.send('nc:{}'.format(nickname).encode(CODING))
                except Exception as e:
                    self.handle_exception(active, e)

    def spread_message(self, client, chad_id, message):

        ''' Заносим новое сообщение в копию '''
        with open('{}/chat{}.csv'.format(PATH, chad_id), 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"')
            writer.writerow((str(self.active_users[client]), message))

        ''' Ищем получателя в базе данных '''
        request = list(self.database.execute("""SELECT user1_id, user2_id FROM chats 
        WHERE id = ?""", (chad_id, )).fetchall())
        request = list(int(''.join(list(request)[i])) for i in range(2))
        receiver = request[0] if request[0] != self.active_users[client] else request[1]

        ''' Отправляем ему новое сообщение '''
        for active in self.active_users:
            if self.active_users[active] == receiver:
                try:
                    active.send('nm:{}:{}'.format(chad_id, message).encode(CODING))
                except Exception as e:
                    self.handle_exception(active, e)

    def get_chat_messages(self, client, chat_id):
        copy_path = ''.join(list(self.database.execute("""SELECT chat_copy FROM chats WHERE id = ?""",
                                                       (chat_id, )).fetchall())[0])
        with open(copy_path, 'r') as file:
            response = list(csv.reader(file, delimiter=',', quotechar='"'))[-LAST_MESSAGES::]
        try:
            client.send(str(response).encode(CODING))
        except Exception as e:
            self.handle_exception(client, e)

    def handle_exception(self, client, exception):
        print('something went wrong: {}'.format(exception))
        client.close()
        del self.active_users[client]


def main():
    print('server was started')
    s = Server()
    print('server was stopped')


if __name__ == '__main__':
    main()
