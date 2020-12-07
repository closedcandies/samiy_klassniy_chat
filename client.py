import socket

port = int(input())
flag = 0    # Чтобы не париться с многопоточностью, я решил получать и отправлять данные по очереди вот такой я умный да XD

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', port))
sock.connect(('localhost', 8889))
print('connected')
while True:
    if flag:
        print(sock.recv(2048).decode('utf-8'))
        flag = 0
    else:
        msg = input('сообщение введи ало\n').encode('utf-8')
        sock.send(msg)
        flag = 1
