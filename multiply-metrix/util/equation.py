import random


def create():
    symbols = ['+', '-', '*', '/']

    n = [random.randrange(1, 100) for _ in range(3)] # 정수를 담을 리스트
    s = [symbols[random.randrange(0, 4)] for _ in range(2)] # 기호를 담을 리스트

    equation = "{} {} {} {} {}".format(n[0], s[0], n[1], s[1], n[2])
    return equation