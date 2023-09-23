from socket import *
import threading
import time
import sys
import equation
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

TIME_OUT = int(config["SERVER"]["timeout"])
SERVER_PORT = int(config["SERVER"]["port"])

sec = 0
client_results = []
client_sockets = []


def time_count(server):
    global sec,  client_results
    while sec < TIME_OUT:
        sec += 1
        time.sleep(1)
    print(">> [{}] The total sum is {}".format(sec, sum(client_results)))
    server.close()

    # for c in client_sockets:
    #     c.send(">> Disconnected.".encode('utf-8'))


def question_process(client, addr):
    eq = equation.create()
    while True:
        client.send(eq.encode('utf-8'))
        print('>> [{}] {:4} {}: {}'.format(sec, "To", addr[0], eq))  # 서버 -> 클라이언트
        result = int(client.recv(1024).decode('utf-8'))  # 만약 받은 데이터가 숫자가 아닐 경우 client_thread에서 캐치되서 연결종료

        answer = int(eval(eq))
        client_results.append(result)
        print('>> [{}] {:4} {}: {}'.format(sec, "From", addr[0], str(result))) # 클라이언트 -> 서버

        if answer == int(result): # 정답일 경우
            print('>> [{}] Correct.'.format(sec))
            eq = equation.create()
        else: # 오답일 경우
            print('>> [{}] Incorrect. The same question will be returned.'.format(sec))
        print('>> [{}] The result is added. (Total: {})'.format(sec, sum(client_results)))


def client_thread(client, addr):
    try:
        while True:
            print(">> [{}] Client '{}' is connected".format(sec, str(addr[0])))
            client_sockets.append(client)
            question_process(client, addr) # 문제 내기
    except Exception as e:
        print(">> [{}] Client '{}' is disconnected.".format(sec, addr[0]))
        client.send(">> Disconnected.".encode('utf-8'))
        client.close()


def shutdown_server_after_delay(server_socket, delay):
    time.sleep(delay)
    print(">> [{}] The Total sum is {}.".format(sec, sum(client_results)))
    print(">> [{}] Close Server.".format(sec))

    # 모든 클라이언트 소켓 종료
    for cl in client_sockets:
        print(cl)
        cl.send(">> Disconnected.".encode('utf-8'))
        cl.close()

    server_socket.close()
    sys.exit()


if __name__ == "__main__":
    server_socket = socket(AF_INET, SOCK_STREAM)

    try:
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen()

        print(">> [{}] The Server is running on {}:{}".format(sec, "127.0.0.1", str(SERVER_PORT)))

        # System clock ++
        t = threading.Thread(target=time_count, args=(server_socket,))
        t.start()

        while True:
            client, addr = server_socket.accept()
            connection_thread = threading.Thread(target=client_thread, args=(client, addr))
            connection_thread.start()

    except Exception as e:
        print(">> [{}] Error in main: {}".format(sec, e))
        server_socket.close()
