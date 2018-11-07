from multiprocessing import Process
import time

start_time = time.clock()


def method_A():
    while True:
        print('method_A', time.clock()-start_time)
        time.sleep(5)


def method_B():
    while True:
        print('method_B', time.clock()-start_time)


if __name__ == '__main__':
    p1 = Process(target=method_A, args=())
    p2 = Process(target=method_B, args=())
    p1.start()
    p2.start()
