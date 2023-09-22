from socket import *
import sys
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
SERVER_IP = config["SERVER"]['ip']

clientSock = socket(AF_INET, SOCK_STREAM)
clientSock.connect((SERVER_IP, 8080))

print('Connected.')

while True:
    data = clientSock.recv(1024).decode('utf-8')
    print(data)
    if data == ">> Disconnected.":
        clientSock.close()
        break
    result = sys.stdin.readline().strip()
    clientSock.send(result.encode('utf-8'))

