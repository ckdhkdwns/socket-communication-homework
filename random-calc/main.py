from socket import *
import threading
import time
import equation
import configparser
import sys
import logging
from logger import Logger


config = configparser.ConfigParser()
config.read('config.ini')

TIME_OUT = int(config["SERVER"]["timeout"])
SERVER_PORT = int(config["SERVER"]["port"])

sec = 0
client_results = []
client_sockets = []

log = ''

def time_count(server):
    global sec,  client_results
    while sec < TIME_OUT:
        sec += 1
        time.sleep(1)


    logger.info("[{}] The total sum is {}".format(sec, sum(client_results)))
    logger.info("[{}] Server closed.".format(sec))

    for i in client_sockets:
        i.send("Disconnected.".encode('utf-8'))
    server.close()



def question_process(client, addr):
    eq = equation.create()
    while True:
        client.send(eq.encode('utf-8'))
        logger.info('[{}] {:4} {}: {}'.format(sec, "To", addr[0], eq))  # 서버 -> 클라이언트

        # 클라이언트에게 응답을 받습니다.
        # 클라이언트가 보내는 데이터의 형식은 "{소요시간} {사용자의 답}" 이므로 정제해서 값을 얻습니다.
        # 만약 받은 데이터가 숫자가 아닐 경우 client_thread에서 캐치되서 연결종료됩니다.
        req = client.recv(1024).decode('utf-8').split(" ")
        time_taken =  req[0]
        result = int(req[1])

        answer = int(eval(eq))
        client_results.append(result)

        if answer == int(result): # 정답일 경우
            logger.info('[{}] {:4} {}: {} (Correct / Time taken: {})'.format(sec, "From", addr[0], str(result), time_taken)) # 클라이언트 -> 서버
            eq = equation.create()
        else: # 오답일 경우
            logger.info('[{}] {:4} {}: {} (Incorrect / Time taken: {})'.format(sec, "From", addr[0], str(result), time_taken)) # 클라이언트 -> 서버


def client_thread(client, addr):
    try:
        while True:
            logger.info("[{}] Client '{}' is connected".format(sec, str(addr[0])))
            client_sockets.append(client)
            question_process(client, addr) # 문제 내기
    except Exception as e:
        logger.info("[{}] Client '{}' is disconnected.".format(sec, addr[0]))
        client.send("Disconnected.".encode('utf-8'))
        client.close()



if __name__ == "__main__":
    logger = Logger("server")
    server_socket = socket(AF_INET, SOCK_STREAM)

    try:
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen()

        logger.info("[{}] The Server is running on {}:{}".format(sec, "127.0.0.1", str(SERVER_PORT)))

        # System clock ++
        t = threading.Thread(target=time_count, args=(server_socket,))
        t.start()

        while True:
            client, addr = server_socket.accept()
            connection_thread = threading.Thread(target=client_thread, args=(client, addr))
            connection_thread.start()
    except Exception as e:
        server_socket.close()
