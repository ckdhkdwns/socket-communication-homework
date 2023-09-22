from socket import *
import sys

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect(('127.0.0.1', 8080))

print('연결 확인 됐습니다.')

while True:
    data = clientSock.recv(1024)
    print(data.decode('utf-8'))
    result = sys.stdin.readline().strip()
    clientSock.send(result.encode('utf-8'))

