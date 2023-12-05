from utils.logger import Logger
from utils.files import split_file, merge_files
from utils.hash import get_file_hash
from utils.sequence import get_seq_chunk, split_received_data

import threading
import configparser
from socket import *
from queue import Queue
import time


lock = threading.Semaphore(1)
client_index = "A"
temp = split_file("./files/B.file")
chunks_length = len(temp)
sequence_size = 63

# 청크 사이즈 256kb + 7b + 1b
chunk_size = sequence_size + len(temp[0]) + 1 # 1 = 클라이언트 인덱스 ex) "D"

my_chunks = {"front": temp[: chunks_length // 2], "back": temp[chunks_length // 2 :]}

chunks = {
    "B": [None for _ in range(chunks_length)],
    "C": [None for _ in range(chunks_length)],
    "D": [None for _ in range(chunks_length)],
}

config = configparser.ConfigParser()
config.read("config.ini")
SERVER_IP = config["SERVER"]["ip"]
SERVER_PORT = int(config["SERVER"]["port"])
logger = Logger("client")


conn_server = None
send_connections = {12: None, 13: None, 14:None}
receive_connections = {21: None, 31: None, 41: None}


send_queue = Queue()

clock_count = 0

progresses = {
    "B": 0,
    "C": 0,
    "D": 0
}

def clock():
    global clock_count
    while True:
        clock_count += 1
        time.sleep(1)
        logger.log("[{}s]현재 진행도  {:<3}: {:<8}% | {:<3}: {:<8}% | {:<3}: {:<8}%".format(
            clock_count,
            "B", progresses["B"],
            "C", progresses["C"],
            "D", progresses["D"]
        ))

def send_chunk():
    global send_queue, send_connections
    count = 0
    while True:
        v = send_queue.get()

        send_connections[int(v[:2].decode('utf-8'))].sendall(v[2:])
        count += 1
    

def append_chunk_to_queue(conn, type):
    for index, chunk in enumerate(my_chunks[type]):
        seq = index
        if type == "back":
            seq += chunks_length // 2

        seq_chunk = get_seq_chunk(str(conn) + client_index, sequence_size, seq, chunk)
        send_queue.put(seq_chunk)
        


def receive_from_server():
    while True:
        data = conn_server.recv(1024).decode("utf-8")
        if data == "start":
            threads = []

            # 모든 클라이언트들에게 front chunks를 보냄
            for index, client in send_connections.items():
                th = threading.Thread(target=append_chunk_to_queue, args=(index, "front"), daemon=True)
                th.start()
                threads.append(th)

            # 2번 클라이언트에게는 back chunks도 보냄
            th = threading.Thread(target=append_chunk_to_queue, args=(12, "back"), daemon=True)

            th.start()
            threads.append(th)
            sending = threading.Thread(target=send_chunk, daemon=True)
            sending.start()
            threads.append(sending)

            clock_thread = threading.Thread(target=clock, daemon=True)
            clock_thread.start()
            # for th in threads:
            #     th.join()
        elif data == "status":
            conn_server.send(
                "status B:{}:C:{}:D:{}".format(
                    chunks_length - chunks["B"].count(None),
                    chunks_length - chunks["C"].count(None),
                    chunks_length - chunks["D"].count(None),
                ).encode("utf-8")
            )
        elif data == "end":
            break



def receive_from_client(index, conn):
    count = 0
    while True:
        try:
            split_size = 64
            header = conn.recv(split_size).decode("utf-8")

            client_index = str(header[0])
            seq = int(header[1:])

            content = b""

            for _ in range(256000 // split_size):
                content += conn.recv(split_size)
        except Exception as e:
            logger.log(e)
            exit(0)

        chunks[client_index][seq] = content
        count += 1
        progresses[client_index] = round((chunks_length - chunks[client_index].count(None))/chunks_length * 100, 3)

        # 받아온 청크가 B청크라면 3번, 4번 클라이언트에게도 보냄 여기서 B청크는 back chunks
        if client_index == "B" and seq >= chunks_length//2:
            c = header.encode('utf-8') + content
            send_queue.put("13".encode('utf-8') + c)
            send_queue.put("14".encode('utf-8') + c)





def run_client_connection(port):
    global receive_connections, send_connections
    
    conn = socket(AF_INET, SOCK_STREAM)
    conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    conn.setsockopt(SOL_SOCKET, SO_SNDBUF, chunk_size) 
    conn.setsockopt(SOL_SOCKET, SO_RCVBUF, chunk_size)
    conn.bind(("", 8000 + port))
    conn.listen()
    client, addr = conn.accept()

    if port in [21, 31, 41]:
        receive_connections[port] = client
    else:
        send_connections[port] = client
    logger.log("{}의 연결이 성립되었습니다.".format(port))



def connect_server():
    global conn_server
    conn_server = socket(AF_INET, SOCK_STREAM)
    conn_server.connect((SERVER_IP, SERVER_PORT))
    logger.log("서버와 연결되었습니다.")


def end_checker():
    while (chunks['B'].count(None) > 0) or (chunks['C'].count(None) > 0) or (chunks['D'].count(None) > 0):
        time.sleep(1)
        pass


if __name__ == "__main__":
    connect_server()
    run_ports = [12, 21, 13, 31, 14, 41]  # 8012, 8013, 8014
    threads = []

    # 클라이언트들과의 연결을 성립
    for port in run_ports:
        th = threading.Thread(target=run_client_connection, args=(port,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()

    # 서버에게 데이터를 받아오는 받아오는 쓰레드
    receive_server_thread = threading.Thread(target=receive_from_server)
    receive_server_thread.start()

    # 클라이언트에게 데이터를 받아오는 쓰레드
    rcths = []
    for index, conn in receive_connections.items():
        receive_client_thread = threading.Thread(
            target=receive_from_client, args=(index, conn), daemon=True
        )
        receive_client_thread.start()
        rcths.append(receive_client_thread)

    end_checker_thread = threading.Thread(target=end_checker, daemon=True)
    end_checker_thread.start()
    end_checker_thread.join()

    conn_server.send("end 1".encode("utf-8"))
    receive_server_thread.join()

    for i, conn in receive_connections.items():
        conn.close()
    for i, conn in send_connections.items():
        conn.close()

    print(chunks["B"].count(None), chunks["C"].count(None), chunks["D"].count(None))
    merge_files(chunks=chunks["B"], output_file="./result_files/1/resultB.file")
    merge_files(chunks=chunks["C"], output_file="./result_files/1/resultC.file")
    merge_files(chunks=chunks["D"], output_file="./result_files/1/resultD.file")
    logger.log("파일을 모두 병합했습니다.")
