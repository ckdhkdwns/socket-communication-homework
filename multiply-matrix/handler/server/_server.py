from socket import *
import threading
import configparser
from util.logger import Logger
from handler.server._round import RoundHandler
import json

config = configparser.ConfigParser()
config.read('config.ini')

TIME_OUT = int(config["SERVER"]["timeout"])
SERVER_IP = config["SERVER"]["ip"]
SERVER_PORT = int(config["SERVER"]["port"])


class ServerHandler:
    def __init__(self):
        self.logger = Logger("server")
        self.clients = []

    def client_thread(self, client):
        self.clients.append(client)
        self.logger.log("{}번째 클라이언트가 접속했습니다.".format(len(self.clients)))

    def send_disconnect_signal(self):
        for c in self.clients:
            data = dict()
            data["type"] = "disconnect"
            data["value"] = -1
            c.send(json.dumps(data).encode("utf-8"))

    def run(self):
        server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            server_socket.bind(('', SERVER_PORT))
            server_socket.listen()

            self.logger.log("서버가 {}:{}에서 실행중입니다.".format(SERVER_IP, str(SERVER_PORT)))

            while True:
                client, addr = server_socket.accept()
                connection_thread = threading.Thread(target=self.client_thread, args=(client, ))
                connection_thread.start()
                clients_count = len(self.clients)
                if clients_count == 4:  # 만약 클라이언트 4개가 접속하면 계산 시작
                    self.logger.log("연산을 시작합니다...")
                    r = RoundHandler(self.logger, self.clients)
                    r.run()
                    self.send_disconnect_signal()
                    server_socket.close()
                    break

        except Exception as e:
            self.logger.log(">> {}".format(e))
            server_socket.close()

