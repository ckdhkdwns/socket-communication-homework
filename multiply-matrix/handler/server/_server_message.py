import json
import threading


class ServerMessageHandler:
    def __init__(self, encoding):
        self.encoding = encoding
        self.lock = threading.Lock()
        self.time_count = 0

    def make_encoded_json(self, t, value):
        data = dict()
        data["type"] = t
        data["value"] = value
        return json.dumps(data).encode(self.encoding)

    def get_row(self, target_client, row_index):
        # self.lock.acquire()
        target_client.send(self.make_encoded_json("row", row_index))
        row = json.loads(target_client.recv(1024).decode(self.encoding))
        # self.lock.release()
        self.time_count += 1
        return row

    def get_column(self, target_client, col_index):
        # self.lock.acquire()
        target_client.send(self.make_encoded_json("col", col_index))
        col = json.loads(target_client.recv(1024).decode(self.encoding))
        # self.lock.release()
        self.time_count += 1
        return col

    def get_multiplied(self, target_client, row_client, col_client, row_index, col_index, row, col):
        # self.lock.acquire()
        row_col = {
            "row_client": row_client,
            "col_client": col_client,
            "row_index": row_index,
            "col_index": col_index,
            "row": row,
            "col": col
        }
        target_client.send(self.make_encoded_json("calculate", row_col))
        result = target_client.recv(1024).decode(self.encoding)
        # self.lock.release()
        self.time_count += 1
        return result

    def signal_end(self, clients, round_count):
        for c in clients: # 끝나면 클라이언트 행렬 다시 생성
            c.send(self.make_encoded_json("refresh", round_count))
        self.time_count += 1


