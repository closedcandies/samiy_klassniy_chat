import socket
import select

all_inputs = list()
all_outputs = list()


def waiting_for_read(queue, server):
    for element in queue:
        if element is server:
            client, adress = element.accept()
            all_inputs.append(client)
            element.setblocking(False)
        else:
            try:
                data = element.recv(1024)
                print('Новое сообщение от {}: {}'.format(element, data.decode('utf-8')))
                if element not in all_outputs:
                    all_outputs.append(element)
            except Exception as e:
                print('Какая-то фигня!!! {}. Закрываем соединение...'.format(e))
                all_inputs.remove(element)
                element.close()


def waiting_for_write(queue):
    for element in queue:
        try:
            element.send('Хорошая работа, Олег!!!'.encode('utf-8'))
        except Exception as e:
            print('Какая-то фигня!!! {}. Закрываем соединение...'.format(e))
            all_outputs.remove(element)


if __name__ == '__main__':
    '''запускаем сервер'''
    main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    main_socket.bind(('localhost', 8889))
    main_socket.listen(5)
    main_socket.setblocking(False)
    all_inputs.append(main_socket)

    '''основной алгоритм'''
    while True:
        try:
            """Здесь я хз почему он кидает в exceptions все инпуты... Наверное, потому что все соединения,
             которые соединились, по любому есть в all_inputs(по логике проги) Изучал вот тут https://habr.com/ru/company/alfa/blog/354728/
             если кто знает, ка это работает. Напишите мне плз я тут почти умер с этой библиотекой (select)"""
            inputs, outputs, exceptions = select.select(all_inputs, all_outputs, all_inputs)
            waiting_for_read(inputs, main_socket)
            waiting_for_write(outputs)
            '''хер знает, че с exceptions делать XD'''
        except KeyboardInterrupt:
            print('Сервер умер всем пока')
            main_socket.close()
            exit()
