from socket import *
import sys
import configparser
import threading
import time
from util.logger import Logger
import numpy as np
import json

config = configparser.ConfigParser()
config.read('config.ini')
SERVER_IP = config["SERVER"]['ip']
t1 = 0

primary_metrix = []


def create_random_metrix():
    return np.random.randint(0, 100, size=(10, 10))


def receive_message(client_socket):
    global t1, primary_metrix
    while True:
        data = json.loads(client_socket.recv(4096))

        # data format
        # {
        #     "req_type" : req_type,
        #     "value" : value
        # }
        # 1) req_type : col, value : 3 -> 3번째 행을 가져오라
        # 2) req_type : row, value : 2 -> 2번째 열을 가져오라
        # 3) req_type : calculate, value : { row: [...], col: [...] } -> 준 값을 계산해라
        # 4) req_type : refresh -> 행렬을 다시 만들라

        req_type, value = data['type'], data['value']
        if req_type == "col":
            col = str(list(primary_metrix[:, int(value)]))
            client_socket.send(col.encode('utf-8'))
        elif req_type == "row":
            row = str(list(primary_metrix[int(value), :]))
            client_socket.send(row.encode('utf-8'))
        elif req_type == "calculate":
            result = sum([r * c for r, c in zip(value['row'], value['col'])])
            client_socket.send(str(result).encode('utf-8'))
        elif req_type == "refresh":
            primary_metrix = create_random_metrix()
        else:
            pass


if __name__ == "__main__":
    primary_metrix = create_random_metrix()
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_IP, 8080))
    logger = Logger("client")

    logger.log('Connected.')

    th = threading.Thread(target=receive_message, args=(client_socket,))
    th.start()


