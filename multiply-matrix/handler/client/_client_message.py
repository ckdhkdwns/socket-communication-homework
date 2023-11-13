from util.logger import Logger


class ClientMessageHandler:
    def __init__(self, matrix):
        self.logger = Logger('client')
        self.conn = None
        self.matrix = matrix

    def return_row(self, value):
        self.logger.log("서버에게 {}번째 행을 전송합니다.".format(value + 1))
        row = str(list(self.matrix[int(value), :]))
        self.conn.send(row.encode('utf-8'))

    def return_column(self, value):
        self.logger.log("서버에게 {}번째 열을 전송합니다.".format(value + 1))
        col = str(list(self.matrix[:, int(value)]))
        self.conn.send(col.encode('utf-8'))

    def return_result(self, value):
        self.logger.log("{}번째 클라이언트와 {}번째 클라이언트의 행렬 곱셈입니다. {}번째 행 × {}번째 열.".format(
            value["row_client"], value["col_client"], value["row_index"], value["col_index"]
        ))
        result = sum([r * c for r, c in zip(value['row'], value['col'])])
        self.conn.send(str(result).encode('utf-8'))
