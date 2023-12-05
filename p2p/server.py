from utils.hash import get_file_hash
from utils.files import split_file, merge_files
from utils.logger import Logger

from socket import *
import configparser
import threading
import time


config = configparser.ConfigParser()
config.read('config.ini')

SERVER_IP = config["SERVER"]["ip"]
SERVER_PORT = int(config["SERVER"]["port"])
STATTUS_INTERVAL = float(config["SERVER"]["status_interval"])


system_clock = 0 # ms
logger = Logger("server")
clients = []

lock = threading.Lock()
closed_count = 0

# temp = split_file('./files/small{}.file'.format("A"))
temp = split_file('./files/A.file')
chunk_length = len(temp)
        
status_count = 0
end_count = 0
status_message = ["" for _ in range(4)]
def client_thread(client_index, client):
    global closed_count, status_count, status_message, end_count

    while True:
        data = client.recv(4096).decode('utf-8').split(" ")
        if data[0] == "status":
            status = data[1].split(":")
            mapping = {
                status[0]: round(int(status[1]) / chunk_length * 100, 3),
                status[2]: round(int(status[3]) / chunk_length * 100, 3),
                status[4]: round(int(status[5]) / chunk_length * 100, 3)
            }
            lock.acquire()
            status_message[client_index] =  "{}번 클라이언트 진행도  {:<3}: {:<8}% | {:<3}: {:<8}% | {:<3}: {:<8}% | {:<3}: {:<8}%".format(
                client_index + 1,
                "A", mapping['A'] if "A" in mapping else "100",
                "B", mapping['B'] if "B" in mapping else "100",
                "C", mapping['C'] if "C" in mapping else "100",
                "D", mapping['D'] if "D" in mapping else "100",
            )
            status_count += 1
            lock.release()
        elif data[0] == "end":
            with lock:
                end_count += 1
            break

        if status_count == 4:
            for s in status_message:
                logger.log(s)
            logger.log("")
            lock.acquire()
            status_message = ["" for _ in range(4)]
            status_count = 0
            lock.release()
        if end_count == 4:
            for client in clients:
                client.send("end".encode('utf-8'))
                
                break
        
            
        


def process():
    for client in clients:
        client.send("start".encode('utf-8'))
    
    threads = []
    for index, client in enumerate(clients):
        th = threading.Thread(target=client_thread, args=(index, client))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()


def clock():
    global system_clock
    while True:
        system_clock += 1 # sec/10
        time.sleep(0.1)

        if system_clock % int(STATTUS_INTERVAL * 10) == 0:
            for client in clients:
                client.send('status'.encode('utf-8'))


def accept_clients(server):
    while True:
        client, addr = server.accept()
        clients.append(client)
        clients_count = len(clients)
        logger.log("클라이언트 {}가 연결되었습니다.".format(clients_count))

        if clients_count == 4:
            logger.log("클라이언트가 모두 연결되었습니다. 전송을 시작합니다.")

            clock_thread = threading.Thread(target=clock, daemon=True)
            process_thread = threading.Thread(target=process)

            clock_thread.start()
            process_thread.start()
            process_thread.join()
            logger.log("파일 전체 전송 완료! 소요시간 : {}sec".format(system_clock/10))
            server.close()
            return


def run_server():
    server = socket(AF_INET, SOCK_STREAM)
    try:
        server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server.bind(('', 8080))
        server.listen()
        logger.log("서버가 {}:{}에서 실행중입니다.".format(SERVER_IP, str(SERVER_PORT)))
        accept_clients(server)
        

    except Exception as e:
        logger.log(">> {}".format(e))
        server.close()

if __name__ == "__main__":
    run_server()
