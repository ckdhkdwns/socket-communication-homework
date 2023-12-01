from utils.logger import Logger
from utils.files import split_file, merge_files
from utils.hash import get_file_hash
from utils.sequence import get_seq_chunk, split_received_data

import threading
import configparser
from socket import *
import json
import time

lock = threading.Semaphore(1)
client_index = "D"
# temp = split_file("./files/{}.file".format(client_index))
temp = split_file('./files/D.file')
chunks_length = len(temp) 
sequence_size = 7

# 청크 사이즈 256kb + 7b + 1b
chunk_size = sequence_size + len(temp[0]) + 1 # 1 = 클라이언트 인덱스 ex) "D"

my_chunks = {"front": temp[: chunks_length // 2], "back": temp[chunks_length // 2 :]}


chunks = {
    "A": [None for _ in range(chunks_length)],
    "B": [None for _ in range(chunks_length)],
    "C": [None for _ in range(chunks_length)],
}


config = configparser.ConfigParser()
config.read("config.ini")
SERVER_IP = config["SERVER"]["ip"]
SERVER_PORT = int(config["SERVER"]["port"])
logger = Logger("client")

conn_server = None

clients_connection = {14: None, 24: None, 34: None}


def send_chunks(conn, type):
    for index, chunk in enumerate(my_chunks[type]):
        seq = index
        if type == "back":
            seq += chunks_length // 2

        seq_chunk = get_seq_chunk(client_index, sequence_size, seq, chunk)
        conn.send(seq_chunk)



def receive_from_server():
    while True:
        data = conn_server.recv(1024).decode("utf-8")
        if data == "start":
            threads = []
            for index, client in clients_connection.items():
                th = threading.Thread(target=send_chunks, args=(client, "front"))
                th.start()
                threads.append(th)
            # 3번 클라이언트에게는 back chunks도 보냄
            th = threading.Thread(
                target=send_chunks, args=(clients_connection[34], "back")
            )
            th.start()
            threads.append(th)

            for th in threads:
                th.join()
        if data == "status":
            conn_server.send(
                "status A:{}:B:{}:C:{}".format(
                    chunks_length - chunks["A"].count(None),
                    chunks_length - chunks["B"].count(None),
                    chunks_length - chunks["C"].count(None),
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
        for i in range(256000 // 2048):
            c = conn.recv(2048)
            content += c
            if len(c) < 2048:
                print("아이 씨 {} {}".format(i, len(c)))

        lock.release()

        # lock.acquire()
        # data = conn.recv(chunk_size)
        # print(len(data))
        # client_index, seq, content = split_chunk(data, sequence_size)

        
        logger.log("[{}] {}의 {}번째 데이터를 받았습니다. 크기: {}".format(index, client_index, seq + 1, len(content)))
        chunks[client_index][seq] = content
        
        print("status A:{}:B:{}:D:{} Count: {}".format(
            chunks_length - chunks["A"].count(None),
            chunks_length - chunks["B"].count(None),
            chunks_length - chunks["C"].count(None),
            count
        ))
        count += 1

        # 받아온 청크가 C청크라면 1번, 2번 클라이언트에게도 보냄 여기서 C청크는 back chunks
        if client_index == "C" and seq >= chunks_length//2:
            clients_connection[14].send(get_seq_chunk("C", sequence_size, seq, content))
            clients_connection[24].send(get_seq_chunk("C", sequence_size, seq, content))


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
    logger.log("서버와 연결되었습니다.")




if __name__ == "__main__":
    connect_server()
    connect_ports = [14, 24, 34]
    threads = []

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
        receive_client_thread = threading.Thread(
            target=receive_from_client, args=(index, conn)
        )
        receive_client_thread.start()
        rcths.append(receive_client_thread)
    for th in rcths:
        th.join()


    conn_server.send("end 4".encode("utf-8"))

    merge_files(chunks=chunks["A"], output_file="./result_files/4/resultA.file")
    merge_files(chunks=chunks["B"], output_file="./result_files/4/resultB.file")
    merge_files(chunks=chunks["C"], output_file="./result_files/4/resultC.file")
