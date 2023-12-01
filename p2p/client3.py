from utils.logger import Logger
from utils.files import split_file, merge_files
from utils.hash import get_file_hash
from utils.sequence import get_seq_chunk, split_received_data

import threading
import configparser
from socket import *
import json

lock = threading.Semaphore(1)
client_index = "C"
temp = split_file('./files/{}.file'.format(client_index))
chunks_length = len(temp)
sequence_size = 7
# 청크 사이즈 256kb + 7b + 1b
chunk_size = sequence_size + len(temp[0]) + 1 # 1 = 클라이언트 인덱스 ex) "D"


my_chunks = {
    "front": temp[:chunks_length // 2],
    "back": temp[chunks_length // 2:]
}


chunks = {
    "A": [None for _ in range(chunks_length)],
    "B": [None for _ in range(chunks_length)],
    "D": [None for _ in range(chunks_length)]
}

config = configparser.ConfigParser()
config.read('config.ini')
SERVER_IP = config["SERVER"]['ip']
SERVER_PORT = int(config["SERVER"]['port'])
logger = Logger("client")

conn_server = None

clients_connection = {
    13: None,
    23: None,
    34: None
}

def send_chunks(conn, type):
    for index, chunk in enumerate(my_chunks[type]):
        seq = index
        if type == "back":
            seq += chunks_length // 2

        seq_chunk = get_seq_chunk(client_index, sequence_size, seq, chunk)
        conn.send(seq_chunk)



def receive_from_server():
    while True:
        data = conn_server.recv(1024).decode('utf-8')
        if data =="start":
            threads = []
            for index, client in clients_connection.items():
                th = threading.Thread(target=send_chunks, args=(client, 'front'))
                th.start()
                threads.append(th)
            # 4번 클라이언트에게는 back chunks도 보냄
            th = threading.Thread(target=send_chunks, args=(clients_connection[34], 'back'))
            th.start()
            threads.append(th)

            for th in threads:
                th.join()
        if data == "status":
            conn_server.send(
                "status A:{}:B:{}:D:{}".format(
                    chunks_length - chunks["A"].count(None),
                    chunks_length - chunks["B"].count(None),
                    chunks_length - chunks["D"].count(None),
                ).encode("utf-8")
            )
        if data == "end":
            conn_server.close()
            break


def receive_from_client(index, conn):
    count = 0
    while count < chunks_length:
        lock.acquire()
        header = conn.recv(8).decode('utf-8')
        
        client_index = str(header[0])
        seq = int(header[1:])
        
        # client_index = str(conn.recv(1).decode('utf-8'))
        # seq = int(conn.recv(sequence_size))
        content = b''
        for _ in range(256000 // 2048):
            content += conn.recv(2048)
        lock.release()
            
        # lock.acquire()
        # data = conn.recv(chunk_size) # 256008
        # print(len(data))
        # client_index, seq, content = split_chunk(data, sequence_size)



        logger.log("[{}] {}의 {}번째 데이터를 받았습니다. 크기: {}".format(index, client_index, seq + 1, len(content)))
        chunks[client_index][seq] = content

        print("status A:{}:B:{}:D:{} Count: {}".format(
            chunks_length - chunks["A"].count(None),
            chunks_length - chunks["B"].count(None),
            chunks_length - chunks["D"].count(None),
            count
        ))
        count += 1

        # 받아온 청크가 D청크라면 1번, 2번 클라이언트에게도 보냄 여기서 D청크는 back chunks
        if client_index == "D" and seq >= chunks_length//2:
            clients_connection[13].send(get_seq_chunk("D", sequence_size, seq, content))
            clients_connection[23].send(get_seq_chunk("D", sequence_size, seq, content))
        lock.release()

def run_client_connection(port):
    global clients_connection
    conn = socket(AF_INET, SOCK_STREAM)
    conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    conn.bind(('', 8000 + port))
    conn.listen()
    client, addr = conn.accept()
    clients_connection[port] = client
    logger.log("{}의 연결이 성립되었습니다.".format(port))


def connect_client(port):
    global clients_connection
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((SERVER_IP, 8000 + port))
    logger.log("{}와의 연결이 성립되었습니다.".format(port))
    clients_connection[port] = conn


def connect_server():
    global conn_server
    conn_server = socket(AF_INET, SOCK_STREAM)
    conn_server.connect((SERVER_IP, SERVER_PORT))
    logger.log('서버와 연결되었습니다.')


if __name__=="__main__":
    connect_server()
    run_ports = [34] # 8023, 8024
    connect_ports = [13, 23] # 8013, 8023
    threads = []

    # 클라이언트들과의 연결을 성립
    for port in run_ports:
        th = threading.Thread(target=run_client_connection, args=(port,))
        th.start()
        threads.append(th)

    for port in connect_ports:
        connect_client(port)

    for th in threads:
        th.join()

    # 서버에게 데이터를 받아오는 받아오는 쓰레드
    receive_server_thread = threading.Thread(target=receive_from_server)
    receive_server_thread.start()

    # 클라이언트에게 데이터를 받아오는 쓰레드
    rcths = []
    for index, conn in clients_connection.items():
        receive_client_thread = threading.Thread(target=receive_from_client, args=(index, conn))
        receive_client_thread.start()
        rcths.append(receive_client_thread)
    for th in rcths:
        th.join()

    conn_server.send("end 3".encode("utf-8"))
    clients_connection[34].close()

    merge_files(chunks=chunks["A"], output_file="./result_files/3/resultA.file")
    merge_files(chunks=chunks["B"], output_file="./result_files/3/resultB.file")
    merge_files(chunks=chunks["D"], output_file="./result_files/3/resultD.file")
