from handler.server._server_message import ServerMessageHandler
import threading
import numpy as np
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

MATRIX_SIZE = int(config["MATRIX"]["size"])


class RoundHandler(ServerMessageHandler):
    def __init__(self, logger, clients, encoding="utf-8"):
        super().__init__(encoding)
        self.logger = logger
        self.clients = clients
        self.matrix_input = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        self.matrix_output = [(2, 3), (1, 3), (1, 2), (0, 3), (0, 2), (0, 1)]
        self.total_results = []
        self.round_result = []
        self.round_count = 0

        self.lock = threading.Lock()

    def round(self):
        ths = []

        for i in range(6):
            th = threading.Thread(target=self.round_thread, args=(i,))
            ths.append(th)
            th.start()
        for th in ths:
            th.join()

        #라운드 종료
        self.signal_end(self.clients, self.round_count)

    def round_thread(self, index):
        # 행렬 정보를 줄 클라이언트와 행렬 정보를 계산할 클라이언트를 분리
        input_clients = [
            self.clients[self.matrix_input[index][0]],
            self.clients[self.matrix_input[index][1]]
        ]
        output_clients = [
            self.clients[self.matrix_output[index][0]],
            self.clients[self.matrix_output[index][1]]
        ]

        self.lock.acquire()
        for row_index in range(MATRIX_SIZE):
            row = self.get_row(input_clients[0], row_index)

            for col_index in range(MATRIX_SIZE):

                col = self.get_column(input_clients[1], col_index)

                fair_num = row_index % 2  # 공평하게 분배하기 위한 상수
                result = self.get_multiplied(output_clients[fair_num],
                                             self.matrix_input[index][0], # 무슨 클라이언트인지
                                             self.matrix_input[index][1],
                                             row_index, col_index,
                                             row, col)
                self.update_result(result, index, row_index, col_index)
        self.lock.release()


    def update_result(self, result, index, row_index, col_index): # 받아온 값을 업데이트
        self.round_result[index][row_index][col_index] = result

    def reset_result(self):
        self.round_result = [np.empty((MATRIX_SIZE, MATRIX_SIZE)) for _ in range(6)]  # 6개의 빈 행렬 생성

    def save_round_result(self):
        temp = dict()
        temp["time"] = self.time_count
        temp["result"] = self.round_result
        self.total_results.append(temp)

    def end_round(self):
        self.round_count += 1
        self.time_count = 0
        self.reset_result()

    def print_result(self):
        self.logger.log("100라운드가 모두 끝났습니다.")
        self.logger.log("=====라운드별 소요시간=====")
        for i in range(len(self.total_results)):
            self.logger.log("{}번째 라운드의 소요시간은 {}sec입니다.".format(i+1, self.total_results[i]["time"]))
        self.logger.log("=====라운드별 곱셈결과=====")
        for i in range(len(self.total_results)):
            self.logger.log("-----라운드 {}-----".format(i+1))
            for j in range(6):
                self.logger.log("{}번째 클라이언트와 {}번째 클라이언트의 곱셈 결과입니다.".format(
                    self.matrix_input[0], self.matrix_input[1]))
                for k in range(MATRIX_SIZE):

                    row = list(map(int, self.total_results[i]["result"][j][k]))
                    row = list(map(str, row))
                    self.logger.log(" ".join(row))

    def run(self):
        self.reset_result()
        while self.round_count < 100:
            self.round()
            self.save_round_result()
            self.end_round()
        self.print_result()


