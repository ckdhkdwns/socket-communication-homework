from socket import *
import sys
import configparser
import threading
import time
from util.logger import Logger

config = configparser.ConfigParser()
config.read('config.ini')
SERVER_IP = config["SERVER"]['ip']
t1 = 0


def receive_message(client_socket):
    global t1
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        logger.log(data)
        t1 = time.time() # 문제가 출제된 시간
        if data == "Disconnected.":
            client_socket.close()
            break


def send_message(client_socket):
    global t1
    while True:
        answer = sys.stdin.readline().strip() # 사용자의 결과
        logger.log(answer, p=False)
        t2 = time.time() # 답을 제출한 시간
        time_taken = int(t2 - t1) # 소요시간
        result = "{} {}".format(str(time_taken), str(answer)) # 서버에게 보내는 데이터 형식: "{소요시간} {답}"
        client_socket.send(result.encode('utf-8'))


if __name__ == "__main__":
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((SERVER_IP, 8080))
    logger = Logger("client")

    logger.log('Connected.')

    th1 = threading.Thread(target=receive_message, args=(client_socket,))
    th2 = threading.Thread(target=send_message, args=(client_socket,))
    th2.daemon = True # th2를 서브스레드로 설정, receive_message가 종료되면 자동으로 send_message 스레드도 종료

    th1.start()
    th2.start()