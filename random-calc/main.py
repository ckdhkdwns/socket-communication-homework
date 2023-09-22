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
    server.close()
    sys.exit(">> [{}] The result is {}".format(sec, sum(client_results)))


def question_process(client, addr):
    eq = equation.create()
    client.send(eq.encode('utf-8'))

    print('>> [{}] {:4} {}: {}'.format(sec, "To", addr[0], eq)) # 서버 -> 클라이언트

    result = int(client.recv(1024).decode('utf-8')) # 만약 받은 데이터가 숫자가 아닐 경우 client_thread에서 캐치되서 연결종료
    answer = int(eval(eq))
    client_results.append(result)

    while True:
        print('>> [{}] {:4} {}: {}'.format(sec, "From", addr[0], str(result))) # 클라이언트 -> 서버
        if answer == int(result): # 정답일 경우
            print('>> [{}] Correct.'.format(sec))
            print('>> [{}] The result is added. (Total: {})'.format(sec, sum(client_results)))

            question_process(client, addr) # 재귀를 통해 다른 문제를 출제
            break
        else: # 오답일 경우
            print('>> [{}] Incorrect. The same question will be returned.'.format(sec))
            print('>> [{}] The result is added. (Total: {})'.format(sec, sum(client_results)))

            client.send(eq.encode('utf-8')) # 똑같은 문제를 다시 출제

            result = int(client.recv(1024).decode('utf-8'))
            client_results.append(result)


def client_thread(client, addr):
    try:
        while True:
            print(">> [{}] Client '{}' is connected".format(sec, str(addr[0])))
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
    for client in client_sockets:
        client.send(">> Disconnected.".encode('utf-8'))
        client.close()

    server_socket.close()


if __name__ == "__main__":
    server_socket = socket(AF_INET, SOCK_STREAM)

    shutdown_thread = threading.Thread(target=shutdown_server_after_delay, args=(server_socket, TIME_OUT,))  # 60초 후 종료
    shutdown_thread.start()

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
    finally:
        server_socket.close()