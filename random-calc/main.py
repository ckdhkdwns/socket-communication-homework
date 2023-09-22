from socket import *
import threading
import time
import random
import sys

SYSTEM_SEC = 0
TIME_OUT = 10
SERVER_PORT = 8080

client_results = []
client_sockets = []

def time_count(server_socket):
    global SYSTEM_SEC, client_results
    while SYSTEM_SEC < TIME_OUT:
        SYSTEM_SEC += 1
        time.sleep(1)
    server_socket.close()
    sys.exit(">> [{}] The result is {}".format(SYSTEM_SEC, sum(client_results)))

# 랜덤 사칙연산 만들기
def generate_equation():
    symbols = ['+', '-', '*', '/']

    n = [random.randrange(1, 100) for _ in range(3)] # 정수를 담을 리스트
    s = [symbols[random.randrange(0, 4)] for _ in range(2)] # 기호를 담을 리스트

    equation = "{} {} {} {} {}".format(n[0], s[0], n[1], s[1], n[2])
    return equation

def get_result(client_socket, addr):
    result = None
    try:
        result = int(client_socket.recv(1024))
    except Exception as e:
        client_socket.close()
        print(">> [{}] Client '{}' is disconnected.".format(SYSTEM_SEC, addr[0]))
    finally:
        return result

def question_process(client_socket, addr):
    equation = generate_equation()
    client_socket.send(equation.encode('utf-8'))

    print('>> [{}] {:4} {}: {}'.format(SYSTEM_SEC, "To", addr[0], equation))
    result = get_result(client_socket, addr)

    if result is None:
        return

    client_results.append(result)

    while True:
        print('>> [{}] {:4} {}: {}'.format(SYSTEM_SEC, "From", addr[0], str(result)))
        if int(eval(equation)) == int(result):
            print('>> [{}] Correct.'.format(SYSTEM_SEC))
            print('>> [{}] The result is added. (Total: {})'.format(SYSTEM_SEC, sum(client_results)))

            question_process(client_socket, addr)
            break
        else:
            print('>> [{}] Incorrect. The same question will be returned.'.format(SYSTEM_SEC))
            print('>> [{}] The result is added. (Total: {})'.format(SYSTEM_SEC, sum(client_results)))

            client_socket.send(equation.encode('utf-8'))
            result = get_result(client_socket, addr)
            if result is None:
                return

            client_results.append(result)


def receive_client(server_socket):
    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_sockets.append(client_socket)

            print(">> [{}] Client '{}' is connected".format(SYSTEM_SEC, str(addr[0])))
            question_process(client_socket, addr)

    except Exception as e:
        print(">> [{}] Error: {}".format(SYSTEM_SEC, e))
    finally:
        server_socket.close()


def shutdown_server_after_delay(delay):
    time.sleep(delay)
    print(">> [{}] The Total sum is {}.".format(SYSTEM_SEC, sum(client_results)))
    print(">> [{}] Close Server.".format(SYSTEM_SEC))

    # 모든 클라이언트 소켓 종료
    for client_socket in client_sockets:
        client_socket.close()

    server_socket.close()

if __name__ == "__main__":
    server_socket = socket(AF_INET, SOCK_STREAM)

    shutdown_thread = threading.Thread(target=shutdown_server_after_delay, args=(TIME_OUT,))  # 60초 후 종료
    shutdown_thread.start()

    try:
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', SERVER_PORT))
        server_socket.listen(1)

        print(">> [{}] The Server is running on {}:{}".format(SYSTEM_SEC, "127.0.0.1", str(SERVER_PORT)))

        # System clock ++
        t = threading.Thread(target=time_count, args=(server_socket,))
        t.start()

        while True:
            connection_socket, addr = server_socket.accept()
            connection_thread = threading.Thread(target=receive_client, args=(server_socket,))
            connection_thread.start()

    except Exception as e:
        print(">> [{}] Error: {}".format(SYSTEM_SEC, e))
    finally:
        server_socket.close()







