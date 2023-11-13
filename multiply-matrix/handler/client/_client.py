import numpy as np
import threading
import json
from socket import *
import configparser
from handler.client._client_message import ClientMessageHandler


config = configparser.ConfigParser()
config.read('config.ini')
SERVER_IP = config["SERVER"]['ip']
SERVER_PORT = int(config["SERVER"]['port'])
MATRIX_SIZE = int(config["MATRIX"]["size"])


class ClientHandler(ClientMessageHandler):
    def __init__(self):
        super().__init__(np.random.randint(0, 100, size=(MATRIX_SIZE, MATRIX_SIZE)))

    def refresh_metrix(self, value):
        self.logger.log("-----{}번째 라운드가 종료되었습니다.-----".format(value + 1))
        self.matrix = np.random.randint(0, 100, size=(MATRIX_SIZE, MATRIX_SIZE))

    def receive(self):
        while True:
            data = json.loads(self.conn.recv(4096))

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
            if req_type == "row":
                self.return_row(value)
            elif req_type == "col":
                self.return_column(value)
            elif req_type == "calculate":
                self.return_result(value)
            elif req_type == "refresh":
                self.refresh_metrix(value)
            elif req_type == "disconnect":
                self.conn.close()
                break

    def run(self):
        self.conn = socket(AF_INET, SOCK_STREAM)
        self.conn.connect((SERVER_IP, SERVER_PORT))

        self.logger.log('서버와 연결되었습니다.')

        th = threading.Thread(target=self.receive)
        th.start()


