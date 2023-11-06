from socket import *
import threading
import time
from util import equation
import configparser
from util.logger import Logger
import json
import numpy as np


config = configparser.ConfigParser()
config.read('config.ini')

TIME_OUT = int(config["SERVER"]["timeout"])
SERVER_PORT = int(config["SERVER"]["port"])

sec = 0
client_results = []
client_sockets = []

log = ''

rounds = {}
def time_count(server):
    global sec, client_results
    while sec < TIME_OUT:
        sec += 1
        time.sleep(1)

    logger.log("[{}] The total sum is {}".format(sec, sum(client_results)))
    logger.log("[{}] Server closed.".format(sec))

    for i in client_sockets:
        i.send("Disconnected.".encode('utf-8'))
    server.close()


def make_encoded_json(t, value, encoding='utf-8'):
    data = {}
    data["type"] = t
    data["value"] = value
    return json.dumps(data).encode(encoding)


def _round(round_count):
    global client_sockets

    matrix_input = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    matrix_output = [(2, 3), (1, 3), (1, 2), (0, 3), (0, 2), (0, 1)]

    m = [np.empty((10, 10)) for _ in range(6)]

    def calculate_metrix(i):
        input_clients = [client_sockets[matrix_input[i][0]], client_sockets[matrix_input[i][1]]] # 행렬 정보를 줄 클라이언트
        output_clients = [client_sockets[matrix_output[i][0]], client_sockets[matrix_output[i][1]]] # 행렬을 계산할 클라이언트

        for row_index in range(10):
            input_clients[0].send(make_encoded_json("row", row_index))
            row = json.loads(input_clients[0].recv(1024).decode('utf-8'))

            for col_index in range(10):
                input_clients[1].send(make_encoded_json("col", col_index))
                col = json.loads(input_clients[1].recv(1024).decode('utf-8'))

                fair_num = row_index % 2
                row_col = {
                    "row": row,
                    "col": col
                }
                result = -1
                if fair_num == 0:
                    output_clients[0].send(make_encoded_json("calculate", row_col))
                    result = output_clients[0].recv(1024).decode('utf-8')
                else:
                    output_clients[1].send(make_encoded_json("calculate", row_col))
                    result = output_clients[1].recv(1024).decode('utf-8')
                m[i][row_index][col_index] = result

    for i in range(6):
        calculate_metrix(i)

    for c in client_sockets: # 끝나면 클라이언트 행렬 다시 생성
        c.send(make_encoded_json("refresh", 0))

    rounds["round_{}".format(round_count)] = m


def client_thread(client, addr):
    client_index = 0

    client_sockets.append(client)

    logger.log("[{}] Client '{}' ({}) is connected".format(sec, str(addr[0]), str(len(client_sockets))))

    if len(client_sockets) == 4:
        round_count = 1
        while round_count <= 10:
            _round(round_count)
            round_count += 1

    print(rounds)


if __name__ == "__main__":
    logger = Logger("server")
    server_socket = socket(AF_INET, SOCK_STREAM)
    try:
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen()

        logger.log("[{}] The Server is running on {}:{}".format(sec, "127.0.0.1", str(SERVER_PORT)))

        # System clock ++
        t = threading.Thread(target=time_count, args=(server_socket,))
        t.start()

        while True:
            client, addr = server_socket.accept()
            connection_thread = threading.Thread(target=client_thread, args=(client, addr))
            connection_thread.start()
    except Exception as e:
        logger.log(">> {}".format(e))
        server_socket.close()
